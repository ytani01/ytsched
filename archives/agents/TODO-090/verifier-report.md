# TODO-090 verifier 報告

## 1. 静的チェック / テスト

- `uv run ruff format --check src tests` → `28 files already formatted`（○）
- `uv run ruff check` → `All checks passed!`（○）
- `uv run basedpyright` → `0 errors, 0 warnings, 0 notes`（○）
- `uv run mypy src` → `Success: no issues found in 14 source files`（○）
- `uv run pytest -q` → `480 passed in 66.78s`（○）

## 2. アプリの起動確認

`uv run ytsched webapp --datadir <一時dir> --port 18765` を
`run_in_background` で起動。

- `curl http://localhost:18765/ytsched/` → 200（○）
- `curl http://localhost:18765/ytsched/edit` → 200（○）
- どちらも `grep -c '{{\|{%'` が 0（テンプレートは展開済み）（○）
- `curl "http://localhost:18765/ytsched/?search_str=hello"` 後、
  `conf.json` に `{"SearchStr": "hello"}` が書かれた（○）
- `conf.json` を外部から `{"SearchStr": "外部から書き換え"}` に書き換え、
  `mtime` をずらしてから `/ytsched/` を取得すると、応答 HTML に
  「外部から書き換え」が出た（キャッシュが追随、○）
- `?search_str=aaa&filter_str=bbb&todo_days=3` を 1 回 GET すると、
  `conf.json` の `mtime` が 1 回だけ変わり、3 つの値がまとめて
  書かれていた（`{"SearchStr": "aaa", "FilterStr": "bbb", "ToDo_Days": "3"}`）。
  書き込み回数そのものは `strace`/`inotifywait` 無しでは数えられないが、
  自動テスト `test_conf_write_happens_once_per_request`
  （`ConfFile._save` を mock で監視）で 1 回だけ呼ばれることを別途確認済み
  （pytest 通過。1. 節参照）
- 予定の追加（`cmd=add`）→ `<datadir>/2026/08/28.jsonl` に新しい行が
  書かれた（○）
- 修正（`cmd=fix`、同じ `sde_id`）→ 同じ行の内容（時刻・タイトル）が
  書き換わった（○）
- 削除（`cmd=del`）→ 該当ファイルが空になった（○）
- サーバのログ（標準出力）に例外・トレースバックなし
  （`grep -i "error\|traceback\|exception"` で 0 件）

起動していたプロセスは確認後に kill 済み。`pgrep -af "ytsched webapp"` で
残存なしを確認。

## 3. 新しいテストが実際に落ちるか

- `src/ytsched/conf.py` の `refresh()` から `if self._dirty: return` を
  一時的に外すと、`test_conf_keeps_unsaved_changes` が
  `AssertionError: assert '30' == '7'` で失敗（期待どおり）。
  `\cp` で元に戻し、`git diff` が無いこと・15 件 pass を確認
- `src/ytsched/ytsched.py` の `get_sdf()` から
  `date not in self._dirty_sdf and` を外すと、
  `test_get_sdf_does_not_reload_dirty_day` が
  `assert sdf2 is sdf1` の `AssertionError` で失敗（期待どおり）。
  `\cp` で元に戻し、`git diff` が無いこと・1 件 pass を確認

（`test_conf_reloads_when_file_changed_outside` /
`test_conf_write_happens_once_per_request` /
`test_update_conf_args_returns_and_saves_all_four` は、依頼どおり
1〜2 個で足りると判断し、意図的には壊していない）

## 見つかった不具合

なし。

## 判断が要る点

なし。実装報告に書かれていた `conf_round_trip` 系テストの作り替え・
`ruff format` の巻き込みは、implementer 側の報告どおりで実害を確認できず、
main の判断が必要な新たな論点は無い。

## 追加の修正の確認（reviewer 指摘への対応：`save_if_dirty()` の `OSError` 処理）

### 1. 静的チェック / テスト

- `uv run ruff format --check src tests` → `28 files already formatted`（○）
- `uv run ruff check` → `All checks passed!`（○）
- `uv run basedpyright` → `0 errors, 0 warnings, 0 notes`（○）
- `uv run mypy src` → `Success: no issues found in 14 source files`（○）
- `uv run pytest -q` → `481 passed in 62.57s`（テストが 1 件増えて 481 件。○）

### 2. 書き込み失敗時の挙動（アプリを実際に起動して確認）

一時ディレクトリで `uv run ytsched webapp --datadir <一時dir> --port 18766` を
起動し、まず 1 回検索して `conf.json` を作らせたあと、
`chmod 400 <datadir>/conf.json`（ディレクトリ自体も 500 にした）で
書けない状態にした。

- 書けない状態で `?search_str=bbb` を送ると **200** が返り、
  サーバのログに
  `WARNING conf.py:191 save_if_dirty()> …/conf.json: [Errno 13] Permission
  denied: … .. not saved` が 1 行出た（○）
- そのまま続けて 4 回リクエスト（検索語を変えて 3 回＋`/ytsched/edit` 1 回）
  しても、すべて 200 が返り続けた。検索語を変えたときだけ
  `WARNING` がその都度出て（＝止まらずに毎回書き込みを試みて失敗するだけ）、
  `edit`（変更なし）では出なかった（○、依頼の「画面が出続けること」を満たす）
- `chmod 600 conf.json` / `chmod 700 <datadir>` で書ける状態に戻し、
  `?search_str=recovered` を送ると `conf.json` の中身が
  `{"SearchStr": "recovered"}` に書き換わった（`_dirty` が `True` のまま
  止まっていないことを確認。○）

確認後、サーバは kill 済み、`chmod` も元（600/700）に戻し、
一時ディレクトリは削除していない（次の確認に影響しない場所のため）。

### 3. 足されたテストが壊れると落ちるか

`save_if_dirty()` の

```python
try:
    self._save()
except OSError as e:
    self.__log.warning(f"{self.pathname}: {e} .. not saved")

self._dirty = False
```

を、`try`/`except` を外して `self._save()` を直接呼ぶ形に一時的に変更。
`uv run pytest tests/test_handler.py -k conf_save_failure` を実行すると、
`test_conf_save_failure_does_not_break_next_request` が
`PermissionError: denied`（mock の `side_effect`）が外へ漏れて失敗した
（期待どおり）。`\cp` で元に戻し、`git diff --stat src/ytsched/conf.py` が
無いこと、`pytest -k conf`（16 件）が全パスすることを確認済み。

見つかった不具合・判断が要る点はなし。
