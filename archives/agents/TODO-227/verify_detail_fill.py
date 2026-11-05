"""TODO-227 verifier: 編集画面の詳細欄が、入力中に上下のバーの間へ広がるかの実測。
使い方: uv run python archives/agents/TODO-227/verify_detail_fill.py
サーバは一時ディレクトリで自分で起動して止める。viewport の高さ 780→430 でキーボードを代用。"""
import datetime as dt, json, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

PORT = 10227
OUT = Path(__file__).parent
tmp = Path(tempfile.mkdtemp(prefix="ytsched-v227-"))
today = dt.date.today()
d = tmp / f"{today:%Y}" / f"{today:%m}"
d.mkdir(parents=True)
detail = "\n".join(f"詳細 {i+1} 行目 あいうえお" for i in range(40))
(d / f"{today:%d}.jsonl").write_text(json.dumps({
    "sde_id": "v227", "date": today.isoformat(), "time_start": "09:00",
    "time_end": "10:00", "type": "会議", "title": "長い詳細", "place": "",
    "detail": detail}, ensure_ascii=False) + "\n", encoding="utf-8")
log = open(tmp / "srv.log", "w")
srv = subprocess.Popen([sys.executable, "-m", "ytsched", "webapp", "--port",
    str(PORT), "--datadir", str(tmp / ""), ], stdout=log, stderr=subprocess.STDOUT)
BASE = f"http://127.0.0.1:{PORT}/ytsched/"
for _ in range(60):
    try:
        urllib.request.urlopen(BASE, timeout=1); break
    except Exception:
        time.sleep(0.3)

BOX = """() => { const r = document.getElementById('detail').getBoundingClientRect();
 return {top: r.top, bottom: r.bottom, h: r.height, scrollY: window.scrollY,
  barBottom: document.querySelector('.my-edit-bar-top').getBoundingClientRect().bottom,
  barTop: document.querySelector('.my-edit-bar-bottom').getBoundingClientRect().top,
  active: document.activeElement.id}; }"""

def box(p):
    p.wait_for_timeout(700)
    b = p.evaluate(BOX)
    return {k: (round(v, 1) if isinstance(v, float) else v) for k, v in b.items()}

def vp(p, h): p.set_viewport_size({"width": 412, "height": h})

def load(b):
    p = b.new_context(viewport={"width": 412, "height": 780}).new_page()
    p.goto(f"{BASE}edit/?date={today.isoformat()}&sde_id=v227", wait_until="load")
    p.wait_for_selector("#input_form", state="visible")
    p.wait_for_timeout(500)
    return p

def fills(b): return abs(b["top"] - b["barBottom"]) <= 1 and abs(b["bottom"] - b["barTop"]) <= 1

res = {}
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/usr/bin/chromium")
    # 基準: 780 / 430 でフォーカスなし
    p = load(br); res["0_load780"] = box(p)
    vp(p, 430); res["0_unfocused430_after_resize"] = box(p)
    p.close()
    # 1,2,3
    p = load(br); base = box(p)
    p.locator("#detail").click(); vp(p, 430); res["1_click_then_430"] = b1 = box(p)
    res["1_fills"] = fills(b1)
    p.screenshot(path=str(OUT / "item6_detail_filled_430.png"))
    vp(p, 780); res["2_back780_focus_kept"] = box(p)
    vp(p, 430); res["3a_430_again"] = box(p)
    p.locator("#title").focus(); res["3b_title_focus"] = box(p)
    p.close()
    # 4
    p = load(br)
    p.locator("#title").click(); vp(p, 430); res["4a_title_click_430"] = box(p)
    p.locator("#detail").click(); res["4b_detail_click"] = b4 = box(p)
    res["4_fills"] = fills(b4)
    res["4_same_as_1"] = (abs(b4["top"]-b1["top"]) <= 1 and abs(b4["h"]-b1["h"]) <= 1)
    p.close()
    # 5
    p = load(br)
    vp(p, 430); res["5a_430_nofocus"] = box(p)
    p.locator("#detail").click(); res["5b_detail_click"] = b5 = box(p)
    res["5_not_filled"] = not fills(b5)
    p.close(); br.close()
res["base_load"] = base
print(json.dumps(res, ensure_ascii=False, indent=1))
(OUT / "verify_detail_fill.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
srv.terminate(); srv.wait(10)
print("server log tail:", (tmp / "srv.log").read_text()[-600:])
