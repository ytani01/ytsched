# writer 報告（TODO-139）

`src/README.md` を、TODO-139 の実装（未コミット）に合わせて直した。

## 確かめた方法

- `git diff` で `trash.py` / `trash_handler.py` / `trash.html` の変更内容を読んだ
- `cat` で新規の `src/ytsched/webroot/static/js/trash-page.js` を読んだ
- `ls` で `webroot/templates/` と `static/js/` の実際のファイル一覧を確かめた

## 直したところ

- モジュール一覧の `trash.py` / `trash_handler.py` の 1 行説明を、
  削除・全消去（`delete()`/`clear()`）と、ハンドラ側の削除・空にするに
  合わせて更新
- `webroot/templates/` の一覧コメントに抜けていた `trash.html` を追加
- `static/js/` の本数を 10 本 → 11 本に修正し、
  「ブラウザ側のスクリプト」節の表に `trash-page.js` を追加。
  `base.html` が読む本数の説明と、`main-page.js`/`edit-page.js` の
  自前読み込みの説明を `trash-page.js` を含めた形に直した。
  `trash-page.js` の中身（`data-confirm` を持つ `<form>` の送信に
  `confirm()` をはさむだけ）も一言添えた
- モジュール一覧の直後（CLI の説明の後）に、`TrashFile.delete()`/
  `clear()` が全件書き直しをすること、`SchedDataFile` と違って
  `.bak` を作らないこと（ゴミ箱のゴミ箱になって意味が無いため）を
  短く足した

## 判断が要る点

特になし。
