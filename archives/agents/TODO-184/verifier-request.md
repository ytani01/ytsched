# TODO-184 確認依頼（verifier）

## 対象

作業ツリーの未コミットの変更（`git diff`）。
`src/ytsched/webroot/static/js/main-page.js` と `week.js`。
背景は TODO.md の TODO-184 と `archives/agents/TODO-184/implementer-request.md`。

## やること

1. `mise run fmt` / `mise run lint` / `mise run typecheck` / `mise run test` を走らせ、
   出力をそのまま報告する
2. アプリを起動して、一覧画面が出ることを確かめる。
   **`--datadir` に必ず一時ディレクトリを指定する**（実データを汚さない）
3. 依頼の 1〜5 が入っているかを diff で確かめる
   - `fillMainHeight()` が測る前に `minHeight` を空へ戻しているか
   - `setActiveWeek()` の呼び出しが `scrollToId()` の**あと**か
   - `resize` / `orientationchange` に登録されているか
   - `onloadHdr()` の分かれ方（短いときは visible → dispGauge → return、
     長いときは scrollToDate を通る）が変わっていないか
4. ブラウザでの見た目の確認までは求めない（手元で再現しにくいため）。
   できる範囲でよい

コードは直さないこと。見つけたことは報告するだけ。

## 報告

`archives/agents/TODO-184/verifier-report.md` に書く。返事は 5 行以内。
