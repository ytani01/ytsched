# TODO-148 verifier 報告

## テスト・lint

- `uv run pytest -q`（フォアグラウンド単独実行） … **595 件全通過**
- `uv run pytest tests/test_browser.py -k trash -q` … 3 件通過
- `uv run ruff format --check src tests` … 35 files already formatted
- `uv run ruff check src tests` … All checks passed
- `uv run basedpyright` … 0 errors
- `uv run mypy src` … Success

## アプリの起動確認

一時ディレクトリ（`/tmp/.../scratchpad/ytsched-data`）に `trash.jsonl`
（同じ `sde_id` の重複グループ 1 組・ToDo・重要マーカー付き予定を含む
計 4 件）と、当日（2026-09-01）の `2026/09/01.jsonl` を自分で書き、
`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18765` を
バックグラウンドで起動して確認した。

- `GET /ytsched/trash` … 200
- `GET /ytsched/`（週間） … 200
- `GET /ytsched/?search_str=会議`（検索） … 200
- `GET /ytsched/?view=month&date=2026-09-01`（月間） … 200
- 取得した HTML に `{{ }}` `{% %}` の生残りなし
- サーバログに例外・トレースバックなし

`/trash` の HTML を確認:

- `.my-date-block` / `.my-date-col` が件数ぶん（4）出ている。年・月・日・
  曜日・今日からの差（今日の予定は `+0`、4 日後は `+4`）が正しい
- `.my-wday-1`（月）`.my-wday-3`（水）`.my-wday-5`（金）と曜日に応じた
  クラスが出ている
- 今日（2026-09-01）の予定に `.my-date-block-today` が付いている
- `.my-sde` `.my-sde-type` `.my-sde-title` が出ており、`sde.html` の
  描画になっている。ToDo は `.my-sde-todo-near`、重要マーカー
  （`(重要)打合せ`）も正しく反映されている
- `<main>` 内に `data-action="edit-sde"` の**属性としての出現は無い**
  （コメント文字列中の文字列としては 4 か所出るが、実際の属性としては
  出ていないことを Python で `<main>`〜`</main>` を切り出して確認済み）
- 同じ `sde_id`（`id-1`）の重複グループで「同じ予定の内容が 2 件」の
  見出しが出ている
- 折りたたみの `<input id="swid...">` は `swid-1-True-0-0` /
  `swid-1-True-0-1` / `swid-3-False-2-0` のように重複なし（重複グループ
  内の 2 件を含めて確認）
- 削除日時の行（`2026-08-30 14:23:05 に削除` など）が各エントリに出ている

## 操作の確認

- 復活（`cmd=restore`） … 302 で `/ytsched/?date=...` へリダイレクト。
  復活後、対象日の `.jsonl` に `(復活)` を先頭に付けた行が追加されて
  いることを確認（ゴミ箱側の件数は変わらない仕様どおり）
- 一括削除（`cmd=delete_many`） … 302 で `/ytsched/trash` へリダイレクト。
  実行後にゴミ箱の件数が 4 件→3 件に減った
- チェックボックスの `data-sde-id` / `data-trashed-at` は今までどおり
  `.my-trash-actions` に残っている

## 見つかった問題

なし。

## 手順上の注意（バグではない）

復活後に対象日のページを見たとき、最初は復活した予定が画面に出ず
戸惑ったが、原因は事前に `search_str=会議` で 1 回リクエストしたのが
`conf.json` に保存され、以後のリクエストにも絞り込みとして効いていた
ためだった（既存の仕様どおり）。`search_str=`（空）を付け直すと表示
された。TODO-148 の変更とは無関係。
