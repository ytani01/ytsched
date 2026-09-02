# TODO-162 verifier 報告

## fmt / lint / test

- `mise run fmt` — 通過（ruff format 41 files unchanged / ruff check All
  checks passed）。実行後 `git status --short` で差分が増えていないこと
  も確認（フォーマット崩れ無し）
- `mise run lint` — 通過（prettier unchanged / eslint 0 件 / basedpyright
  0 errors / mypy Success, 38 files）
- `mise run test` — 通過（`607 passed in 154.91s`）

## アプリの起動・見た目

`--datadir /tmp/claude-649/ytsched-verify-datadir`（一時ディレクトリ）で
`uv run ytsched webapp` を起動。実データは使っていない。

- `curl -s -o /dev/null -w '%{http_code}'` → `200`
- ログに `traceback` / `error` / `exception` の出力なし
- 取得した HTML に `header_date` の出現無し（0 件）、`{{` / `{%` の
  生残りも無し
- ヘッダーの週バーから日付入力欄が消えていることをスクリーンショットで
  確認（`~/tmp/playwright-mcp/todo-162-header.png`）
- フッターのスクリーンショット（`~/tmp/playwright-mcp/todo-162-footer.png`）
  を保存。矢印・ホームボタンの位置を Playwright の `bounding_box()` で
  実測:
  - ハンバーガー右端 59.4px、ホーム左端 227.2px → 中間点 143.3px
  - back〜forward 全体の中心 145.3px（ハンバーガーとホームの中間との差
    2px、見た目上ほぼ中央）
  - back 右端 131.3px〜forward 左端 159.3px の間隔 28px（TODO-161 時点
    の 0.5em 相当の間隔より明確に拡大）
  - フッター行全体の中心 240px、ホームボタン中心 240px（TODO-161 の
    中央揃えは崩れていない）
- 週送りボタンの動作確認: `#forward_button` をクリックし
  `ytsched.ytState.activeMonday` が `2026-08-31` → `2026-09-07` に変化
  することを確認（週送りは機能している）
- 検索欄 `#search_str` に文字を入力し反映されることを確認（フォーム自体
  は壊れていない）

起動したプロセスは確認後に kill 済み（`pgrep -f "ytsched webapp"` で
プロセスが残っていないことを確認）。

## 問題点

見つからず。
