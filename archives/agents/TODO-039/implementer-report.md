# TODO-039 implementer 報告

## 変更したファイル

- `src/ytsched/webroot/static/manifest.json`（新規）依頼書どおりの内容
- `src/ytsched/webroot/templates/base.html`
  `<head>` に viewport の `interactive-widget=resizes-content`、
  `theme-color`・`mobile-web-app-capable`・
  `apple-mobile-web-app-capable`・`apple-mobile-web-app-status-bar-style`・
  `apple-mobile-web-app-title` の meta、`icon.svg`・
  `apple-touch-icon.png`・`manifest.json` へのリンクを追加。既存の
  favicon の行に `sizes="32x32"` を追加
- `src/ytsched/webroot/templates/edit.html`
  `#menu` に `my-follow-keyboard` クラスを追加
- `src/ytsched/webroot/templates/main.html`
  `#menu_bar` に `my-follow-keyboard` クラスを追加（`.my-bar-content`
  には付けていない）
- `src/ytsched/webroot/static/js/my.js`
  依頼書のコードそのまま（`followKeyboard()` と `visualViewport` の
  リスナー登録）を末尾に追加
- `src/ytsched/webroot/static/css/my.css`
  `.my-follow-keyboard` の空ルールと説明コメントを追加
- `tests/test_webapp.py`
  `test_manifest_and_icons_are_bundled`・`test_manifest_content` を追加
  （`import json` も追加）
- `tests/test_web.py`
  `TestManifestAndIcons` クラス（`test_manifest`・
  `test_apple_touch_icon`・`test_favicon`・`test_links_in_html`）を
  `TestMainHandler` の後、`TestInvalidArgs` の前に追加
- `README.md`
  「同梱しているライブラリ」の下に「スマホのホーム画面に追加する」の
  節を新設。アイコンが独自デザインで `tools/make-icons.sh` で作り直せる
  こと、`manifest.json` の `start_url` が相対で `--urlprefix` に付いて
  くることを短く書いた

## 自分で確かめたこと

- `mise run test`（`fmt` → `typecheck` → `lint` → `test` を含む）で
  418 件すべて通過（新規追加は 6 件。依頼書に「今 412 件通る」とあった
  分から一致）
- `ytsched webapp --datadir <一時ディレクトリ> --port 18765` で実際に
  起動し、curl で確認
  - `/ytsched/static/manifest.json` が 200、中身の `start_url` /
    `scope` が `../` になっている
  - `/ytsched/static/icons/apple-touch-icon.png`・`favicon.ico` が 200
  - `/ytsched/` の HTML に `theme-color`・`mobile-web-app-capable`・
    `interactive-widget=resizes-content`・`rel="manifest"`・
    `rel="apple-touch-icon"` が出ている
  - 確認後にサーバは停止済み（残存プロセス無しを確認）
- `visualViewport` を使ったキーボード追従は、iOS Safari の実機が
  手元に無いため**目視での動作確認はできていない**。コードは依頼書の
  指示どおりそのまま使い、ロジック（`vv.scale <= 1.01` の判定、
  `gap` の計算、`load`/`resize`/`scroll` の登録）を読んで妥当と判断した

## 単独で決めた判断

- `edit.html`・`main.html` のクラス属性の順番は依頼書に厳密な指定が
  無かったため、`my-follow-keyboard` を末尾に追記する形にした
  （既存のクラスの並びは変えていない）
- `base.html` の viewport の `content` 属性値を複数行に折り返した
  （長い属性値のため。他の属性でも同様の折り返しが既存コードにあり、
  書き方を揃えた）
- README の見出しは依頼書に案が無かったため「スマホのホーム画面に
  追加する」とした。既存の見出し（「同梱しているライブラリ」など）の
  文体に合わせた造語ではない一般的な言い回りのつもり

## 気づいたが直さなかったもの

- なし（依頼書の範囲はすべて対応済み）

## うまくいかなかったところ

- 特になし。iOS Safari の実機確認ができない点のみ上記に記載
