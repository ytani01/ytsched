# TODO-081 verifier 報告

## 1. mise run fmt / typecheck / lint / test

```
mise run fmt        → ruff format: 28 files left unchanged / ruff check: All checks passed!
mise run typecheck   → basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success: no issues found in 25 source files
mise run lint        → 上記 fmt + typecheck と同じ、Finished in 6.67s
mise run test        → uv run pytest tests: 475 passed in 51.68s
```

`tests/test_browser.py` も含めて実行され、19 件通っている
（collected 475 items の内訳に `tests/test_browser.py ...................  [4%]`）。

## 2. アプリの起動と URL 5 つ

```
uv run ytsched webapp --datadir <tmp> --port 18765
```
で起動し、例外なく `start server: run forever ..` を出力（PID 確認・
最終的に kill 済み）。

```
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18765/          → 200
curl ... /ytsched                                                          → 200
curl ... /ytsched/                                                         → 200
curl ... /ytsched/edit                                                     → 200
curl ... /ytsched/edit/                                                    → 200
```

`/` と `/ytsched/` の HTML を取得し `{{`・`{%` の残存を grep したが
0 件（テンプレートは展開されている）。`<title>Ytsched: ...</title>`
なども正しく出ている。

`webapp.py` の URL 登録を確認、5 か所すべてに `{"sd": self._sd}` が
渡っていることをソースで確認済み（`src/ytsched/webapp.py:84-88`）。
`handler.py` は `initialize(self, sd: SchedData) -> None` で
`self._sd: SchedData = sd` を設定し、`__init__` はもう `_sd` を
触っていない（`src/ytsched/handler.py:35, 67, 78`）。

## 3. 予定の追加・修正・削除（POST）

一時データディレクトリに対して実際に POST し、`.jsonl` の中身と
再表示ページの両方で確認した。

- **追加**（`cmd=add`）: 302 → `2026/08/27.jsonl` に
  `"title": "TestEvent"` が書かれた。再表示ページに `TestEvent` が
  出た
- **修正**（`cmd=fix`）: 302 → 同じ行が `"title": "TestEventFixed"`
  に書き換わった
- **削除**（`cmd=del`）: 302 → `2026/08/27.jsonl` の中身が空になった

いずれもサーバのログに例外・トレースバックは出ていない
（`grep -i "traceback\|exception\|error"` で 0 件）。

なお `sde_id` は空文字列でも明示的に渡す必要がある（渡さないと
`400 Missing argument sde_id`）。これは POST フォームの隠しフィールド
`sde_id`（追加時は空値、`readonly`）に対応する仕様どおりの挙動で、
今回の変更が原因ではない。

## 4. `convert_value()` の警告ログ

`GET /ytsched/?date=notadate` を叩くと 200 を返しつつ、ログに

```
08/27 21:37:30 ⚠️ WARNING handler_util.py:57 convert_value()> date='notadate': Invalid isoformat string: 'notadate' .. ignored
```

が 1 行出た。移す前と同じ「警告 1 行＋ `None` を返して無視」の挙動
（TODO-027・TODO-012）を維持している。

## 5. CLI の他コマンド

```
uv run ytsched --help          → Commands: migrate / webapp / x-data1 が表示される
uv run ytsched migrate --help  → 正常にヘルプが出る（handler.py を経由しない経路だが import の連鎖は確認できた）
```

## 見つかったこと

特に問題は見つからなかった。以下は判断材料として書いておく。

- `tests/test_webapp.py` は `Application.settings` から `sd` を
  外したことに対応して直っている（`mise run test` で 8 件パス）。
  内容は目視で軽く見ただけで、詳細な差分レビューはしていない
  （依頼の範囲を超えるため）
- `handler_util.py` の `_log = getLogger(__name__)` はクラスが無い
  モジュールとして妥当。`migrate.py` と同じ書き方になっていることを
  確認した

## 判断が要る点

なし。実装は依頼どおりに動作している。
