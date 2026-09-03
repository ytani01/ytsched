# TODO-166 verifier report

## 静的チェック

- `uv run ruff format --check src/ytsched/main_binder.py src/ytsched/main_view.py tests/test_main_handler.py tests/test_web.py` — ○（4 files already formatted）
  - リポジトリ全体に `--check` を掛けると `archives/todo/` 配下の 10 ファイルが未整形と出るが、これは本件と無関係な既存差分（implementer-report にも記載あり）
- `uv run ruff check` — ○（All checks passed!）
- `uv run basedpyright` — ○（0 errors, 0 warnings, 0 notes）
- `uv run pytest -q` — ○（619 passed in 183.25s）

## アプリの起動確認

一時ディレクトリ（`/tmp/.../ytsched-verify/datadir1`）を `--datadir` に指定し、
`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18801` を起動して確認。

`conf.json` の値は文字列で書く必要がある（`docs/User.md` の記述どおり）。
数値そのまま（`{"LoadMonthPages": 0}`）を試したところ `not a string ..
ignored` の警告になり既定へ落ちた（仕様どおりの挙動で、バグではない）。

`?view=month` の `data-block="` の個数:

| `LoadMonthPages` | 結果 | 期待 |
|---|---|---|
| 未設定（`{}`） | 5 | 5 |
| `"0"` | 1 | 1 |
| `"10"` | 21 | 21 |
| `"11"`（範囲外） | 5 + 警告ログ | 5 + 警告ログ |
| `"-1"`（範囲外） | 5 + 警告ログ | 5 + 警告ログ |
| `"abc"`（数字でない） | 5 + 警告ログ | 5 + 警告ログ |

警告ログの実例:
```
convert_value()> LoadMonthPages='11': LoadMonthPages must be in 0..10, not 11 .. ignored
convert_value()> LoadMonthPages='-1': LoadMonthPages must be in 0..10, not -1 .. ignored
convert_value()> LoadMonthPages='abc': invalid literal for int() with base 10: 'abc' .. ignored
```

`?view=week`（`conf.json` を `{}` に戻した状態）— HTTP 200、
`my-week-panel`/`data-week` 系の要素あり、`{{`/`{%` の生残りなし、
`app1.log` に例外・トレースバックなし。`LoadMonths` 系の挙動には
影響していない。

起動したプロセスは `pgrep -f "ytsched webapp.*18801"` で PID を確認し、
`kill` で停止済み。

## 文書の確認

`src/README.md`・`docs/User.md`・`tests/README.md` の
「既定 2・範囲 0〜10・既定 5 ブロック＝30 ヶ月」の記述は、実測した
挙動と一致。`docs/User.md` のサンプル JSON も文字列表記になっており
実装と合っている。

## 見つかった問題

なし。
