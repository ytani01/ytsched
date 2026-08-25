#
# (c) 2026 Yoichi Tanibayashi
#
"""アイコンの確認用ページを作る (TODO-048)

``static/icons/icons.svg`` の ``<symbol>`` を並べた HTML を吐く。図案を
描き直したときに、見た目をまとめて確かめるためのもの。

字形が変わると、変更の前後のキャプチャを突き合わせても分からない。
一覧・大きさ・メニューバーに置いた様子を 1 枚にまとめて見るしかない
(TODO-048)。

# 使い方

吐いたページは、その場で配信してから ``screenshot.py`` で撮る。

```
uv run python tools/icons_preview.py
python3 -m http.server 10091 --bind 127.0.0.1 -d ~/tmp/playwright-mcp/icons-preview &
uv run --with playwright python tools/screenshot.py \
    http://127.0.0.1:10091/index.html --full-page -p todo048_icons
```

``icons.svg`` はページに直接埋め込むが、外部ファイルを ``<use>`` で
参照できるかも同じページで見るので、隣にも置いてある。
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2026/08"

import argparse
import pathlib
import shutil
import sys
from typing import Any

from ytsched.mylog import getLogger, loggerInit

_log = getLogger("icons_preview")

#: ``icons.svg`` の場所 (このファイルからの相対)
DEF_SRC = "../src/ytsched/webroot/static/icons/icons.svg"

#: 吐き先。``screenshot.py`` と同じ置き場所の下に作る
DEF_OUTDIR = "~/tmp/playwright-mcp/icons-preview"

#: (``symbol`` の id, どこで何に使っているか)
ICONS = (
    ("home", "今日へ戻る / メニューバー"),
    ("search", "検索 / 検索欄・期間送り"),
    ("bars", "メニューの開閉 / メニューバー"),
    ("chevron-left", "前の週へ / メニューバー"),
    ("chevron-right", "次の週へ / メニューバー"),
    ("angle-down", "詳細の開閉 / 予定の行"),
    ("filter", "絞り込み / メニュー"),
    ("plus-square", "予定を足す / 日付ブロック"),
    ("check-square", "確定 (fix) / 編集画面"),
    ("square", "ToDo の印 / 予定の行"),
    ("circle-up-fill", "検索を過去へ広げる / 検索バー"),
    ("circle-up", "日付を 1 日戻す / 編集画面"),
    ("circle-down", "日付を 1 日進める / 編集画面"),
    ("dot-circle", "今日の日付にする / 編集画面"),
    ("arrows-h", "検索する期間 / 検索バー"),
    ("backspace", "検索文字列を消す / 検索欄"),
    ("trash", "削除 / 編集画面"),
    ("clone", "複製して足す / 編集画面"),
    ("sync", "更新 (update) / 編集画面"),
    ("spinner", "読み込み中 / 一覧・編集画面"),
    ("reply", "前の画面へ戻る / 編集画面 (今は未使用)"),
    ("warning", "読み込みに失敗 / 一覧"),
    ("list", "ToDo を出す日数 / メニュー"),
)

#: 確認用ページの見た目。``my-icon*`` は ``my.css`` へ移す前の下書き
CSS = """
body {
  margin: 0; padding: 16px;
  font-family: sans-serif; color: #222; background: #fff;
}
h1 { font-size: 18px; margin: 0 0 4px; }
h2 {
  font-size: 15px; margin: 24px 0 8px; padding: 4px 8px;
  background: #48C; color: #fff; border-radius: 4px;
}
p.note { font-size: 12px; margin: 4px 0; color: #555; }

.my-icon {
  width: 1em; height: 1em; vertical-align: -0.125em; overflow: visible;
}
.my-icon-lg   { width: 1.25em; height: 1.25em; }
.my-icon-2x   { width: 2em;    height: 2em; }
.my-icon-9x   { width: 9em;    height: 9em;   stroke-width: 1; }
.my-icon-spin { animation: my-icon-spin 2s linear infinite; }
@keyframes my-icon-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 6px;
}
.cell {
  border: 1px solid #ccc; border-radius: 4px; padding: 6px;
  text-align: center;
}
.cell .icons { font-size: 28px; line-height: 1.4; }
.cell .name { font-size: 12px; font-weight: bold; margin-top: 2px; }
.cell .use  { font-size: 11px; color: #666; }

.bar {
  background: #48C; color: #fff; padding: 8px; border-radius: 4px;
  display: flex; justify-content: space-around; align-items: center;
  font-size: 16px;
}
.sizes { font-size: 16px; }
.sizes span { margin-right: 20px; }
.pair {
  display: inline-block; border: 1px solid #ccc; border-radius: 4px;
  padding: 6px 12px; margin: 0 8px 8px 0;
  text-align: center; font-size: 28px;
}
.pair .label { font-size: 11px; color: #666; }
.line { font-size: 14px; line-height: 1.6; }
.ext { font-size: 28px; }
"""


def icon(icon_id: str, cls: str = "my-icon-2x", label: str = "") -> str:
    """``<use>`` で 1 つ参照する。``label`` があれば下に添える。"""
    svg = f'<svg class="my-icon {cls}"><use href="#{icon_id}"></use></svg>'
    if not label:
        return svg
    return f'<div class="pair">{svg}<div class="label">{label}</div></div>'


def cell(icon_id: str, use: str) -> str:
    """一覧の 1 枠。実寸・lg・2x の 3 つを並べる。"""
    sizes = "".join(
        icon(icon_id, cls) for cls in ("", "my-icon-lg", "my-icon-2x")
    )
    return (
        '  <div class="cell">\n'
        f'    <div class="icons">{sizes}</div>\n'
        f'    <div class="name">{icon_id}</div>\n'
        f'    <div class="use">{use}</div>\n'
        "  </div>"
    )


def build(sprite: str) -> str:
    """確認用ページの HTML を組み立てる。"""
    cells = "\n".join(cell(i, u) for i, u in ICONS)

    pairs = "".join(
        icon(i, label=lbl)
        for i, lbl in (
            ("square", "square (ToDo 未)"),
            ("check-square", "check-square (確定)"),
            ("circle-up", "circle-up (輪郭)"),
            ("circle-up-fill", "circle-up-fill (塗り)"),
            ("circle-down", "circle-down"),
            ("dot-circle", "dot-circle"),
        )
    )

    bar1 = "".join(
        icon(i, cls)
        for i, cls in (
            ("bars", "my-icon-lg"),
            ("chevron-left", ""),
            ("chevron-right", ""),
            ("home", "my-icon-lg"),
            ("search", "my-icon-lg"),
            ("backspace", "my-icon-lg"),
        )
    )
    bar2 = "".join(
        icon(i, "my-icon-2x")
        for i in ("sync", "check-square", "clone", "trash")
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>TODO-048 アイコン確認</title>
<style>{CSS}</style>
</head>
<body>
{sprite}

<h1>TODO-048: 自作アイコン {len(ICONS)} 個</h1>
<p class="note">
  24x24 / 太さ 2 の線画。1 つの枠に「実寸(1em) / lg(1.25em) / 2x(2em)」の
  3 つを並べてある。文字の大きさは 28px。
</p>

<h2>1. 一覧 ({len(ICONS)} 個)</h2>
<div class="grid">
{cells}
</div>

<h2>2. 輪郭と塗りの対</h2>
<p class="note">
  外形をそろえて、輪郭だけか中を塗るかで「未選択 / 選択中」を分けている。
</p>
<div>{pairs}</div>

<h2>3. 大きさと、文字と並べたとき</h2>
<div class="sizes">
  <span>{icon("home", "")} 実寸(1em)</span>
  <span>{icon("home", "my-icon-lg")} lg(1.25em)</span>
  <span>{icon("home", "my-icon-2x")} 2x(2em)</span>
</div>
<p class="line">
  行の中に混ぜたとき:
  {icon("search", "my-icon-lg")} 検索 /
  {icon("list", "my-icon-lg")} ToDo 日数 /
  {icon("filter", "my-icon-lg")} 絞り込み /
  {icon("backspace", "my-icon-lg")} 消去
</p>

<h2>4. メニューバーに置いたとき</h2>
<div class="bar">{bar1}</div>
<div class="bar" style="margin-top:6px">{bar2}</div>

<h2>5. 読み込み中のしるし (9x・回転)</h2>
<p class="note">
  9x は 9em = 252px。線が太くなりすぎるので stroke-width を 1 に下げてある。
  回っているのはキャプチャには写らない。
</p>
<div style="opacity:0.3; font-size:16px">
  {icon("spinner", "my-icon-9x my-icon-spin")}
  {icon("sync", "my-icon-9x my-icon-spin")}
</div>
<p class="note">
  左が spinner、右が sync。図案は似ているが、別のままにした
  (更新ボタンと読み込み中が同じ絵になるため)。
</p>

<h2>6. 外部ファイルを &lt;use&gt; で参照できるか</h2>
<p class="note">
  ここだけ <code>&lt;use href="icons.svg#..."&gt;</code> で外のファイルを
  参照している。<b>下に何も出なければ、この方式は使えない</b>
  (その場合はスプライトを base.html に埋め込む)。Chromium では出た
  (2026-08-25 に確認)。
</p>
<div class="ext">
  <svg class="my-icon my-icon-2x"><use href="icons.svg#home"></use></svg>
  <svg class="my-icon my-icon-2x"><use href="icons.svg#search"></use></svg>
  <svg class="my-icon my-icon-2x"><use href="icons.svg#trash"></use></svg>
</div>

</body>
</html>
"""


def parse_args(argv: list[str] | None = None) -> Any:
    """コマンドラインを読む。"""
    parser = argparse.ArgumentParser(
        description="アイコンの確認用ページを作る (TODO-048)"
    )
    _ = parser.add_argument(
        "-s", "--src", default=None, help=f"icons.svg (既定: {DEF_SRC})"
    )
    _ = parser.add_argument(
        "-o",
        "--outdir",
        default=DEF_OUTDIR,
        help=f"吐き先 (既定: {DEF_OUTDIR})",
    )
    _ = parser.add_argument(
        "-d", "--debug", action="store_true", help="debug ログ"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """入口。吐いた index.html のパスを表示する。"""
    args = parse_args(argv)
    loggerInit(debug=args.debug)

    here = pathlib.Path(__file__).resolve().parent
    src = pathlib.Path(args.src).expanduser() if args.src else here / DEF_SRC
    outdir = pathlib.Path(args.outdir).expanduser()

    if not src.exists():
        print(f"見つからない: {src}", file=sys.stderr)
        return 1

    outdir.mkdir(parents=True, exist_ok=True)
    _ = shutil.copy(src, outdir / "icons.svg")

    # XML 宣言は HTML に埋め込めないので落とす
    sprite = src.read_text(encoding="utf-8").split("?>", 1)[-1].strip()

    out = outdir / "index.html"
    _ = out.write_text(build(sprite), encoding="utf-8")
    _log.debug(f"saved: {out}")

    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
