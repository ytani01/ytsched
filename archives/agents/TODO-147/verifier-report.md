# TODO-147 verifier 報告

## 1. lint / 型チェック / テスト

- `uv run ruff format --check` : × 9 files would be reformatted。ただし内訳は
  `archives/todo/*.md` など今回の変更と無関係なファイルのみ（今回変更した
  `main.html` / `my.css` は対象外＝ Python ファイルではないため関知しない）。
  今回の diff によるものではない
- `uv run ruff check` : ○ All checks passed!
- `uv run basedpyright` : ○ 0 errors, 0 warnings, 0 notes
- `uv run mypy src` : ○ Success: no issues found in 19 source files
- `uv run pytest -q` : ○ 589 passed in 156.84s

## 2. 週間表示の見出し行

一時 datadir にダミー予定を 2 件作成（`2026-03-30` と `2026-04-06`）し、
`uv run ytsched webapp --datadir <一時dir> --port 18147` を起動して確認。

- `?date=2026-03-30`（月をまたぐ週、`data-offset="0"`）: 見出しが
  `2026/03` → `2026/04` の順に **2 行**、日付ブロックの直前に出現。○
- `?date=2026-04-06`（またがない週）: 見出しは `2026/04` の **1 行**のみ。○
- 隣接週（前後に読み込まれる `my-week-panel`、offset -4〜4）も
  1 週ごとに先頭で必ず見出しが出ており、`cur_ym` が週をまたいで
  持ち越されていないことを確認（offset -1 の末尾が `2026/03` でも、
  offset 0 の先頭は `2026/03` から出し直している）。○
- 週間表示の日付欄（`my-date-ym`）: 出現数 0。年月は出ておらず、
  日・曜日・今日からの日数のみ。○

## 3. 検索モード

`?search_str=xtest` で検索モードにして確認。

- `my-month-header` : 出現数 0（出ない）。○
- `my-date-ym` : 出現数 2（該当する 2 件の日付ブロックに残っている）。○

## 4. 月間表示・ゴミ箱

- `?view=month` : `my-month-header` / `my-date-ym` とも出現数 0（無関係で影響なし）。○
- `/ytsched/trash`（url_prefix 付き。トップページの実際のリンク先で確認）: HTTP 200。
  テンプレート未展開の `{{` `{%` 残りなし。○
  （※依頼文中の `/trash` は url_prefix 抜きのパスで、実際には
  `/ytsched/trash` が正しい。404 は url_prefix を付け忘れた自分の
  誤りで、実装の不具合ではない）

## 5. サーバログ

`INFO webapp.py:127 main()> start server: run forever ..` のみで、
例外・トレースバックは出ていない。

## その他の気づき（実装への指摘ではない、参考情報）

- `search_str` はクエリパラメータとして送ると設定ファイルに永続化される
  （`_update_conf_arg`）。検証中、`?search_str=xtest` を送った後に
  `?search_str=` を送り忘れると、以降 `?date=...` だけのリクエストでも
  検索モードのままになる（今回はこれで一度気づかずに検索モードの画面を
  見てしまった）。TODO-147 の実装とは無関係の既存挙動。

## 追記: tests/test_web.py の TestMonthHeader 確認

- `uv run pytest tests/test_web.py -q` : ○ 149 passed（既存を壊していない）
- `uv run ruff format --check tests/test_web.py` : ○ 1 file already formatted
- `uv run ruff check tests/test_web.py` : ○ All checks passed!

テストの中身も確認した。

- `week_panel()` は `my-week-cur` が付いた「いま見ている週」だけを
  切り出すヘルパーで、`test_header_at_week_top` / `test_header_at_month_border`
  はその中だけを見ている。手動確認（offset=0 のパネルだけ抜き出した結果）
  と一致しており、前後の週を巻き込んで素通りする作りにはなっていない
- `test_header_at_month_border` は `my-month-header">2021/04` の出現位置と
  `date_id(2021-04-01)` の出現位置を `index()` で比較しており、順番
  （見出しが日付ブロックより先）まで見ている。文字列の有無だけでなく
  順序も検証していて妥当
- `test_no_ym_in_date_col` は `week_panel()` を通さず本文全体
  （前後の週パネルも含む）で `"my-date-ym" not in body` を見ている。
  依頼文にある懸念どおり範囲が広いが、これは意図的に隣接週も含めて
  「週間表示なら 1 つも無いはず」を確認する強い検証であり、妥当。
  自分の手動確認（ファイル全体で `grep -c my-date-ym` が 0）とも一致する
- `test_search_mode` は `search_str="病院"` で検索モードにし、
  `my-month-header` が無く `my-date-ym` があることを見ている。手動確認と
  同じ観点で、素通りするテストにはなっていない

4 件とも、実装の意図（週の先頭に必ず 1 行・月の境目にもう 1 行・検索モードは
従来どおり）を実際に検証できている。指摘なし。
