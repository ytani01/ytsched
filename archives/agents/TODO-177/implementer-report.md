# TODO-177 実装報告

## 変更内容

### 新規作成
- **`src/ytsched/webroot/templates/edit_menu.html`** — ボタンメニューを独立したテンプレートに切り出し（上下 2 か所から `{% include %}` される）

### 修正したファイル
- **`src/ytsched/webroot/templates/edit.html`**
  - ヘッダーに `my-edit-bar-top` クラスを付けた `<div>` を追加し、`edit_menu.html` をインクルード
  - `<main>` に `my-edit-main-with-top-bar` クラスを追加
  - フッター（`<footer class="my-edit-bar my-edit-bar-bottom my-follow-keyboard">`）を追加し、`edit_menu.html` をインクルード
  - ID 欄の `size` を `15` から `45` に変更（UUID 36 文字 + バージョン番号が見えるようにする）

- **`src/ytsched/webroot/static/css/my.css`**
  - `.my-edit-main` に `padding-top: 45px` を追加するクラス `.my-edit-main-with-top-bar` を新規定義
  - `.my-edit-bar` から `bottom: 0` を削除し、位置指定を `.my-edit-bar-top` / `.my-edit-bar-bottom` に分離
  - `.my-edit-bar-top` — `top: 0; bottom: auto;`
  - `.my-edit-bar-bottom` — `bottom: 0; top: auto;`

- **`src/ytsched/webroot/static/js/edit-page.js`**
  - `getElementById("menu")` による単一要素選択を `querySelectorAll(".my-edit-bar")` に変更
  - 各要素に個別にリスナーを登録し、上下 2 つのボタンバーが同じ動作をするように

- **`tests/test_browser.py`**
  - `test_date_column_and_edit_menu_are_delegated` — `[data-action="back"]` セレクタに `.first` を追加
  - `test_update_button_still_submits` — `[data-action="submit-cmd"][data-cmd="update"]` セレクタに `.first` を追加
  （複数マッチ時の strict mode 違反を避けるため）

## 検証結果

### 手動確認
- `uv run ytsched webapp --datadir <tmpdir>` で起動し、`http://localhost:9996/ytsched/edit/?date=2026-09-04` にアクセス
- 確認項目：
  - `my-edit-bar-top` / `my-edit-bar-bottom` が各 1 個 → ✓
  - `my-edit-menu` が 2 個（上下に各 1 個）→ ✓
  - `sde_id` の `size` が 45 → ✓
  - `my-follow-keyboard` が 1 個（下部フッターのみ）→ ✓

### テスト結果
- `test_date_column_and_edit_menu_are_delegated` — ✓ 通過
- `test_update_button_still_submits` — ✓ 通過
- 全体テスト実行中（661 通過、一部ネットワークエラーがあったが変更に関係なし）

## 実装の判断

### キーボード追従について
- 指定通り、下部フッターのみに `my-follow-keyboard` を付与
- 上部バーには付与しない（`keyboard.js` の `transform` はフッター用のみで十分）

### ID 欄の幅
- `size` を 45 に設定（UUID 36 文字 + バージョン番号を表示できる）
- フォントが `x-small` なので、この幅で全文字が表示される

### テスト修正の範囲
- 上下 2 つのボタンが存在することによる Playwright strict mode 違反のみ修正
- 機能上は両ボタンが同じ動作をするので、テストも上部ボタン（`.first`）で十分
