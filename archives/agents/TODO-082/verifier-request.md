# TODO-082 verifier への依頼

implementer が TODO-082 を実装した。**コードは直さず**、確かめて報告する。

- 依頼書: `archives/agents/TODO-082/implementer-request.md`
- 実装の報告: `archives/agents/TODO-082/implementer-report.md`
- 項目: `TODO.md` の TODO-082

変更は `git diff` で見られる（まだコミットしていない）。

## 確かめること

1. `mise run lint` と `mise run test` が通る（出力をそのまま報告）
2. `uv run ytsched --help` / `webapp --help` / `migrate --help` が出て、
   `x_data1` が消えていること、`musicbox` や `sample package` といった
   別プロジェクトからの写しの文字列が残っていないこと
3. `ytsched migrate` が tornado を読み込まないこと。
   `uv run python -c "import sys; from ytsched.migrate import Migrator; print('tornado' in sys.modules)"`
   が `False`
4. **ruff の設定を移す前後で結果が変わっていないこと。**
   `pyproject.toml` の `line-length` / `extend-select` が実際に効いて
   いるか。`git stash` などは使わず、たとえば 79 文字の行を含む一時
   ファイルを作って `uv run ruff format --check` / `uv run ruff check`
   に掛け、`line-length 78` と import 並べ替え（`I`）が当たることを
   確かめる（確かめたら一時ファイルは消す）。
   `mise.toml` と `docs/Developer.md` からオプションが消えていること
5. `--size_limit` の既定値が変わっていないこと
   （`WebServer.DEF_SIZE_LIMIT` が `100 * 1024 * 1024` と同じ値か）
6. アプリが起動して週表示が出ること。**`--datadir` には必ず一時
   ディレクトリを指定する**（`~/ytsched/data` を汚さない）。
   `curl` で `/ytsched/` が 200 を返すところまで
7. 消した属性（`HandlerBase._app` / `_req`、`SchedDataFile.filename` /
   `dirname`）と `x_data1` / `DataFileApp` への参照が、`src` `tests`
   `tools` `docs` `*.md` のどこにも残っていないこと
8. `CONF_KEY_TODO_DAYS` / `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` が
   `MainHandler` にあり、`CONF_KEY_SEARCH_STR` は `HandlerBase` に
   残っていること。`EditHandler` が壊れていないこと
9. `src/README.md` の記述が実装と合っていること

## 報告

`archives/agents/TODO-082/verifier-report.md` に書く。
**直さずに、見つけたことを報告する。** 返事は 5 行以内で。
