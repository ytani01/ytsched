# TODO-083 reviewer 報告

## やったこと

- `git show HEAD:src/ytsched/webroot/static/js/my.js` で元の 1,399 行を
  取り出し、新しい 7 本（`state.js` / `spinner.js` / `gauge.js` /
  `nav.js` / `week.js` / `keyboard.js` / `swipe.js`）を `base.html` と
  同じ順で結合し、`ytState.xxx` → `xxx` に機械的に戻したうえで
  `diff -u` を取った。差分はファイル冒頭のヘッダコメントと、
  `let elLoadingSpinner;` などの宣言が `ytState = {...}` に変わった
  部分だけで、**関数・定数の中身は 1 バイトも変わっていない**ことを
  確認した
- `main-page.js` は結合対象に入らないので、`homeButtonHdr` /
  `onloadHdr` / `changeSearchN` を旧 `main.html` の該当部分と
  1 行ずつ突き合わせた。`search_str0` と `search_str`
  （検索モードの判定値と入力欄の値）の取り違えは無い。
  `cur_day.value` → `document.getElementById("cur_day").value` も
  等価
- `window.addEventListener` の総数を数えて突き合わせ
  （旧: `my.js` 2 件 + `main.html` 10 件 = 12 件、
  新: `main-page.js` 10 件 + `keyboard.js` 1 件 + `spinner.js` 1 件
  = 12 件、一致）
- 7 本 + `main-page.js` の間でトップレベルの `const`/`let` 宣言に
  重複が無いことを確認（同じ識別子を 2 か所で宣言すると
  `SyntaxError` になるため）
- `base.html` の読み込み順（`state` → `spinner` → `gauge` → `nav` →
  `week` → `keyboard` → `swipe`）と、`main-page.js` が `base.html` に
  入っていないことを確認
- `edit.html` の `elLoadingSpinner = ...` → `ytState.elLoadingSpinner
  = ...` の 1 か所以外に、`elMain` / `elGaugeR0` / `elWeekWrap` /
  `activeWeekOffset` の生の参照が残っていないことを確認
- `src/README.md` / `docs/Developer.md` / `tests/README.md` の
  `my.js` への言及が新しい構成に合わせて更新されていることを確認

**挙動が変わっている箇所は見つからなかった。**

## 指摘（確信度は高いが、実害の小さいもの）

### 1. コメントに `my.js` への言及が 2 か所残っている（直したほうがよい）

- `src/ytsched/webroot/templates/main.html:28`
  「`mouseDownHdr()/mouseUpHdr() (my.js)` にドラッグと…」— この関数は
  今 `swipe.js` にある。`main.html` 自体はこの項目で直接編集した
  ファイルなので、ここだけ直し忘れたと見える
- `src/ytsched/webroot/static/css/my.css:868`
  「位置調整は `my.js` の `followKeyboard()` が…」— 今は
  `keyboard.js`。このファイルは今回触っていないが、`my.js` という
  ファイル名自体が無くなったので古い記述になった

どちらも動作に影響しない、コメントだけの話。

## 気になったが確信度が低いもの

- `activeWeekOffset` の宣言に付いていた「いま見ている週が、最初に
  描かれた週から何週ぶん離れているか (TODO-069)。``.my-week-panel``
  の ``data-offset`` と同じ数え方で、読み込んだ直後は 0」という
  説明コメントが、`state.js` へ移すときに消え、5 つ共通の 1 行コメント
  だけになっている。挙動には関係ないが、この変数だけ他の 4 つより
  意味が分かりにくいので、残すかどうかは判断が要るところ

## 判断が要る点

- 上の「コメント 2 か所」を直すかどうか（動作に影響しないので、
  この項目の範囲でやるか、次の文書整合の項目に回すかは main の判断）
