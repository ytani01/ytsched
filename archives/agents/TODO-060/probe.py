from playwright.sync_api import sync_playwright

BASE = "http://localhost:10099/ytsched/"

INIT = """
window.__probe = {samples: [], marks: [], prev: null};
try { window.__probe.prev =
        sessionStorage.getItem('ytsched_gage_monday'); } catch (e) {}
const t0 = performance.now();
const mark = (n) => window.__probe.marks.push([n,
    Math.round(performance.now() - t0)]);
document.addEventListener('DOMContentLoaded', () => mark('DOMContentLoaded'));
window.addEventListener('load', () => mark('load'));
const tick = () => {
    const el = document.getElementById('gage_r');
    if (el) {
        const s = el.style.left || '(未設定)';
        const c = getComputedStyle(el).left;
        const last = window.__probe.samples.at(-1);
        if (!last || last[1] !== s || last[2] !== c) {
            window.__probe.samples.push(
                [Math.round(performance.now() - t0), s, c]);
        }
    }
    if (performance.now() - t0 < 1500) requestAnimationFrame(tick);
};
tick();
"""

def run(pg, url, label):
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(1200)
    p = pg.evaluate("window.__probe")
    print(f"--- {label}")
    print(f"    前の週 (sessionStorage): {p['prev']}")
    print(f"    {p['marks']}")
    for t, s, c in p["samples"][:12]:
        print(f"      {t:5d}ms  style.left={s:>12s}  computed={c}")

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/chromium")
    ctx = b.new_context(viewport={"width": 412, "height": 900})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    run(pg, BASE + "?date=2027-08-25", "① 初回 (sessionStorage 空)")
    run(pg, BASE + "?date=2027-08-25", "② 同じ週をもう一度")
    run(pg, BASE + "?date=2027-09-01", "③ 隣の週へ")
    b.close()
