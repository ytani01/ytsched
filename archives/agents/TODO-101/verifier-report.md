# TODO-101 verifier 報告

## 1. lint / typecheck / test

- `mise run lint` -- ○ (`ruff format` 31 files left unchanged / `ruff check` All checks passed / `eslint` 問題なし)
- `mise run typecheck` -- ○ (`basedpyright` 0 errors, 0 warnings, 0 notes / `mypy` Success: no issues found in 28 source files)
- `uv run pytest -q` -- ○ 481 passed in 61.19s

## 2. 画面の確認

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 10099` を
`run_in_background` で起動し、`curl -s -o /dev/null -w '%{http_code}'` で
`http://localhost:10099/ytsched/` が 200 を確認。

`tools/screenshot.py` は一覧画面用の URL しか撮れない（編集画面は
`sde_id` が要り、フォームクリックを介した遷移になる）ため、その仕組みを
借りて自前の短い playwright スクリプトを書き、幅 412px / 800px ×
新規作成・既存編集の 4 枚を撮った（スクリプトはスクラッチパッドに置き、
リポジトリには置いていない）。

- `~/tmp/playwright-mcp/todo101_new_412.png` -- 新規作成、ボタン 4 つ
  （戻る・リロード・fix・削除）が中央に等間隔で並ぶ
- `~/tmp/playwright-mcp/todo101_new_800.png` -- 同上、幅 800px
- `~/tmp/playwright-mcp/todo101_existing_412.png` -- 既存編集、ボタン 5 つ
  （戻る・リロード・fix・複製・削除）が中央に等間隔で並ぶ
- `~/tmp/playwright-mcp/todo101_existing_800.png` -- 同上、幅 800px

412px（スマホ相当）・800px のどちらも、5 個の `.my-btn` が折り返さず
1 行に収まり、画面からはみ出していない。`gap: 2rem` は見た目やや広めだが
崩れてはいない（この判断は目視によるもので、主観の余地あり）。

## 3. ボタンの動作

- 新規作成画面で `title` に `TESTITEM` を入力し、
  `page.evaluate("submitCmd('add')")` を実行 → 保存されて週表示へ
  リダイレクトされ、一覧に `TESTITEM` が現れた（複製ボタンの
  `submitCmd('add')` と同じ経路を通ることを確認）
- 一覧の `TESTITEM` をクリックして既存編集画面へ遷移 → 5 ボタン
  （戻る・update・fix・add・del）が表示され、`sde_id` も入っている
- `{% if not new_flag %}` ... `{% end %}` のテンプレート構文は、
  新規作成画面・既存編集画面のどちらも `curl` で取得した HTML に
  `{{ }}` `{% %}` が生で残っていないことを確認（Tornado テンプレートが
  正しく展開されている）
- サーバのログ（`todo101-server.log`）に例外・トレースバックは出て
  いない

「戻る」「update」「fix」「del」の onmousedown まではクリックして
確認していない（`add` のみクリックで確認）。テンプレートの
`onmousedown` 属性そのものは変更前と同じ文字列で、`.my-btn` の並べ方
（flex）だけを変えた変更なので、挙動が壊れる要素は見当たらない。

## 判断が要る点

特になし。lint / typecheck / test / 画面表示のいずれも問題は
見つからなかった。
