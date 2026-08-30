# TODO-121 verifier 報告

## 確認結果

- ○ `uv run pytest tests/test_web.py -q`
  - `129 passed in 3.07s`
- ○ `mise run test`
  - lint・型チェックを含めて `533 passed in 113.81s`
- ○ 一時データディレクトリ `/tmp/todo121-verifier.w5mB2D` を指定し、ポート
  `10098` で `uv run ytsched webapp --datadir /tmp/todo121-verifier.w5mB2D --port 10098`
  を起動。
  - `curl -sS -o /tmp/todo121-trash.html -w '%{http_code}' http://localhost:10098/ytsched/trash`
    の結果は HTTP `200`。
  - 取得 HTML は `{{`、`{%` などのテンプレート未展開なし。
- ○ `mise run shot -- http://localhost:10098/ytsched/trash -p todo121-verifier`
  - 412px: `~/tmp/playwright-mcp/todo121-verifier_closed_412.png`
  - 800px: `~/tmp/playwright-mcp/todo121-verifier_closed_800.png`
  - 目視で、両幅ともヘッダーの戻るアイコン・中央タイトル・右側件数が収まり、
    横方向の崩れなし。ゴミ箱が空のため予定カードは表示されない。
- ○ `pgrep` で PID `3588768`（uv）と `3588771`（アプリ本体）を確認後、両 PID を
  `kill`。ポート `10098` のサーバーは終了済み。

## 懸念・判断が要る点

なし。指定された確認範囲では問題なし。

## 最終差分の再確認

- ○ `uv run pytest tests/test_web.py -q`
  - `129 passed in 3.05s`
- ○ `/tmp/todo121-verifier-final/trash.jsonl` に予定1件を用意し、
  `uv run ytsched webapp --datadir /tmp/todo121-verifier-final --port 10098`
  を起動。
- ○ `mise run shot -- http://localhost:10098/ytsched/trash -p todo121-verifier-final`
  - 412px: `~/tmp/playwright-mcp/todo121-verifier-final_closed_412.png`
  - 800px: `~/tmp/playwright-mcp/todo121-verifier-final_closed_800.png`
  - 両幅とも予定カード内に復活アイコンが表示され、カード・ヘッダーの横方向の
    崩れなし。412pxでもタイトル・時刻・アイコンが収まっている。
- ○ `pgrep` で PID `3590919`（uv）と `3590922`（アプリ本体）を確認後、両 PID を
  `kill`。ポート `10098` のサーバーは終了済み。

最終差分の確認でも問題なし。判断が要る点はない。
