# TODO-107 implementer 報告

## 実施済み

- `state.js` で `window.ytsched` と `ytState` を作成した。
- `spinner.js`、`nav.js`、`gauge.js`、`week.js`、`keyboard.js`、
  `edit-page.js` の一部または全部で、ファイル間で使う関数・状態を
  `window.ytsched` 経由に変更した。
- `base.html` と `main.html` のテンプレート値を
  `window.ytsched` の下へ置く変更を入れた。
- `nav.js` と `week.js` は、`no-undef` と `no-unused-vars` を一時的に
  有効にした ESLint 実行でエラーが無いことを確認した。

## 未実施

- `swipe.js` と `main-page.js` の残りの公開名への移行。
- 全テンプレートのインラインイベント追随、ブラウザテスト、
  `eslint.config.js`、`src/README.md` の更新、pageerror テスト。
- `mise run lintjs` とブラウザテストの実行。

## 停止理由

作業時間内に一貫した移行と全体確認まで完了できなかった。中途変更が
共有作業ツリーに残っているため、続きの担当者は現在の diff を確認して
から実装を再開する必要がある。
