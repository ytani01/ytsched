# TODO-091 検証報告（verifier）

対象: `src/ytsched/{main_handler,sched_load}.py`、`webroot/templates/main.html`、
`tests/test_main_handler.py` の dataclass 化リファクタリング。

## 結果まとめ

すべて ○。挙動の変化・回帰は見つからなかった。

| 確認 | 結果 | 得られた値 |
|------|------|-----------|
| `mise run test` | ○ | 482 passed（約 60s） |
| `mise run typecheck` | ○ | basedpyright 0 errors / mypy Success（27 files） |
| `mise run lint` | ○ | ruff format 30 files unchanged / ruff check All passed |
| アプリ起動 | ○ | port 10085 で listen、起動ログのみ |
| `GET /ytsched/` | ○ | HTTP 200 |
| 検索モード `?date=2021-03-01&search_str=会議` | ○ | HTTP 200 |
| テンプレート展開 | ○ | `{{` `{%` の生残りゼロ（両ページ） |
| 版数の隣のキャッシュ件数 | ○ | `Version 0.5.3.dev6...` の直後に `(1)` |
| サーバログの例外 | ○ | トレースバック・例外なし |

## 使ったコマンド

```
mise run test
mise run typecheck
mise run lint
uv run ytsched webapp --datadir <tmp>            # port 10085
curl -s -o /dev/null -w '%{http_code}' http://localhost:10085/ytsched/
curl -s -o /dev/null -w '%{http_code}' 'http://localhost:10085/ytsched/?date=2021-03-01&search_str=会議'
```

一時 datadir・起動プロセスは後始末済み。作業ツリーは変更なし（TODO-091 の
4 ファイル + `archives/agents/TODO-091/` のみ）。

## main の判断が要る点（不具合ではない）

依頼書の確認 (c)「`data-offset=` を持つ `my-week-panel` の div が**複数**」は、
今回の環境では **1 個（`data-offset="0"` のみ）** しか出なかった。

- 原因は空の一時 datadir に `conf.json` が無いこと。`LoadMonths` が既定へ
  落ちず、`mk_weeks()` のループが `range(0, 1)` になり週パネルが 1 個になる。
- **回帰ではない。** `git stash` で HEAD（変更前）を別ポートで起動して
  同じ URL を叩いたが、変更前も `data-offset="0"` 1 個だけで出力は一致した。
- 複数週での属性参照（`w.offset` / `s.date` 等）は `mise run test` の
  482 件（`test_main_handler.py` / `test_web.py` / `test_browser.py`）が
  実テンプレートで通っているので確認できている。

判断: 上記は既存挙動で TODO-091 の範囲外。実データがあれば複数パネルになる。
