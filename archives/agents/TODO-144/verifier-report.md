# TODO-144 verifier 報告

## 確認結果

- `uv run pytest -q` → ○ 589 passed in 155.00s
- `uv run ruff check` → ○ All checks passed!
- `uv run ruff format --check` → ×（今回の変更に起因、既存の
  `archives/todo/*.md` 未整形は無関係）。**`tests/test_web.py` の
  変更した 2 行が unformatted** と出る（199〜200 行目、211〜212 行目の
  `assert re.search(...)` が 88 桁を超えている）。ruff format を掛けると
  複数行に折り返される
- `uv run basedpyright` → ○ 0 errors, 0 warnings, 0 notes
- `uv run mypy src tests tools` → ○ Success: no issues found in 35 source files

## アプリ起動確認

一時ディレクトリ（`/tmp/.../scratchpad/ytsched-datadir`）を `--datadir` に
指定して起動、`http://127.0.0.1:18844/` に対し確認。

- `curl -s -o /dev/null -w "%{http_code}"` → `200`
- ゴミ箱リンク内の件数: `<span class="my-fs-medium align-middle">\n0</span>`
  → カッコ無し・クラスは `my-fs-medium`（期待通り）
- `trash.jsonl` に `trashed_at` を持つ行を 3 件追記 → 再取得すると
  件数が `3` に変化（期待通り）
- フッター上段の `cache_size` 表示: `<span class="my-fs-xx-small">\n(99)</span>`
  → カッコ付き・`my-fs-xx-small` のまま。**変わっていない**（期待通り）
- 配信 CSS（`/ytsched/static/css/my.css`）に
  `.my-bar a.my-btn { color: white; text-decoration: none; }` が入っている
  ことを確認
- サーバログ（`webapp.log`）に Traceback / ERROR / CRITICAL は無し
  （`grep -c` で 0 件）
- 確認後、プロセスを `kill` し、`pgrep -fa "ytsched webapp"` で
  残っていないことを確認済み

## main の判断が要る点

- `ruff format --check` が `tests/test_web.py` の変更 2 行を
  unformatted と検出する。`ruff format` を実行して整形するかどうかは
  main の判断待ち
