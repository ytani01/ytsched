# TODO-106 implementer 報告

## 変更

- `src/ytsched/main_binder.py` を追加し、一覧画面のクエリ・フォーム引数、
  設定値、正規表現の解析と検証を `MainBinder` へ集約した。
- `src/ytsched/main_view.py` を追加し、ToDo・週間データ・月間カレンダーと
  テンプレート引数を `MainViewBuilder` へ分離した。
- `src/ytsched/main_handler.py` は GET/POST、更新コマンド、リダイレクトに
  絞った。既存の定数と `months2weeks()` は参照先を保つため残した。
- `tests/test_main_handler.py` は binder と `SchedLoader` を直接検証する形へ
  更新し、`src/README.md` の構成説明を実装に合わせた。

## 確認

- `uv run pytest tests/test_main_handler.py tests/test_web.py -q`: 184 passed
- `mise run lint`: passed（basedpyright 0 errors、mypy 成功を含む）
- `uv run pytest tests/test_main_handler.py -q`: 57 passed
- `uv run pytest tests/test_main_handler.py tests/test_web.py -q`: 184 passed

## 判断

- Tornado の `get_argument()` の型定義と binder 用 Protocol の違いは
  `MainHandler.initialize()` の局所的な `cast(Any, self)` で吸収した。
  実行時に必要なメソッドは Protocol で限定している。
- テストで `MainHandler` を直接 binder に渡す箇所も、同じ型定義の違いを
  `cast(Any, handler)` で明示した。実行時のオブジェクトと挙動は変わらない。
