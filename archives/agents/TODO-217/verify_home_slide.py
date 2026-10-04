"""TODO-217 verifier: ホームで今日の週へ流す動きの実測。
使い方: uv run python archives/agents/TODO-217/verify_home_slide.py
サーバ(port 10099)は自分で一時ディレクトリで起動して止める。"""
import datetime as dt, json, os, subprocess, sys, tempfile, time, re
from playwright.sync_api import sync_playwright

PORT = 10099
BASE = f"http://127.0.0.1:{PORT}/"
tmp = tempfile.mkdtemp(prefix="ytsched-v217-")
today = dt.date.today()
for i in range(-60, 61, 1):
    d = today + dt.timedelta(days=i)
    p = os.path.join(tmp, f"{d.year:04d}", f"{d.month:02d}")
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, f"{d.day:02d}.jsonl"), "a") as f:
        f.write(json.dumps({"sde_id": f"id{i}-1", "date": d.isoformat(),
            "time_start": "10:00", "time_end": "11:00", "type": "予定",
            "title": f"予定{d.isoformat()}", "place": "", "detail": ""},
            ensure_ascii=False) + "\n")
srv = subprocess.Popen(["uv", "run", "ytsched", "webapp", "--datadir", tmp,
    "--port", str(PORT)], stdout=open(tmp + "/srv.log", "w"), stderr=subprocess.STDOUT)
for _ in range(50):
    try:
        import urllib.request; urllib.request.urlopen(BASE, timeout=1); break
    except Exception: time.sleep(0.3)

errors = []
res = {}
SAMPLER = """() => { window.__log = []; window.__t0 = null;
 const hb = document.getElementById('home_button');
 hb.addEventListener('mousedown', () => { window.__t0 = performance.now(); }, true);
 window.addEventListener('keydown', () => { if (window.__t0===null) window.__t0 = performance.now(); }, true);
 window.__iv = setInterval(() => {
  if (window.__t0===null) return;
  const w = document.querySelector('.my-week-wrap');
  const m = new DOMMatrix(getComputedStyle(w).transform);
  const disp = {}; document.querySelectorAll('.my-week-panel').forEach(p => disp[p.dataset.offset] = getComputedStyle(p).display);
  window.__log.push({t: Math.round(performance.now()-window.__t0), tx: Math.round(m.m41*10)/10, disp});
 }, 50); }"""
STATE = """() => { const w = document.querySelector('.my-week-wrap');
 return {off: ytsched.ytState.activeWeekOffset, style: w.getAttribute('style'),
  cls: w.className, url: location.search + location.pathname,
  near: [...document.querySelectorAll('.my-week-near')].map(p=>p.dataset.offset),
  cur: [...document.querySelectorAll('.my-week-cur')].map(p=>p.dataset.offset)}; }"""

def mon(d): return d - dt.timedelta(days=d.weekday())

def go_weeks(page, n):
    key = "ArrowRight" if n > 0 else "ArrowLeft"
    for _ in range(abs(n)):
        page.keyboard.press(key); page.wait_for_timeout(450)

def fresh(page, view=""):
    page.goto(BASE + view); page.wait_for_selector(".my-week-wrap, .my-week-panel", state="attached")
    page.wait_for_timeout(800)

def home_click(page):
    b = page.locator("#home_button").bounding_box()
    page.mouse.move(b["x"]+b["width"]/2, b["y"]+b["height"]/2); page.mouse.down(); page.mouse.up()

def report_log(name, log, n):
    txs = [(e["t"], e["tx"]) for e in log if e["t"] <= 550]
    res[name+"_tx"] = txs
    res[name+"_mid_display"] = [(e["t"], {k:v for k,v in e["disp"].items() if k in ("0","1","2","3","4","-1","-2","-3","-4")}) for e in log[::3]][:5]

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}, has_touch=False)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(("console."+m.type, m.text)) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(("pageerror", str(e))))

    for name, n, how in (("1_future", 4, "button"), ("2_past", -4, "key")):
        fresh(page); page.evaluate(SAMPLER)
        go_weeks(page, n)
        res[name+"_before"] = page.evaluate(STATE)
        page.evaluate("() => { window.__t0 = null; window.__log = []; }")
        if how == "button": home_click(page)
        else: page.keyboard.press("Home")
        page.wait_for_timeout(180)
        page.screenshot(path=os.path.join(os.path.dirname(__file__), f"mid_{name}.png"))
        page.wait_for_timeout(700)
        log = page.evaluate("() => window.__log")
        res[name+"_log"] = [(e["t"], e["tx"], sorted(k for k,v in e["disp"].items() if v!="none")) for e in log if e["t"]<=550]
        res[name+"_after"] = page.evaluate(STATE)

    # 3: 今日の週にいる
    page.evaluate("() => { window.__t0 = null; window.__log = []; }")
    home_click(page); page.wait_for_timeout(600)
    res["3_log_txs"] = sorted({e["tx"] for e in page.evaluate("() => window.__log")})
    res["3_after"] = page.evaluate(STATE)

    # 4: 途中で history.back()
    fresh(page); page.evaluate(SAMPLER); go_weeks(page, 4)
    home_click(page); page.wait_for_timeout(100)
    page.evaluate("() => history.back()"); page.wait_for_timeout(450)
    res["4_back"] = page.evaluate(STATE)
    # 4b: ゲージクリック(途中で)
    fresh(page); go_weeks(page, 4)
    home_click(page); page.wait_for_timeout(100)
    gb = page.locator("#footer_gauge_bar").first.bounding_box()
    page.mouse.move(gb["x"]+gb["width"]*0.3, gb["y"]+gb["height"]/2); page.mouse.down(); page.mouse.up()
    page.wait_for_timeout(450)
    res["4_gauge"] = page.evaluate(STATE)

    # 5: ダブルタップ 200ms
    fresh(page); go_weeks(page, 4)
    page.evaluate("() => { window.__reloaded = true; }")
    home_click(page); page.wait_for_timeout(200); home_click(page)
    page.wait_for_timeout(1500)
    res["5_flag_after"] = page.evaluate("() => window.__reloaded === true")  # false => 読み直された
    res["5_after"] = page.evaluate(STATE)
    # 7: transition
    res["7_transition_sliding"] = None
    fresh(page); page.evaluate(SAMPLER)
    page.keyboard.press("ArrowRight"); page.wait_for_timeout(60)
    res["7"] = page.evaluate("() => { const w=document.querySelector('.my-week-wrap'); const s=getComputedStyle(w); return [w.className, s.transitionDuration, s.transitionProperty, s.transform]; }")
    page.wait_for_timeout(500)
    # 6: 月間表示
    fresh(page, "?view=month")
    res["6_before"] = page.url
    n0 = len(errors)
    home_click(page); page.wait_for_timeout(900)
    res["6_after"] = page.url
    res["6_errs"] = errors[n0:]
    br.close()

srv.terminate(); srv.wait(10)
res["errors"] = errors
res["server_log_traceback"] = "Traceback" in open(tmp + "/srv.log").read()
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
