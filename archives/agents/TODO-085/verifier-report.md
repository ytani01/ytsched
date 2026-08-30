# TODO-085 verifier 報告

## mise チェック

- `mise run fmt` — 通過（ruff format: 35 files unchanged / ruff check: All checks passed / prettier: unchanged）
- `mise run typecheck` — 通過（basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success, no issues found in 32 source files）
- `mise run lint` — 通過（eslint も無警告）
- `mise run test` — 通過（525 passed in 102.93s。`test_trash.py` は 7 件）

## アプリ起動と HTTP での実地確認

`uv run ytsched webapp --port 18765 --datadir <一時ディレクトリ>` を
`run_in_background` で起動し、curl の POST（`cmd=add`/`del`/`fix`）で確認した。

- 追加だけでは `trash.jsonl` は作られない（○）
- 削除すると `trash.jsonl` に 1 行増え、消した予定の内容（`sde_id`・
  日時・タイトル「検証用予定1」・場所「会議室」等）と一致（○）
- `fix`（編集）すると、**編集前**の内容（「編集前タイトル」）がゴミ箱に
  入り、編集後の内容（「編集後タイトル」）は元のファイルにのみ残る（○）
- ToDo（`sde_type=□`、`date` が None のファイル `ToDo.jsonl`）を削除
  すると、ゴミ箱に入り、`ToDo.jsonl` からは正しく消える（○）
- 3 回の操作（del → fix → ToDo del）でゴミ箱の行が 3 行まで積み上がり、
  既存の行は消えていない（○）
- `trash.jsonl.bak` は作られない（○。データディレクトリ直下に `trash.jsonl`
  のみ存在。予定ファイル自体の `.bak`（例: `30.jsonl.bak`）は既存仕様どおり
  発生するが別物）
- 日本語（「検証用予定1」「会議室」「編集前タイトル」など）はエスケープ
  されずそのまま UTF-8 で書かれている（○）
- サーバログ（`server.log`）に例外・トレースバックなし

## 文書との突き合わせ

- `docs/data-format.md` の「ゴミ箱（TODO-085）」の記述（追記のみ・`.bak`
  なし・`SchedData.del_sde()` の 1 か所で削除と編集の両方をカバー・
  1 行の形）は、実装（`src/ytsched/trash.py`・`ytsched.py` の
  `del_sde()`）と食い違いなし
- `src/README.md` の `trash.py` の説明も内容と一致

## 既存テストが実データを汚さないか

- `tests/test_trash.py` は全テストで `tmp_path` を使用
- `tests/helpers.py` の `make_app(datadir)` は呼び出し元が渡す `datadir`
  をそのまま `SchedData` へ渡すだけで、実データディレクトリへのハード
  コードは無い
- `tests/test_ytsched.py` の `SchedData("~/data")` は
  `monkeypatch.setenv("HOME", str(tmp_path))` により `~` が一時
  ディレクトリへ展開されるため、実データを汚さない

## 見つかった不具合

なし。仕様（1〜4）どおりに動作していることを確認した。
