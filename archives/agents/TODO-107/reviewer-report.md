# TODO-107 reviewer 報告

## 指摘

無し。

## 確認したこと

- `base.html` は `window.ytsched` と `url_prefix` を作成してから
  `state.js`、依存先となる各スクリプトを順に読む。前方参照がある
  `gauge.js` と `nav.js`、`nav.js` と `week.js` は、いずれも後から起きる
  イベント処理で参照するため、この順序で問題ない。
- ファイル間で使う関数・状態、テンプレートのインラインイベント、
  `page.evaluate()` の参照は `window.ytsched` に揃っている。イベント委譲への
  変更は含まれず、TODO-108 の範囲を越えていない。
- `eslint.config.js` から `no-undef` と `no-unused-vars` の無効化を除き、
  `mise run lintjs` が成功した。
