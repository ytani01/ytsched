# TODO-174. 週間表示のミニカレンダーの見出しをボタンらしく見せる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier + runner |
| 消費 | output 18,179 / cache_creation 88,367 / 概算 $2.0 |
|      | main 85% + verifier 13% + runner 2%（料金の割合） |

runner を足した理由は
[archives/agents/TODO-174/README.md](../agents/TODO-174/README.md)。

## きっかけ

週間表示の下にあるミニカレンダーの見出し `2026/09` は、押すとその月を
含む 6 か月ブロックの月間表示へ移る（`data-action="month-view"`、
TODO-137）。ただし `.my-mini-cal-caption` の CSS は
`font-weight: bold` だけで、太字のテキストにしか見えず、押せることが
分からなかった。

## やったこと

`mini_cal.html` と `my.css` の 2 ファイル。

- **押せるときだけ、中身を span で包んだ。** `caption` 要素に直接枠を
  付けると表の幅いっぱいに広がるので、
  `<span class="my-mini-cal-caption-btn my-btn">` を中に置き、
  `data-action` / `data-date` も caption からその span へ移した。
  クリックの処理は `main-page.js` の `closest("[data-action]")` なので、
  移しても拾われる
- **枠は `.my-mini-cal-caption-btn` に付けた。** `inline-block`、
  1px の枠（`#AAA`）、角丸 4px、左右 8px の余白、背景 `#EEE`。
  押したときの黄色は既存の `.my-btn:active` がそのまま効き、
  枠の中だけが黄色くなる
- **`.my-mini-cal-caption` に `text-align: center` を明示した。**
  span を `inline-block` にしたので、中央に置く指定を UA の既定に
  任せずに書いた
- **月間表示のミニカレンダーは変えていない。**
  `mini_cal_caption_action` が空で押せないため、span も枠も付かない

## テスト

`tests/test_web.py::TestMonthMiniCal::test_shows_two_months` が落ちた。
`my-mini-cal-caption[^>]*>\s*([^<]+?)\s*<` という正規表現で caption の
中身を取っていたが、span を入れたことで最初の `<` までが改行だけに
なったため。**caption の中身をタグごと取り、タグを剥がしてから比べる
形に直した**（押せない月間表示側は span が無いので、どちらも同じ形で
取れる）。

`tests/test_browser.py::test_month_view_round_trip` は直さずに通った。
`.my-mini-cal-caption` の中心をクリックしているが、`text-align: center`
で span が中央に来るので、そのまま span に当たる。

verifier の確認は
[archives/agents/TODO-174/verifier-report.md](../agents/TODO-174/verifier-report.md)。
`pytest` 665 件のうち上の 1 件だけが落ち、`ruff format --check` /
`ruff check` / `basedpyright` / `mypy` は通過。実際の HTML で、週間表示
だけ span と枠が付き、月間表示には付かないことも確かめた。テストを
直したあとの再実行は
[archives/agents/TODO-174/runner-report.md](../agents/TODO-174/runner-report.md)。

見た目は、chromium で撮ったキャプチャを利用者に見せて確認した
（通常の状態と、押している状態の 2 枚）。
