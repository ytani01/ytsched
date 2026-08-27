# TODO-089 verifier 報告

対象コミット前の作業ツリー（HEAD 43d43d2）。変更ファイル:
`edit.html` / `spinner.js` / `src/README.md`（M）、`edit-page.js`（新規）。

## 1. lint / typecheck — ○

- `mise run lint`: ruff format「30 files left unchanged」、ruff check「All checks passed!」
- `mise run typecheck`: basedpyright「0 errors, 0 warnings」、mypy「Success: no issues found in 27 source files」

## 2. test — ○

- `mise run test`: `482 passed in 60.65s`。既知の揺れ
  （`test_tap_again_stops_auto_page_turn`）を含め失敗なし。再実行不要。

## 3. アプリ起動・編集画面 — ○

- コマンド: `uv run ytsched webapp --datadir <mktemp -d>`（ポート 10085 で listen）
- `curl .../ytsched/static/js/edit-page.js` → **200**
- `curl .../ytsched/static/js/main-page.js` → **200**（退行なし）
- `curl '.../ytsched/edit?date=2026-08-28'` の HTML:
  - `{{ }}` / `{%` の生残りなし
  - `<script type="text/javascript" src="/ytsched/static/js/edit-page.js?v=...">` が `<body>` 内に入っている
  - 旧インラインの中身（`wdayList` / `function submitCmd` / `changeElDate` / `changeDetailHeight`）は HTML に残っていない
  - 冒頭に残るインラインは `const url_prefix = '/ytsched/';` のみ（テンプレートの値）
- サーバログ: `start server` の 1 行のみ。例外・トレースバックなし
- kill 済み。ポート 10085 解放を確認

## 4. 字句一致 — おおむね一致。ただし依頼書に無い並べ替えが 1 件

`git show HEAD:src/ytsched/webroot/templates/edit.html` のインライン `<script>` を
取り出し、依頼書の許容差分（先頭コメント追加 / `onloadHdr`→`onloadEdit` の 2 か所 /
コメントアウト `resize` リスナー削除 / `rotationchange` リスナー削除 / 4 スペース
デデント・行末スペース除去）を適用して `edit-page.js` と diff。

- 関数・定数の**本体は全て一致**。
- **依頼書に挙がっていない差分が 1 件**: `const onloadEdit = (event) => {...}` の
  定義位置が、`window.addEventListener('load', function() { changeDetailHeight(); })`
  の**前**へ移動している（旧は後ろ）。あわせて 2 つの `load` リスナー登録の間に
  あった空行が消えている。
  - `load` リスナーの登録順（changeDetailHeight → onloadEdit）は保たれており、
    `onloadEdit` は両方の登録より前で定義されるため、**挙動への影響は無い**。

## main の判断が要る点

- 項目 4 の並べ替え（`onloadEdit` 定義位置の移動）は挙動に影響しないが、
  依頼書の「本体に変更が無いこと／許容差分だけ」に対する逸脱。
  このまま許容するか、旧の位置へ戻させるか。
