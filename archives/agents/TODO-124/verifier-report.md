# TODO-124 verifier 報告

## 対象diff
`git diff HEAD -- src/ytsched/webroot/templates/main.html` は 1 行削除のみ。
```
-          ゴミ箱
```
他の変更なし（依頼通り）。

## 1. lint / test

- `mise run lint` → ○（ruff format/check、eslint、basedpyright 0 errors、mypy Success）
- `mise run test` → ○ 536 passed in 125.99s（exit code 0）

## 2. 「ゴミ箱」文字列の grep

`grep -rn "ゴミ箱" src/ tests/` の結果、main.html のフッタ文字列を期待する
テスト・実装は無し。ヒットはすべて別画面・コメント由来:
- `src/ytsched/webroot/templates/trash.html:11` — ゴミ箱画面自体のタイトル（対象外）
- `src/README.md`, `src/ytsched/trash.py`, `trash_handler.py`, `ytsched.py`,
  `icons.svg`, `my.css` のコメント／説明文
- `tests/test_trash.py`, `tests/test_web.py` の docstring・コメント

## 3. アプリ起動確認

- `uv run ytsched webapp --datadir <一時ディレクトリ> --port 18124` を
  バックグラウンド起動
- `curl -s -o top124.html -w "%{http_code}"` → **200**
- 取得した HTML 中のフッタの trash リンク:
  ```html
  <a class="my-btn" href="/ytsched/trash">
  <svg class="my-icon my-icon-xl align-middle">
  <use href=".../icons.svg?...#trash"></use>
  </svg>
  </a>
  ```
  「ゴミ箱」の文字列は無く、アイコンのみ。リンク（`href="/ytsched/trash"`）は残存。
  `{{ }}` / `{%` の生残りなし（テンプレート展開は正常）
- サーバログに error / traceback / exception なし
- 確認後、PID (3654383, 3654386) を kill 済み。`pgrep -af "ytsched webapp" | grep 18124` で残プロセス無しを確認

## 判断が要る点
なし。すべて完了条件を満たしている。
