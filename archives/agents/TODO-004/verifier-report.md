# TODO-004 verifier 報告

implementer 報告（`archives/agents/TODO-004/implementer-report.md`）を
読んだうえで、依頼の 9 項目を実際に手を動かして確認した。

## 1. git diff / git status

```
git status
git diff --stat
```

- `pyproject.toml`、`src/ytsched/*.py`（8 ファイル）、`tests/*.py`
  （5 ファイル）が modified。`mise.toml` と `archives/agents/TODO-004/`
  が untracked。
- 変更ファイルの一覧・件数は報告の「変更・作成したファイル」と一致
  （`src/ytsched/` は `__init__.py` を含めて 8 ファイル、報告本文の
  「7 ファイル」という書き方とは 1 つずれるが、後段の整形結果の
  一覧では `__init__.py` も挙げられており実質一致。数え方の揺れのみ）。

## 2. `uv run pytest tests`

```
$ uv run pytest tests
...
collected 161 items
...
============================= 161 passed in 2.89s ==============================
```

報告どおり 161 件全件通過。○

## 3. 78 文字超の行

```
$ awk 'length > 78 {print FILENAME":"FNR": "length}' \
    src/ytsched/*.py tests/*.py
```

出力なし（0 件）。報告と一致。○

## 4. `mise tasks`

```
$ mise tasks
build           build
installmise     install mise
installuv       install uv by mise
lint            linting
test            test
upgradeapt      upgrade apt packages
upgrademise     upgrade mise
upgradeproject  upgrade in this project
upgradeuv       upgrade uv
```

依頼の 7 タスク（`upgradeapt` / `upgrademise` / `upgradeuv` /
`upgradeproject` / `lint` / `test` / `build`）はすべて存在する。
`installmise` / `installuv` は報告どおりユーザーのグローバル設定由来
（`mise.toml` には無い）。○

## 5. `mise run upgradeproject`

正常終了を確認。`rm -f uv.lock` → `uv sync` → `uv pip install -U -e .`
→ `uv pip install -U --group dev -e .` → `uv run ytsched --help` の順に
実行され、最後に `ytsched` の Usage（`webapp` / `x-data1` サブコマンド）
が表示された。○

## 6. `mise run lint`（depends の並び）

`mise.toml` を読み、依頼された確認を行った。

- `upgradeproject` → `lint`（`depends = ["upgradeproject"]`）
  → `test`（`depends = ["lint"]`） → `build`（`depends = ["test"]`）
  の並びを確認。報告どおり。○
- `mise run lint` を実行すると、`ruff format` → `ruff check --fix
  --extend-select I` の順に走り、`ruff check` が **97 件のエラーで
  `[lint] ERROR task failed`** となって終了。basedpyright / mypy には
  到達しない。既知の状態として問題視しない。○（想定どおり）

## 7. `uv run mypy src tests` / `uv run basedpyright src tests`

```
$ uv run mypy src tests
...
Found 35 errors in 5 files (checked 13 source files)
```

```
$ uv run basedpyright src tests
...
28 errors, 2 warnings, 0 notes
```

報告にある「mypy 35 件」「basedpyright 28 errors, 2 warnings」と
件数が完全に一致。出力されたエラー箇所（`ytsched.py` の implicit
Optional 群、`main_handler.py:458` の `-> (datetime.date, str)`、
`edit_handler.py:77` の `get_argument` オーバーロード不一致、
`tests/test_ytsched.py` の None 引数、basedpyright だけが出す
`ytsched.py:189/191` の `join()` と `309/402` の `reportUnreachable`
warning）も報告の記載と一致した。○

## 8. webapp の起動確認

一時ディレクトリを `--datadir` に指定し、implementer が使った 10099 を
避けて **10098** で起動。

```
$ uv run ytsched webapp --datadir <tmp> --port 10098 &
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:10098/ytsched/
200
```

ログ（stdout/stderr）には
`05:26:24 INFO webapp.py.WebServer.main:129> start server: run forever ..`
のみで、例外・トレースバックは出ていない。

確認後、`pgrep -af` で PID を確かめてから `kill` でプロセスを停止した
（一度 kill 済みの PID を再度 kill しようとして「そのようなプロセス
はありません」と出たが、これは kill が既に成功していたための表示で
問題ではない。停止後に残っていたのは自分自身の確認コマンドの文字列を
`pgrep -af` が拾っただけで、webapp プロセスは残っていない）。○

## 9. pyproject.toml / mise.toml の tmr との比較

`pyproject.toml`:

- `python_version = "3.14"`（tmr は `"3.13"`）— 報告どおり
- `[[tool.mypy.overrides]]` の `module` が
  `"click,tornado,tornado.*,pytest,pytest.*"` になっており、tmr の
  `blessed` / `loguru` 系は含まれていない — 報告どおり
- `[tool.basedpyright]` は tmr と同一内容（tmr 側にあった行末の
  余分な空白は無い） — 報告どおり
- `[tool.ruff]` セクションは存在しない — 報告どおり

`mise.toml`:

- コマンド名が `uv run ytsched --help`（tmr は `uv run tmr -V`）に
  なっている点、全 4 か所（`upgradeproject` / `lint` / `test` /
  `build`）すべてで統一されていることを確認 — 報告どおり
- tmr の `upgradeproject` にあった
  `# uv pip install -U --group samples -e .`、`lint` 各行末尾の
  `# samples`、末尾の `[tasks.testpypi]`（コメントアウト）は
  ytsched の `mise.toml` に存在しない — 報告どおり

## まとめ

依頼した 9 項目すべてで、報告の内容と実際の挙動が一致した。
不具合は見つからなかった。
