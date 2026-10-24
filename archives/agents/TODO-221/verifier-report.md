# verifier の報告（TODO-221・TODO-224）

担当が報告ファイルを書けなかったため、返事の内容を main が写した。

- `mise run lint`: エラー無し。`mise run typecheck`: basedpyright 0 errors、mypy Success（39 files）。`mise run test`: 727 passed
- CLI（一時ディレクトリ、`--date 2026-10-05`）
  - `--days 3`: 空の日も出る。行は `[会議] 定例 @本社`、ToDo は `10-06 [予約] __ @歯科`
  - `--days 3 --skip-empty --detail`: 10-07 の節だけ。詳細 2 行が 4 字下げで出る
  - `--days 2 --skip-empty`: `2026-10-05 (月) 〜 10-06 (火)` と「予定なし」。ToDo の節は出る
  - 上に `--url` を足す: 見出しがリンクになり、予定の行が `` ` `` で囲まれる（TODO-222 の仕様どおり）
- 壊すと落ちるか
  - `rstrip("\n")` を消す → test_detail_lines_indented が落ちる
  - `or "__"` を消す → 2 件落ちる
  - `skip_empty and` を消す → test_skip_empty_off_keeps_empty_days が落ちる
