# TODO-064 verifier 再確認（reviewer 指摘対応後）

対象: `my.js` の `mouseDownHdr` / `mouseUpHdr` の修正のみ。

## 1. lint / typecheck / test / node --check

- `mise run lint` — ○ ruff format 25 files unchanged、ruff check All checks passed
- `mise run typecheck` — ○ basedpyright 0 errors、mypy Success (22 files)
- `mise run test` — ○ 439 passed
- `node --check src/ytsched/webroot/static/js/my.js` — ○ 構文エラー無し

## 2. アプリ起動・ブラウザ操作（playwright, chromium）

`uv run ytsched webapp --datadir <mktemp -d> --port 18766` を起動（HTTP 200 確認）。
`page.mouse` で日付セル上を押し、指定 px だけ小刻みに動かしてから離す。

- ○ 30px 横に動かして離す → 編集画面へ（`/ytsched/edit/?date=...`）
- ○ 10px 横に動かして離す → 編集画面へ
- ○ 59px 横に動かして離す → 編集画面へ
- ○ 200px 横に動かして離す → 週送り（次週）、編集画面へは行かない
- ○ 縦に 100px 動かして離す → 編集画面へ（意図どおりクリック扱い）
- ○ 動かさずクリック → 編集画面へ（回帰なし）
- ○ 200px 左ドラッグ → 次週、200px 右ドラッグ → 前週（回帰なし）
- △ 「窓の外で mouseup を出さずに離した状況」の完全な再現は headless
  chromium ではできなかった（OS レベルで mouseup が別ウィンドウへ配送される
  状況を作れない）。近似として、ドラッグ開始 → `mouse.up()` → 再読み込み →
  動かさずクリック、という手順で試したところ 1 回目から正しく編集画面へ
  遷移した（`mouseDownHdr` 先頭の後始末が効いている）
- コンソールエラー・例外・サーバログのトレースバック無し

## 後片付け

`kill` でサーバプロセスを終了、`ss -ltnp` でポート 18766 が空いていることを確認。
