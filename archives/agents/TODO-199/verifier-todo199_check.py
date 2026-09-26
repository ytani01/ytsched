"""TODO-199 ホームボタンの位置合わせを実測する (verifier 用、1 本だけ)。

使い方:
  uv run python todo199_check.py <base_url>

条件ごとに a (今日=日曜のまま) / b (today_str を水曜に書き換え) /
c (ダブルタップ) を測り、JSON で標準出力へ書く。
スクリーンショットは ~/tmp/playwright-mcp/TODO-199-<条件>.png に保存する。
"""

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROMIUM = "/home/ytani/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
SHOT_DIR = Path.home() / "tmp" / "playwright-mcp"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

MONDAY = "2026-09-21"


def measure(page):
    # スクロール (behavior smooth/instant)・遅延読み込みでの scroll anchoring が
    # 落ち着くのを待つ。scrollY が 300ms 変化しなくなるまでポーリングする
    prev = None
    for _ in range(20):
        page.wait_for_timeout(300)
        cur = page.evaluate("window.scrollY")
        if cur == prev:
            break
        prev = cur
    return page.evaluate(
        """() => {
          const today_el = document.getElementById('date-' + ytsched.today_str);
          const menu = document.getElementById('menu_bar');
          const gauge = document.getElementById('footer_gauge_bar');
          const r = today_el ? today_el.getBoundingClientRect() : null;
          const m = menu ? menu.getBoundingClientRect() : null;
          const g = gauge ? gauge.getBoundingClientRect() : null;
          return {
            today_top: r ? r.top : null,
            today_bottom: r ? r.bottom : null,
            menu_top: m ? m.top : null,
            gauge_top: g ? g.top : null,
            scrollY: window.scrollY,
            url: location.href,
          };
        }"""
    )


def get_monday_top_reference(page):
    # "top" 合わせのときの月曜日の scrollY を、直接 scrollToId を呼んで測る
    return page.evaluate(
        """() => {
          const before = window.scrollY;
          ytsched.scrollToId('date-2026-09-21', 'top', 'instant');
          return window.scrollY;
        }"""
    )


def run_condition(pw, name, viewport, is_mobile, has_touch, results):
    browser = pw.chromium.launch(executable_path=CHROMIUM)
    context = browser.new_context(
        viewport=viewport, is_mobile=is_mobile, has_touch=has_touch
    )
    page = context.new_page()
    base_url = sys.argv[1]

    def goto_week(date_str):
        page.goto(f"{base_url}?date={date_str}")
        page.wait_for_selector("#menu_bar")

    def tap_home(n=1):
        home_btn = page.locator("#home_button")
        for _ in range(n):
            if has_touch:
                home_btn.tap()
            else:
                home_btn.click()

    # --- a: 今日=日曜のまま。前の週を開いてからホーム 1 回 ---
    goto_week("2026-09-14")
    tap_home(1)
    page.wait_for_load_state("load")
    page.wait_for_selector("#menu_bar")
    monday_top_ref = get_monday_top_reference(page)
    goto_week("2026-09-14")
    tap_home(1)
    a = measure(page)
    a["monday_top_ref"] = monday_top_ref
    page.screenshot(path=str(SHOT_DIR / f"TODO-199-{name}.png"))
    results[f"{name}-a"] = a

    # --- b: today_str を水曜に書き換えてからホーム 1 回 ---
    goto_week("2026-09-14")
    page.evaluate("ytsched.today_str = '2026-09-23'")
    tap_home(1)
    b = measure(page)
    b["monday_top_ref"] = monday_top_ref
    results[f"{name}-b"] = b

    # --- c: ダブルタップ (350ms 以内) ---
    goto_week("2026-09-14")
    home_btn = page.locator("#home_button")
    if has_touch:
        home_btn.tap()
        page.wait_for_timeout(100)
        home_btn.tap()
    else:
        home_btn.click()
        page.wait_for_timeout(100)
        home_btn.click()
    page.wait_for_timeout(500)  # POST でのリロードを待つ
    c = measure(page)
    c["monday_top_ref"] = monday_top_ref
    results[f"{name}-c"] = c

    # --- 画面の高さを 1080->600 に変えて a と同じ測定 (PC 1920 幅のみ) ---
    if name == "pc1920":
        goto_week("2026-09-14")
        tap_home(1)
        page.set_viewport_size({"width": 1920, "height": 600})
        page.wait_for_timeout(300)
        goto_week("2026-09-14")
        tap_home(1)
        d = measure(page)
        d["monday_top_ref"] = monday_top_ref
        page.screenshot(path=str(SHOT_DIR / f"TODO-199-{name}-h600.png"))
        results[f"{name}-h600"] = d

    context.close()
    browser.close()


def main():
    results = {}
    with sync_playwright() as pw:
        run_condition(pw, "pc1920", {"width": 1920, "height": 1080}, False, False, results)
        run_condition(pw, "pc1366", {"width": 1366, "height": 768}, False, False, results)
        run_condition(pw, "mobile390", {"width": 390, "height": 844}, True, True, results)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
