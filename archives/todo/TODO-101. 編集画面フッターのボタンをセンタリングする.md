# TODO-101. 編集画面フッターのボタンをセンタリングする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier + wording |
| 消費 | output 21,192 / cache_creation 168,601 / 概算 $3.3 |
|      | main 86% + verifier 11% + wording 3%（料金の割合） |

分担は [archives/agents/TODO-101/](../agents/TODO-101/) にある。

## きっかけ

編集画面のフッターは、12 列の `.row` に `.col-2` を 6 個並べていた。
中身は戻る・update・fix・複製の 4 つが左の 4 枠、5 枠目が空、削除が
右端で、ボタンが左に寄って見えていた。新規作成のときは複製の枠を
空の `.col-2` で埋めていた。

## やったこと

削除も含めた 5 つを、一定の間隔で中央に並べるようにした（削除の
置き場所は着手時に利用者へ確認し、「5 つまとめて中央に」を選んだ）。

- `edit.html`: `.row` + `.col-2` をやめ、`.my-edit-menu` という入れ物に
  `.my-btn` を直接並べた。複製は `{% if new_flag %}` で空の枠を出して
  いたのを `{% if not new_flag %}` に変え、新規作成のときは枠ごと
  出さない（4 つが中央に寄る）。5 枠目の空の `.col-2` も消した。
- `my.css`: `.my-edit-menu` を足した。`display: flex` で
  `justify-content: center`、間隔は `gap: 0.75rem`。12 列のグリッドでは、
  ボタンの数が 4 つと 5 つで変わるぶん等間隔に割り切れないため。
  `.my-edit-menu > .my-btn` には左右のパディングを付けて、アイコンの
  周りも押せる範囲に含めた。

## テスト

- `mise run lint`（`ruff format` / `ruff check` / `eslint`）・
  `mise run typecheck`（`basedpyright` / `mypy`）: 緑。
- `uv run pytest`: 481 passed。
- 一時 datadir でアプリを起動し、幅 412px（スマホ相当）と 800px で、
  既存の予定（ボタン 5 つ）と新規作成（ボタン 4 つ）の編集画面を
  撮った。どちらの幅でも折り返さず、画面からもはみ出していない。
- 新規作成の画面で `submitCmd('add')`（複製ボタンと同じ経路）を
  実行し、予定が保存されて一覧に出ることを確認。テンプレートの
  展開結果に `{% %}` が残っていないことも確認した。

間隔は最初 `gap: 2rem` にしたが、利用者から「もっと中央にかためて」と
指摘があり `0.75rem` へ詰めた。詰めたあとの画面も同じ 2 つの幅で
撮り直している。
