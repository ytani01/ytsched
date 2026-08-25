#
# (c) 2026 Yoichi Tanibayashi
#
"""アプリの画面を撮る (TODO-046)

見た目を変える項目では、テストだけでは確かめられず、画面を見るしかない
(TODO-042・TODO-043・TODO-045)。そのたびに playwright を動かす短いコードを
書き直していたので、まとめたもの。

ブラウザはシステムの ``/usr/bin/chromium`` を使う。
``~/.cache/ms-playwright`` にあるビルドは playwright-mcp が入れたもので、
``uv run --with playwright`` が取ってくる版とは合わず起動しない
(TODO-045)。

# 使い方

```
uv run --with playwright python tools/screenshot.py
uv run --with playwright python tools/screenshot.py --width 412 --width 800
uv run --with playwright python tools/screenshot.py -p todo047 --open
```

``mise run shot -- --open`` でも同じ。

撮る前に、アプリを起動しておくこと。**実データを汚さないよう、確かめる
ときは ``--datadir`` に一時ディレクトリを指定する。**

```
uv run ytsched webapp --datadir /tmp/somewhere --port 10085
```
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2026/08"

import argparse
import pathlib
import sys
from typing import Any

from ytsched.mylog import exmsg, getLogger, loggerInit

_log = getLogger("screenshot")

#: 既定の URL (``mise run webapp`` の待ち受け先)。
#: ``--urlprefix`` の既定 (``/ytsched``) に合わせてある。一覧は ``/`` にも
#: 割り当ててあるが、編集画面は前置きが無いと 404 になる (TODO-051)
DEF_URL = "http://localhost:10085/ytsched/"

#: 既定の画面の幅 (px)。スマホと、広めの窓
DEF_WIDTHS = (412, 800)

#: 既定の画面の高さ (px)
DEF_HEIGHT = 900

#: 保存先。利用者に見せる置き場所 (``~/.claude/CLAUDE.md`` 参照)
DEF_OUTDIR = "~/tmp/playwright-mcp"

#: ブラウザの実行ファイル
DEF_CHROMIUM = "/usr/bin/chromium"

#: ``--open`` で開くもの。詳細 (detail) の開閉スイッチ
DEF_TOGGLE = "input.longtext-sw"


def shoot(
    url: str,
    widths: list[int],
    height: int,
    outdir: pathlib.Path,
    prefix: str,
    chromium: str,
    toggle: str,
    open_toggles: bool,
    full_page: bool,
) -> list[pathlib.Path]:
    """画面を撮って、保存したファイルの一覧を返す。

    ``open_toggles`` が真なら、``toggle`` に当たるチェックボックスを
    すべて入れた状態も撮る。幅ごとに ``closed`` と ``open`` の 2 枚。
    """
    from playwright.sync_api import sync_playwright

    outdir.mkdir(parents=True, exist_ok=True)
    saved: list[pathlib.Path] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium)
        try:
            for width in widths:
                page = browser.new_page(
                    viewport={"width": width, "height": height}
                )
                page.goto(url, wait_until="networkidle")

                path = outdir / f"{prefix}_closed_{width}.png"
                page.screenshot(path=str(path), full_page=full_page)
                saved.append(path)
                _log.info(f"saved: {path}")

                if open_toggles:
                    boxes = page.locator(toggle).all()
                    for box in boxes:
                        box.evaluate("el => el.checked = true")
                    _log.debug(f"opened {len(boxes)} toggle(s)")
                    # 開いたあとの描画を待つ
                    page.wait_for_timeout(300)

                    path = outdir / f"{prefix}_open_{width}.png"
                    page.screenshot(path=str(path), full_page=full_page)
                    saved.append(path)
                    _log.info(f"saved: {path}")

                page.close()
        finally:
            browser.close()

    return saved


def parse_args(argv: list[str] | None = None) -> Any:
    """コマンドラインを読む。"""
    parser = argparse.ArgumentParser(
        description="アプリの画面を撮る (TODO-046)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "撮る前にアプリを起動しておくこと。実データを汚さないよう、"
            "確かめるときは --datadir に一時ディレクトリを指定する。"
        ),
    )
    _ = parser.add_argument(
        "url", nargs="?", default=DEF_URL, help=f"URL (既定: {DEF_URL})"
    )
    _ = parser.add_argument(
        "-w",
        "--width",
        type=int,
        action="append",
        dest="widths",
        help=f"画面の幅 (px)。複数回渡せる (既定: {list(DEF_WIDTHS)})",
    )
    _ = parser.add_argument(
        "--height",
        type=int,
        default=DEF_HEIGHT,
        help=f"画面の高さ (px) (既定: {DEF_HEIGHT})",
    )
    _ = parser.add_argument(
        "-o",
        "--outdir",
        default=DEF_OUTDIR,
        help=f"保存先 (既定: {DEF_OUTDIR})",
    )
    _ = parser.add_argument(
        "-p",
        "--prefix",
        default="shot",
        help="ファイル名の頭 (既定: shot)",
    )
    _ = parser.add_argument(
        "--open",
        action="store_true",
        dest="open_toggles",
        help="開閉するものを開いた状態も撮る",
    )
    _ = parser.add_argument(
        "--toggle",
        default=DEF_TOGGLE,
        help=f"--open で開くもの (既定: {DEF_TOGGLE})",
    )
    _ = parser.add_argument(
        "--full-page",
        action="store_true",
        help="画面に収まらない分も含めて撮る",
    )
    _ = parser.add_argument(
        "--chromium",
        default=DEF_CHROMIUM,
        help=f"ブラウザの実行ファイル (既定: {DEF_CHROMIUM})",
    )
    _ = parser.add_argument(
        "-d", "--debug", action="store_true", help="debug ログ"
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """入口。保存したファイルのパスを表示する。"""
    args = parse_args(argv)
    loggerInit(debug=args.debug)
    _log.debug(f"args={args}")

    widths: list[int] = args.widths or list(DEF_WIDTHS)
    outdir = pathlib.Path(args.outdir).expanduser()

    if not pathlib.Path(args.chromium).exists():
        print(
            f"ブラウザが見つからない: {args.chromium}\n"
            "--chromium で場所を指定する。",
            file=sys.stderr,
        )
        return 1

    try:
        saved = shoot(
            url=args.url,
            widths=widths,
            height=args.height,
            outdir=outdir,
            prefix=args.prefix,
            chromium=args.chromium,
            toggle=args.toggle,
            open_toggles=args.open_toggles,
            full_page=args.full_page,
        )
    except ImportError as ex:
        print(
            f"{exmsg(ex)}\n"
            "playwright が要る。"
            "`uv run --with playwright python tools/screenshot.py` "
            "で走らせる。",
            file=sys.stderr,
        )
        return 1
    except Exception as ex:  # noqa: BLE001
        print(exmsg(ex), file=sys.stderr)
        print(
            f"アプリが {args.url} で動いているか確かめる。",
            file=sys.stderr,
        )
        return 1

    for path in saved:
        print(path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
