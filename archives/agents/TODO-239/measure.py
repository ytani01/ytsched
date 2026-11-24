"""TODO-239: 同じ名前で付け直した添付画像を、ブラウザが古いまま出すかを測る。

使い方: uv run python archives/agents/TODO-239/measure.py
"""

import datetime, os, re, socket, struct, subprocess, sys, tempfile
import time, urllib.request, zlib
from pathlib import Path

from playwright.sync_api import sync_playwright


def png(w, h):
    raw = b"".join(b"\0" + b"\xff\0\0" * w for _ in range(h))
    def ch(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d))
    return (b"\x89PNG\r\n\x1a\n"
            + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b""))


tmp = Path(tempfile.mkdtemp())
data = tmp / "data"
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
logf = open(tmp / "server.log", "w")
proc = subprocess.Popen(
    [sys.executable, "-m", "ytsched", "webapp", "--port", str(port),
     "--datadir", str(data)], stdout=logf, stderr=logf)
base = f"http://127.0.0.1:{port}/ytsched/"
for _ in range(100):
    try:
        urllib.request.urlopen(base, timeout=1); break
    except Exception:
        time.sleep(0.2)
today = datetime.date.today().isoformat()
(tmp / "a.png").write_bytes(png(10, 10))
(tmp / "b").mkdir()
(tmp / "b" / "a.png").write_bytes(png(40, 30))
print("tmp", tmp, "base", base)


def logsize():
    logf.flush(); return (tmp / "server.log").stat().st_size


with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/usr/bin/chromium")
    ctx = br.new_context(viewport={"width": 1000, "height": 900})
    pg = ctx.new_page()
    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")
    cache = []
    ids = {}
    cdp.on("Network.requestWillBeSent", lambda e: ids.__setitem__(
        e["requestId"], e["request"]["url"]))
    cdp.on("Network.responseReceived", lambda e: cache.append(
        ("response", e["response"]["status"], "fromDiskCache=%s" %
         e["response"].get("fromDiskCache"))) if "/attach/" in
        e["response"]["url"] else None)
    cdp.on("Network.requestServedFromCache", lambda e: cache.append(
        "servedFromCache") if "/attach/" in ids.get(e["requestId"], "")
        else None)
    reqs = []
    pg.on("response", lambda r: reqs.append(r) if "/attach/" in r.url else None)

    # 予定を作り、a.png (10x10) を添付
    pg.goto(f"{base}edit/?date={today}", wait_until="load")
    pg.wait_for_selector("#input_form", state="visible")
    pg.fill("#title", "t239")
    pg.set_input_files("#attach", str(tmp / "a.png"))
    pg.locator('[data-cmd="update"]').first.click()
    pg.wait_for_load_state("load"); time.sleep(1)
    print("after add url", pg.url)
    att = list((data / "attachments").rglob("*"))
    print("files", [str(p.relative_to(data)) for p in att])
    f = [p for p in att if p.is_file()][0]
    old = time.time() - 30 * 86400
    os.utime(f, (old, old))

    def open_detail(how):
        reqs.clear(); cache.clear()
        if how == "goto":
            pg.goto(f"{base}?date={today}", wait_until="load")
        else:  # 予定画面（別URL）から戻る操作
            pg.goto(f"{base}?date={today}", wait_until="load")
        pg.wait_for_selector("#main", state="visible")
        pg.locator(".my-sde-detail-sw label").first.click()
        img = pg.locator(".my-sde-attach img").first
        img.wait_for(state="visible")
        pg.wait_for_function(
            "document.querySelector('.my-sde-attach img').complete")
        d = pg.evaluate(
            "[...document.querySelectorAll('.my-sde-attach img')]"
            ".map(i=>[i.naturalWidth,i.naturalHeight])")
        info = [list(cache)] + [(r.status, r.from_service_worker,
                 {k: v for k, v in r.headers.items() if k in
                  ("last-modified", "etag", "cache-control")}) for r in reqs]
        return d, info

    def server_hits(before):
        logf.flush()
        t = (tmp / "server.log").read_text()[before:]
        return len(re.findall(r"/attach/", t))

    print("== 付ける前 (10x10) 1回目 ==")
    for i in range(3):
        b = logsize()
        print(i, open_detail("goto"))

    # 外して、40x30 を同じ名前で付け直す (画面操作)
    pg.goto(f"{base}edit/?date={today}&sde_id=" + f.parent.name + "-1",
            wait_until="load")
    pg.wait_for_selector("#input_form", state="visible")
    pg.locator('input[name="attach_del"]').check()
    pg.set_input_files("#attach", str(tmp / "b" / "a.png"))
    pg.locator('[data-cmd="update"]').first.click()
    pg.wait_for_load_state("load"); time.sleep(1)
    new_id = pg.input_value("#sde_id")
    print("sde_id after reattach", new_id)
    att = [p for p in (data / "attachments").rglob("*") if p.is_file()]
    print("after reattach files", [str(p.relative_to(data)) for p in att],
          [(p.stat().st_size) for p in att])
    for p in att:
        print("mtime age days", (time.time() - p.stat().st_mtime) / 86400)

    print("== 付け直し後 (期待: 40x30) goto ==")
    for i in range(3):
        b = logsize()
        print(i, open_detail("goto"))
    print("== 付け直し後 通常操作 (編集画面を開き、戻るボタンで週画面へ) ==")
    for i in range(3):
        reqs.clear(); cache.clear()
        pg.goto(f"{base}edit/?date={today}&sde_id=" + new_id,
                wait_until="load")
        pg.wait_for_selector("#input_form", state="visible")
        reqs.clear(); cache.clear()
        pg.locator('[data-action="back"]').first.click()
        pg.wait_for_selector("#main", state="visible")
        pg.locator(".my-sde-detail-sw label").first.click()
        pg.wait_for_function(
            "document.querySelector('.my-sde-attach img').complete")
        d = pg.evaluate(
            "[...document.querySelectorAll('.my-sde-attach img')]"
            ".map(i=>[i.naturalWidth,i.naturalHeight])")
        print(i, d, "url", pg.url, "cdp", list(cache), "reqs",
              [(r.status, r.headers.get("last-modified")) for r in reqs])
    br.close()
proc.terminate(); proc.wait(timeout=10)
print((tmp / "server.log").read_text()[-1500:])
