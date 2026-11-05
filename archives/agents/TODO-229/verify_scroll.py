"""TODO-229 verifier: scroll-behavior と scrollBy / 読み直し後の位置合わせの実測。
使い方: uv run python archives/agents/TODO-229/verify_scroll.py"""
import datetime as dt, json, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

PORT = 10229
tmp = Path(tempfile.mkdtemp(prefix="ytsched-v229-"))
today = dt.date.today()
d = tmp / f"{today:%Y}" / f"{today:%m}"
d.mkdir(parents=True)
with (d / f"{today:%d}.jsonl").open("w", encoding="utf-8") as f:
    for i in range(40):
        f.write(json.dumps({"sde_id": f"id-{i}", "date": today.isoformat(),
            "time_start": "09:00", "time_end": "10:00", "type": "会議",
            "title": f"予定{i}", "place": "", "detail": ""}, ensure_ascii=False) + "\n")
srv = subprocess.Popen([sys.executable, "-m", "ytsched", "webapp", "--port",
    str(PORT), "--datadir", str(tmp)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
BASE = f"http://127.0.0.1:{PORT}/ytsched/"
for _ in range(60):
    try:
        urllib.request.urlopen(BASE, timeout=1); break
    except Exception:
        time.sleep(0.3)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/chromium")
        p = b.new_context(viewport={"width": 412, "height": 800}).new_page()
        # 読み直し直後の scrollY を、スクリプト実行前から記録する
        p.add_init_script("""
          window.__ys = [];
          const rec = () => window.__ys.push(Math.round(window.scrollY));
          const loop = () => { rec(); requestAnimationFrame(loop); };
          requestAnimationFrame(loop);
        """)
        # 1,3: sde_align=top で開く（onloadHdr の scrollToDate "instant"）
        p.goto(f"{BASE}?date={today}&sde_align=top", wait_until="load")
        p.wait_for_selector("#main", state="visible")
        p.wait_for_timeout(1500)
        ys = p.evaluate("window.__ys")
        print("computed scrollBehavior:", p.evaluate("getComputedStyle(document.documentElement).scrollBehavior"))
        print("body scrollBehavior:", p.evaluate("getComputedStyle(document.body).scrollBehavior"))
        print("onload scrollY final:", p.evaluate("scrollY"), "distinct(rAF):", sorted(set(ys)))
        # 3: 位置合わせ後の途中値が無いか（先頭0 → 最終値のみか）
        # 2: flash 付きで開き、scrollBy の同期後 scrollY を読む
        # scrollBy を包んで直後の scrollY を記録
        p2 = b.new_context(viewport={"width": 412, "height": 800}).new_page()
        p2.add_init_script("""
          window.__sb = [];
          const orig = window.scrollBy.bind(window);
          window.scrollBy = (...a) => { const b = window.scrollY; orig(...a);
            window.__sb.push({args: a, before: Math.round(b), after: Math.round(window.scrollY)}); };
          window.__ys = [];
          const loop = () => { window.__ys.push(Math.round(window.scrollY)); requestAnimationFrame(loop); };
          requestAnimationFrame(loop);
        """)
        p2.goto(f"{BASE}?date={today}&sde_align=top&flash_date={today}&flash_sde_id=id-39", wait_until="load")
        p2.wait_for_selector("#main", state="visible")
        p2.wait_for_timeout(1500)
        print("scrollBy calls:", json.dumps(p2.evaluate("window.__sb")))
        print("flash scrollY final:", p2.evaluate("scrollY"), "distinct(rAF):", sorted(set(p2.evaluate("window.__ys"))))
        b.close()
finally:
    srv.terminate(); srv.wait(timeout=10)
