"""TODO-233 の実測。使い方: verifier-check.py <datadir> <port>"""
import datetime, json, subprocess, sys, time, pathlib, urllib.request
from playwright.sync_api import sync_playwright

dd, port = pathlib.Path(sys.argv[1]), int(sys.argv[2])
base = f"http://127.0.0.1:{port}/"
today = datetime.date.today()

def write(date, n):
    p = dd / "data" / f"{date:%Y}" / f"{date:%m}"
    p.mkdir(parents=True, exist_ok=True)
    rows = [json.dumps({"sde_id": f"id-{i}", "date": date.isoformat(),
        "time_start": f"{i%24:02}:00", "time_end": "", "type": "",
        "title": f"予定{i}", "place": "", "detail": ""}, ensure_ascii=False)
        for i in range(n)]
    (p / f"{date:%d}.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")

write(today, 40)
srv = subprocess.Popen(["uv", "run", "ytsched", "webapp", "--datadir", str(dd), "--port", str(port)])
try:
    for _ in range(60):
        try:
            urllib.request.urlopen(base, timeout=1); break
        except Exception:
            time.sleep(0.5)
    flash = lambda pg: pg.eval_on_selector_all(".my-flash", "els=>els.map(e=>e.id||e.parentElement.id+' > '+e.className)")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/chromium")
        pg = b.new_page(viewport={"width": 412, "height": 300})
        # a
        pg.goto(f"{base}?date={today}", wait_until="load")
        pg.wait_for_selector("#main", state="visible")
        print("a: my-flash =", pg.locator(".my-flash").count(),
              "date-col =", pg.locator(f"#date-{today} .my-date-col.my-flash").count(), "url =", pg.url)
        # b
        pg2 = b.new_page(viewport={"width": 412, "height": 300})
        pg2.goto(base, wait_until="load")
        pg2.wait_for_selector("#main", state="visible")
        print("b: my-flash =", pg2.locator(".my-flash").count(), "url =", pg2.url)
        # c: a のページで画面内の移動 (pushDateInUrl) をしてから戻る (popstate)
        pg.wait_for_timeout(6000)
        print("c: before move my-flash =", pg.locator(".my-flash").count())
        pg.evaluate("(d) => window.ytsched.pushDateInUrl(d)", str(today + datetime.timedelta(days=14)))
        pg.wait_for_timeout(500)
        print("c: moved url =", pg.url)
        pg.wait_for_timeout(6000)
        pg.go_back()
        pg.wait_for_timeout(1500)
        print("c: after go_back(popstate) url =", pg.url, "my-flash =", pg.locator(".my-flash").count(), flash(pg))
        # c2: ミニカレンダーの日をクリックして go_back
        pg.goto(f"{base}?date={today}", wait_until="load")
        pg.wait_for_selector("#main", state="visible")
        pg.wait_for_timeout(6000)
        pg.locator(".my-week-cur .my-mini-cal [data-date]").nth(3).click()
        pg.wait_for_load_state("load"); pg.wait_for_timeout(6000)
        print("c2: moved url =", pg.url)
        pg.go_back(); pg.wait_for_timeout(1500)
        print("c2: after go_back(mini-cal 日クリック、画面内移動) url =", pg.url, "my-flash =", pg.locator(".my-flash").count())
        b.close()
finally:
    srv.terminate(); srv.wait(10)
