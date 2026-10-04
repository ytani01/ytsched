"""TODO-217 verifier(2回目: 1秒・ゲージ追従・取り消し): ホームで今日の週へ流す動きの実測。
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
 window.addEventListener('keydown', (e) => { if (e.key==='Home' && window.__t0===null) window.__t0 = performance.now(); }, true);
 window.__iv = setInterval(() => {
  if (window.__t0===null) return;
  const w = document.querySelector('.my-week-wrap');
  const m = new DOMMatrix(getComputedStyle(w).transform);
  const disp = {}; document.querySelectorAll('.my-week-panel').forEach(p => disp[p.dataset.offset] = getComputedStyle(p).display);
  const g = document.querySelector('.my-gauge-r');
  window.__log.push({t: Math.round(performance.now()-window.__t0), tx: Math.round(m.m41*10)/10, disp,
    gl: Math.round(g.getBoundingClientRect().left*10)/10, lab: g.querySelector('.my-gauge-r-label').textContent}); window.name = JSON.stringify(window.__log.slice(-60));
 }, 50); }"""
STATE = """() => { const w = document.querySelector('.my-week-wrap');
 return {off: ytsched.ytState.activeWeekOffset, style: w.getAttribute('style'),
  cls: w.className, url: location.search,
  nt: document.querySelectorAll('.my-gauge-r-no-transition').length,
  near: [...document.querySelectorAll('.my-week-near')].map(p=>p.dataset.offset),
  cur: [...document.querySelectorAll('.my-week-cur')].map(p=>p.dataset.offset)}; }"""
RESET = "() => { window.__t0 = null; window.__log = []; }"

def go_weeks(page, n):
    key = "ArrowRight" if n > 0 else "ArrowLeft"
    for _ in range(abs(n)):
        page.keyboard.press(key); page.wait_for_timeout(450)

def fresh(page, view=""):
    page.goto(BASE + view); page.wait_for_selector(".my-week-panel", state="attached")
    page.wait_for_timeout(800)

def home_click(page):
    b = page.locator("#home_button").bounding_box()
    page.mouse.move(b["x"]+b["width"]/2, b["y"]+b["height"]/2); page.mouse.down(); page.mouse.up()

def gauge_click(page, frac):
    gb = page.locator("#footer_gauge_bar").first.bounding_box()
    page.mouse.move(gb["x"]+gb["width"]*frac, gb["y"]+gb["height"]/2); page.mouse.down(); page.mouse.up()

def mono(vals, inc):
    d = [b-a for a, b in zip(vals, vals[1:])]
    return all(x >= -0.5 for x in d) if inc else all(x <= 0.5 for x in d)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(("console."+m.type, m.text)) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(("pageerror", str(e))))

    # 1
    for name, n, how in (("1_future", 4, "button"), ("2_past", -4, "key")):
        fresh(page); page.evaluate(SAMPLER); go_weeks(page, n)
        res[name+"_before"] = page.evaluate(STATE)
        page.evaluate(RESET)
        if how == "button": home_click(page)
        else: page.keyboard.press("Home")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(os.path.dirname(__file__), f"mid2_{name}.png"))
        page.wait_for_timeout(1000)
        log = page.evaluate("() => window.__log")
        res[name+"_log"] = [(e["t"], e["tx"], e["gl"], e["lab"], sorted(k for k,v in e["disp"].items() if v!="none")) for e in log if e["t"]<=1300 and e["t"] % 100 < 50 or e["t"]<=60]
        mv = [e for e in log if e["t"] <= 1000]
        res[name+"_gauge_monotone_toward_today"] = mono([abs(e["gl"]-log[-1]["gl"]) for e in mv], False)
        res[name+"_tx_monotone"] = mono([abs(e["tx"]) for e in mv], True)
        res[name+"_after"] = page.evaluate(STATE)

    # 2: 途中 300ms で戻る
    fresh(page); go_weeks(page, 4)
    home_click(page); page.wait_for_timeout(300)
    page.evaluate("() => history.back()"); page.wait_for_timeout(1200)
    res["2_back"] = page.evaluate(STATE)
    fresh(page); go_weeks(page, 4)
    home_click(page); page.wait_for_timeout(300)
    gauge_click(page, 0.3); page.wait_for_timeout(1200)
    res["2_gauge"] = page.evaluate(STATE)
    # 2c: ゲージで今日に近い週(+1w 相当)を狙う: 針の右 4w 位置付近
    # (DOM にある週へ直に移る経路 = setActiveWeek を通る)
    fresh(page); go_weeks(page, 4)
    home_click(page); page.wait_for_timeout(300)
    gb = page.locator("#footer_gauge_bar").first.bounding_box()
    res["2c_gauge_box"] = gb
    for f in (0.5,):
        pass
    # 針ラベルが +1w の位置 (ラベルから探す)
    pos = page.evaluate("""() => { const l=[...document.querySelectorAll('#footer_gauge_bar .my-gauge-label')].find(e=>e.textContent.trim()==='+1w'); if(!l) return null; const r=l.getBoundingClientRect(); return r.left+r.width/2; }""")
    res["2c_pos"] = pos
    if pos:
        page.mouse.move(pos, gb["y"]+gb["height"]/2); page.mouse.down(); page.mouse.up()
    page.wait_for_timeout(1200)
    res["2c_after"] = page.evaluate(STATE)

    # 3: 途中 300ms でドラッグ
    fresh(page); page.evaluate(SAMPLER); go_weeks(page, 4)
    page.evaluate(RESET)
    if not os.environ.get("NOSLIDE"): home_click(page)
    page.wait_for_timeout(300)
    DY=int(os.environ.get("DRAGY","400")); NOSLIDE=os.environ.get("NOSLIDE")
    page.mouse.move(300, DY); page.mouse.down()
    DX = int(os.environ.get("DRAGDX", "160"))
    for i in range(1, DX // 20 + 1):
        page.mouse.move(300 - i*20, DY); page.wait_for_timeout(30)
        if i == 3 and DX >= 60:
            try: res["3_state_during_drag"] = page.evaluate(STATE)
            except Exception as e: res["3_state_during_drag"] = "ERR"
    page.mouse.up()
    page.wait_for_timeout(1300)
    log = page.evaluate("() => window.__log") or json.loads(page.evaluate("() => window.name") or "[]")
    res["3_events_after_url"] = page.url
    res["3_log_lost(ページが読み直された)"] = not log
    txs = [e["tx"] for e in log if e["t"] <= 1000] or [0, 0]
    res["3_tx"] = txs
    res["3_max_step"] = max(abs(b-a) for a, b in zip(txs, txs[1:]))
    res["3_url"] = page.url
    try:
        page.wait_for_timeout(1000)
        res["3_after"] = page.evaluate(STATE)
    except Exception as e:
        res["3_after"] = "ERR " + str(e)[:300]

    # 4: ダブルタップ + サーバ応答 1.5 秒遅れ
    fresh(page); go_weeks(page, 4)
    def slow(route):
        if route.request.resource_type == "document":
            page.wait_for_timeout(1500)
        route.continue_()
    page.route("**/*", slow)
    page.evaluate("() => { window.__reloaded = true; const st = %s; window.addEventListener('pagehide', () => { const o = st(); o.t = Math.round(performance.now() - window.__t2); sessionStorage.setItem('v4state', JSON.stringify(o)); }); }" % STATE)
    home_click(page); page.wait_for_timeout(200); page.evaluate("() => { window.__t2 = performance.now(); }"); home_click(page)
    page.wait_for_timeout(150)
    try: res["4_state_after_2nd_tap"] = page.evaluate(STATE)
    except Exception as e: res["4_state_after_2nd_tap"] = "ERR " + str(e)[:200]
    page.wait_for_timeout(450)
    res["4_mid_url"] = page.url
    page.wait_for_timeout(3500)
    res["4_flag_survives(true=未読直し)"] = page.evaluate("() => window.__reloaded === true")
    res["4_after"] = page.evaluate(STATE)
    res["4_state_at_pagehide"] = page.evaluate("() => sessionStorage.getItem('v4state')")
    page.unroute("**/*")

    # 5: 3(今日の週)・7・6
    fresh(page); page.evaluate(SAMPLER); page.evaluate(RESET)
    home_click(page); page.wait_for_timeout(1300)
    res["5_3_txs"] = sorted({e["tx"] for e in page.evaluate("() => window.__log")})
    page.keyboard.press("ArrowRight"); page.wait_for_timeout(60)
    res["5_7"] = page.evaluate("() => { const w=document.querySelector('.my-week-wrap'); const s=getComputedStyle(w); return [w.className, s.transitionDuration]; }")
    page.wait_for_timeout(500)
    fresh(page, "?view=month"); n0 = len(errors)
    home_click(page); page.wait_for_timeout(900)
    res["5_6_after"] = page.url; res["5_6_errs"] = errors[n0:]
    br.close()

srv.terminate(); srv.wait(10)
res["errors"] = errors
_l = open(tmp + "/srv.log").read()
res["server_log_traceback"] = "Traceback" in _l
if "Traceback" in _l:
    i = _l.index("Traceback"); res["server_log_tb_text"] = _l[max(0,i-300):i+900]
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
