#
# (c) 2026 ytani01
#
"""画面のキャプチャに引き出し線と吹き出しを重ねる (TODO-152)

``docs/User.md`` に貼る図を作る。``tools/screenshot.py`` で撮った PNG を
HTML に貼り、その上へ吹き出しを絶対位置で並べ、引き出し線を SVG で引いて、
chromium で撮り直す。

注釈の位置は JSON に書く（既定は ``tools/user-figs.json``）。画面を撮り
直したら、同じ JSON でもう一度流せばよい。

# 使い方

```
uv run python tools/annotate.py --srcdir ~/tmp/playwright-mcp
uv run python tools/annotate.py --only user-week --outdir /tmp/try
```

# JSON の書き方

```json
{
  "outdir": "docs",
  "scale": 2,
  "pad": {"left": 150, "right": 150, "top": 16, "bottom": 16},
  "figures": [
    {
      "name": "user-week",
      "src": "week_closed_412.png",
      "width": 412,
      "notes": [
        {"text": "ゲージ", "to": [206, 20], "at": [-145, 8], "w": 140}
      ]
    }
  ]
}
```

- ``width`` は画像を並べるときの幅 (px)。``tools/screenshot.py`` に渡した
  ``-w`` の値。画像そのものは ``--scale`` 倍で撮ってあるので、この幅に
  縮めて置き、``scale`` 倍で撮り直すと元の解像度に戻る
- ``to`` は指し示す点、``at`` は吹き出しの左上。**どちらも画像の左上を
  原点とした px** で、余白へ出すときは負の値や ``width`` より大きい値に
  なる。``w`` は吹き出しの幅 (px、既定 140)
- ``crop`` に ``[x, y, w, h]`` を書くと、画像のその範囲だけを見せる
  （画面の一部だけを図にしたいとき）。**このとき ``to`` と ``at`` の
  原点も、切り出した左上へ移る**
- 引き出し線の根元は、吹き出しのどの辺から出すかをブラウザ側で決める
  （吹き出しの中心と指し示す点の位置関係で選ぶ）
"""

__author__ = "ytani01"
__date__ = "2026/09"

import argparse
import base64
import json
import pathlib
import sys
from typing import Any

from ytsched.mylog import exmsg, getLogger, loggerInit

_log = getLogger("annotate")

#: 注釈の位置を書いた JSON
DEF_SPEC = "tools/user-figs.json"

#: 撮ったキャプチャの置き場所 (``tools/screenshot.py`` の既定と同じ)
DEF_SRCDIR = "~/tmp/playwright-mcp"

#: ブラウザの実行ファイル (``tools/screenshot.py`` と同じ理由で決め打ち)
DEF_CHROMIUM = "/usr/bin/chromium"

#: 吹き出しの既定の幅 (px)
DEF_NOTE_W = 140

#: 余白の既定値 (px)
DEF_PAD = {"left": 150, "right": 150, "top": 16, "bottom": 16}

#: 既定のデバイスピクセル比
DEF_SCALE = 2.0

#: 吹き出しと引き出し線の色
COLOR = "#d33"

_CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #fff;
  font-family: "Noto Sans CJK JP", "IPAPGothic", sans-serif; }
#fig { position: relative; background: #fff; }
#shotbox { position: absolute; overflow: hidden; }
#shot { position: absolute; display: block; }
#lines { position: absolute; left: 0; top: 0; overflow: visible;
  pointer-events: none; }
.note { position: absolute; background: #fff; color: __COLOR__;
  border: 1.5px solid __COLOR__; border-radius: 6px;
  padding: 3px 6px; font-size: 12px; line-height: 1.35;
  white-space: pre-wrap; }
""".replace("__COLOR__", COLOR)

# 吹き出しの位置と指し示す点から、線の根元（吹き出しのどの辺の中央か）を
# 選んで引く。横のずれが縦より大きければ左右の辺、そうでなければ上下の辺
_JS = """
const box = document.getElementById('fig').getBoundingClientRect();
const svg = document.getElementById('lines');
const ns = 'http://www.w3.org/2000/svg';
for (const el of document.querySelectorAll('.note')) {
  const r = el.getBoundingClientRect();
  const tx = parseFloat(el.dataset.tx), ty = parseFloat(el.dataset.ty);
  const cx = r.left + r.width / 2 - box.left;
  const cy = r.top + r.height / 2 - box.top;
  let sx, sy;
  if (Math.abs(tx - cx) > Math.abs(ty - cy)) {
    sx = (tx > cx ? r.right : r.left) - box.left;
    sy = cy;
  } else {
    sx = cx;
    sy = (ty > cy ? r.bottom : r.top) - box.top;
  }
  const line = document.createElementNS(ns, 'line');
  line.setAttribute('x1', sx); line.setAttribute('y1', sy);
  line.setAttribute('x2', tx); line.setAttribute('y2', ty);
  line.setAttribute('stroke', '__COLOR__');
  line.setAttribute('stroke-width', '1.5');
  svg.appendChild(line);
  const dot = document.createElementNS(ns, 'circle');
  dot.setAttribute('cx', tx); dot.setAttribute('cy', ty);
  dot.setAttribute('r', '4');
  dot.setAttribute('fill', '__COLOR__');
  svg.appendChild(dot);
}
""".replace("__COLOR__", COLOR)


def _data_uri(path: pathlib.Path) -> str:
    """PNG を data: URI にする。

    ``page.set_content()`` で開いたページは about:blank 扱いになり、
    ``file:`` の画像を読めない。埋め込んで渡す。
    """
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _esc(text: str) -> str:
    """HTML のテキストとして書ける形にする。"""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def build_html(
    src: pathlib.Path,
    width: int,
    height: int,
    notes: list[dict[str, Any]],
    pad: dict[str, int],
    crop: list[int] | None = None,
) -> str:
    """1 枚ぶんの HTML を組み立てる。

    画像は ``pad`` のぶんだけずらして置き、吹き出しの座標は画像の左上を
    原点として扱う。``crop`` (``[x, y, w, h]``) があれば、その範囲だけを
    見せる。**吹き出しの座標の原点も、切り出した左上へ移る。**
    """
    crop_x, crop_y, view_w, view_h = crop or [0, 0, width, height]
    total_w = pad["left"] + view_w + pad["right"]
    total_h = pad["top"] + view_h + pad["bottom"]

    items: list[str] = []
    for note in notes:
        at_x, at_y = note["at"]
        to_x, to_y = note["to"]
        note_w = note.get("w", DEF_NOTE_W)
        items.append(
            f'<div class="note" style="left:{pad["left"] + at_x}px;'
            f'top:{pad["top"] + at_y}px;width:{note_w}px"'
            f' data-tx="{pad["left"] + to_x}" data-ty="{pad["top"] + to_y}">'
            f"{_esc(note['text'])}</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><style>{_CSS}</style></head>
<body>
<div id="fig" style="width:{total_w}px;height:{total_h}px">
  <div id="shotbox" style="left:{pad["left"]}px;top:{pad["top"]}px;
    width:{view_w}px;height:{view_h}px">
    <img id="shot" src="{_data_uri(src)}" style="left:{-crop_x}px;
      top:{-crop_y}px;width:{width}px;height:{height}px">
  </div>
  <svg id="lines" width="{total_w}" height="{total_h}"></svg>
  {"".join(items)}
</div>
<script>{_JS}</script>
</body></html>
"""


def annotate(
    figures: list[dict[str, Any]],
    srcdir: pathlib.Path,
    outdir: pathlib.Path,
    pad: dict[str, int],
    scale: float,
    chromium: str,
) -> list[pathlib.Path]:
    """図を作って、保存したファイルの一覧を返す。"""
    from playwright.sync_api import sync_playwright

    outdir.mkdir(parents=True, exist_ok=True)
    saved: list[pathlib.Path] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium)
        try:
            for fig in figures:
                src = srcdir / fig["src"]
                if not src.exists():
                    raise FileNotFoundError(str(src))

                fig_pad = {**pad, **fig.get("pad", {})}
                width = fig["width"]
                # 撮った画像は scale 倍なので、幅から高さを割り出す
                src_w, src_h = _png_size(src)
                height = round(src_h * width / src_w)

                html = build_html(
                    src,
                    width,
                    height,
                    fig.get("notes", []),
                    fig_pad,
                    fig.get("crop"),
                )
                page = browser.new_page(device_scale_factor=scale)
                page.set_content(html, wait_until="load")
                page.wait_for_timeout(200)

                path = outdir / f"{fig['name']}.png"
                page.locator("#fig").screenshot(path=str(path))
                page.close()
                saved.append(path)
                _log.info(f"saved: {path}")
        finally:
            browser.close()

    return saved


def _png_size(path: pathlib.Path) -> tuple[int, int]:
    """PNG の幅と高さを、ヘッダ (IHDR) から読む。"""
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"PNG ではない: {path}")
    return (
        int.from_bytes(head[16:20], "big"),
        int.from_bytes(head[20:24], "big"),
    )


def parse_args(argv: list[str] | None = None) -> Any:
    """コマンドラインを読む。"""
    parser = argparse.ArgumentParser(
        description="画面のキャプチャに注釈を重ねる (TODO-152)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "先に tools/screenshot.py で画面を撮っておくこと。"
            "注釈の位置は JSON に書く。"
        ),
    )
    _ = parser.add_argument(
        "--spec", default=DEF_SPEC, help=f"注釈の JSON (既定: {DEF_SPEC})"
    )
    _ = parser.add_argument(
        "--srcdir",
        default=None,
        help=f"キャプチャの置き場所 (既定: {DEF_SRCDIR})",
    )
    _ = parser.add_argument(
        "-o", "--outdir", default=None, help="保存先 (既定: JSON の outdir)"
    )
    _ = parser.add_argument(
        "--only",
        action="append",
        dest="only",
        help="この名前の図だけ作る。複数回渡せる",
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

    spec_path = pathlib.Path(args.spec).expanduser()
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print(f"{spec_path}: {exmsg(ex)}", file=sys.stderr)
        return 1

    figures = spec.get("figures", [])
    if args.only:
        figures = [f for f in figures if f["name"] in args.only]
        if not figures:
            print(f"その名前の図が無い: {args.only}", file=sys.stderr)
            return 1

    srcdir = pathlib.Path(
        args.srcdir or spec.get("srcdir", DEF_SRCDIR)
    ).expanduser()
    outdir = pathlib.Path(args.outdir or spec.get("outdir", ".")).expanduser()

    if not pathlib.Path(args.chromium).exists():
        print(
            f"ブラウザが見つからない: {args.chromium}\n"
            "--chromium で場所を指定する。",
            file=sys.stderr,
        )
        return 1

    try:
        saved = annotate(
            figures=figures,
            srcdir=srcdir,
            outdir=outdir,
            pad={**DEF_PAD, **spec.get("pad", {})},
            scale=spec.get("scale", DEF_SCALE),
            chromium=args.chromium,
        )
    except ImportError as ex:
        print(
            f"{exmsg(ex)}\nplaywright が要る。`uv sync` で入る。",
            file=sys.stderr,
        )
        return 1
    except Exception as ex:  # noqa: BLE001
        print(exmsg(ex), file=sys.stderr)
        return 1

    for path in saved:
        print(path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
