# TODO-226 reviewer 報告

対象: `git diff`（`src/ytsched/webroot/static/js/edit-page.js`、`docs/UsersGuide.md`）

## 要修正

無し

## 検討

無し

## 問題が無かった点

- 分岐: `key !== "Enter"` か `isComposing` なら何もしないので、Enter 単独の既定の動き（textarea の改行）は変わらない。Ctrl/Cmd のときだけ `preventDefault` するので、Ctrl+Enter で textarea に改行が入ることも無い
- Shift/Alt を一緒に押しても確定する。項目の範囲（Ctrl/Cmd+Enter）から外れず、困る組み合わせは見当たらない
- 登録先の `#input_form` に、入力欄はすべて入っている（date/time/type/title/place/detail/sde_id）。ボタンは focus できない `div` で、form の外にある。「どの欄でも」と食い違わない
- busyFlag: キーを押し続けて repeat が来ても、2 回目からは `submitCmd` の busyFlag で止まる
- detail の onchange（`update`）: `form.submit()` は blur を起こさないので change は出ない。仮に出ても busyFlag で止まり、`fix` だけが送られる。ボタンの mousedown と同じ順番になる
- 他の keydown: `keyHdr`（keyboard.js）を登録しているのは main-page.js だけで、edit.html は main-page.js を読み込んでいない。ぶつからない
- 暗黙の送信: form に submit ボタンが無く、テキスト欄も複数あるので、Enter 単独で送信されることは元から無い。Ctrl+Enter は `preventDefault` しているので、二重に送られることも無い
- 文書: 「完了」は `data-cmd="fix"` のボタンで、記述は実装と合っている。Mac で Ctrl+Enter も効くことは「Cmd+Enter も」という書き方と矛盾しない
- 冒頭の「外へ出すもの」の欄に keyDownHdr の行が足してある。書き方は onloadEdit の行と揃っている

## 作り込みすぎ

作り込みすぎ: なし

## 確信度が低いもの

- Safari（macOS）の一部の版では、IME で確定する Enter の keydown が compositionend の後に届き、`isComposing` が false になることが知られている。ただ、この処理は Ctrl/Cmd を押していないと動かないので、変換を確定する素の Enter で誤って送信されることは無いはず。実害は未確認
