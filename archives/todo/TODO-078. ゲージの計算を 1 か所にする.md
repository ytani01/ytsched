# TODO-078. ゲージの計算を 1 か所にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 14,491 / cache_creation 254,091 / 概算 $8.1 |
|      | main 70% + implementer 22% + reviewer 4% + verifier 3%（料金の割合） |

## きっかけ

基本設計のレビュー（`docs/design-review.md` の A・E）で見つかった。

`main_handler.py` の `days2x_percent()` / `calc_gauge_label()` と定数 4 つが、
`my.js` の `days2xPercent()` / `gaugeDiffLabel()` と同名の定数に、
同じ式・同じ数値で二重にあった。`calc_gauge_label()` の docstring 自身が
「食い違うと針が動く前後で文字が変わって見える」と書いており、
揃え続けるのが人の注意任せだった。

## 決めたこと

**JavaScript に寄せて、Python 側を消した。**

目盛りの位置（`GAUGE`）も針の上の文字（`gauge_label`）も、サーバが
埋めるのは読み込み直後の一度だけで、あとは `my.js` が書き換えていた。
JavaScript 側には同じ式が既にあるので、初回の描画も JavaScript に
やらせれば Python 側は要らなくなる。

**両方残して数値が一致することを見るテストを置く案は採らなかった。**
比べるのに結局ブラウザが要るうえ、二重に持つこと自体は解消しない。

項目名の「別ファイルへ分ける」も**やっていない**。Python 側が丸ごと
消えたので、`main_handler.py` から出すものが残らなかった。JavaScript
側をファイルに分けるのは TODO-083 の範囲。

## やったこと

- `my.js` に `GAUGE_MARKS`（目盛り 14 個の一覧）と `dispGaugeMarks()`
  （`.my-gauge-bar` へ目盛りを描く。帯が無ければ何もしない）を足した
- `main.html` の `onloadHdr()` から `dispGaugeMarks()` を一度だけ呼ぶ。
  `{{ gauge_label }}` は空にした（`dispGauge()` →
  `setGaugePosition()` が読み込み時に必ず埋める）
- `main.html` の `{% for d in gauge %}` を消した
- `main_handler.py` から `days2x_percent()` / `calc_gauge_label()` /
  `DAYS_YEAR` / `DAYS_MONTH` / `DAYS_GAUGE_MAX` / `DAYS_GAUGE_K` /
  `GAUGE` と、`render()` に渡していた 2 つ、`import math` を消した
  （96 行減）

## テスト

Python 側で見ていた 10 本を消し、**観点はブラウザ側へ移した**。

- `tests/test_handler.py` の `test_days2x_percent_*` 5 本 →
  `tests/test_browser.py` で `page.evaluate()` から `days2xPercent()` を
  直に呼ぶ 5 本に
- `tests/test_main_handler.py` の `test_calc_gauge_label_*` 2 本 →
  `test_gauge_diff_label_reflects_the_week_offset` /
  `test_gauge_diff_label_switches_unit` に
- `tests/test_web.py` の 3 本のうち 1 本は既存のブラウザのテストと
  重複していたので消し、残り 2 本は上の 2 本へ移した
- 目盛りが 14 個描かれ、`-1w`=46.21%・`+1w`=53.79% の位置に出ることを
  見るテストを足した。期待値は変更前の Python の式から実測した
- `mise run lint` 通過。`uv run pytest tests` 459 passed（skip なし）

verifier が変更前後の画面を撮って見比べ、**キャプチャが完全に一致**する
ことを確かめた（main が md5 でも確かめた）。今週から離れた週を直接
開いても、読み込み直後から目盛りと針の文字が出ている。

分担と報告は [`archives/agents/TODO-078/`](../agents/TODO-078/README.md)。
