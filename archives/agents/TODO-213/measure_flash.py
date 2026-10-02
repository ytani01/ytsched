"""点滅の黄色が見えるかを測る (TODO-213)。

使い方: uv run python archives/agents/TODO-213/measure_flash.py
一時ディレクトリで webapp を起動し、flash_* 付きで開き、アニメーションを
0ms (黄色の相) で止めて、日付の欄と予定の行の黄色の画素の割合を出す。
"""
import datetime, io, json, subprocess, sys, tempfile, time, socket
import urllib.request
from pathlib import Path
import base64
from playwright.sync_api import sync_playwright

tmp = Path(tempfile.mkdtemp())
today = datetime.date.today()
cases = {"normal": ("会議", today), "holiday": ("休日", today + datetime.timedelta(1)),
         "todo": ("□", today + datetime.timedelta(2))}
for kind, (typ, d) in cases.items():
    p = tmp / "data" / d.strftime("%Y") / d.strftime("%m")
    p.mkdir(parents=True, exist_ok=True)
    (p / (d.strftime("%d") + ".jsonl")).write_text(json.dumps(
        {"sde_id": f"id-{kind}", "date": d.isoformat(), "time_start": "09:00",
         "time_end": "10:00", "type": typ, "title": kind, "place": "", "detail": ""},
        ensure_ascii=False) + "\n", encoding="utf-8")
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
proc = subprocess.Popen([sys.executable, "-m", "ytsched", "webapp", "--port", str(port),
                         "--datadir", str(tmp / "data")], stdout=-3, stderr=-3)
base = f"http://127.0.0.1:{port}/ytsched/"
for _ in range(100):
    try:
        urllib.request.urlopen(base, timeout=1); break
    except Exception:
        time.sleep(0.2)

JS = """async (b64) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + b64;
  await img.decode();
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const x = c.getContext('2d'); x.drawImage(img, 0, 0);
  const d = x.getImageData(0, 0, c.width, c.height).data; let n = 0;
  for (let i = 0; i < d.length; i += 4) if (d[i]==255 && d[i+1]==235 && d[i+2]==59) n++;
  return n / (d.length / 4);
}"""

def yellow(png):
    return PG.evaluate(JS, base64.b64encode(png).decode())

PG = None
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/chromium")
        PG = pg = b.new_page(viewport={"width": 412, "height": 1600})
        for kind, (_, d) in cases.items():
            pg.goto(f"{base}?date={d}&flash_date={d}&flash_sde_id=id-{kind}")
            pg.wait_for_selector("#main", state="visible")
            pg.evaluate("document.getAnimations().forEach(a=>{a.pause();a.currentTime=0})")
            for name, sel in (("date-col", f"#date-{d} .my-date-col"),
                              ("sde-row", f'.my-sde:has([data-sde-id="id-{kind}"])')):
                el = pg.locator(sel).first
                print(kind, name, f"{yellow(el.screenshot()):.1%}")
        b.close()
finally:
    proc.terminate()
