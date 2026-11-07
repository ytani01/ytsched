# TODO-233 reviewer 報告

対象: `git diff -- src tests`（`main-page.js` の `flashUpdated()`、`tests/test_browser.py`）。
実測は scratchpad に置いた使い捨ての pytest（`tests/test_browser.py` の `server` / `page` を import）で行った。リポジトリには残していない。

## 問題の無い点

- `flash_*` があるときの挙動は変わっていない。`flash_date` があれば今までどおりそちらを使い、`flashDate || sdeId` のときは今までどおり `findLast` で位置を合わせる
- `flash_sde_id` だけ（+ `date`）のとき、日付の欄も点滅するようになるが、位置合わせの対象は `findLast` で予定の行のままなので、TODO-215 の位置合わせは変わらない。サーバは `flash_sde_id` を付けるとき必ず `flash_date` も付ける（`main_handler.py:70-71`）ので、実際にはこの組み合わせは来ない
- POST のあと: `get_date()` は `modified_date or date or cur_day` を返すので、リダイレクト先の `date` と `flash_date` は同じ値。どちらを優先しても結果は同じ
- 足したテスト 2 件は、それぞれ「予定の行に付かない」「date だけのときにずらさない」を見ている。分岐を捕まえられている（ガードを外すと落ちることは main が確認済み）
- `_write_many_sched` の切り出しは中身を変えていない（`range(40)` → `range(n)` で、呼ぶ側は 40 を渡す）
- 作り込みすぎ: なし

## 指摘

### 1. 【要修正（ただし方針で許容もありうる）】`?date=` が無い URL で開いても点滅する

- 場所: `main-page.js:854-855`（load のリスナーを登録する順）と `flashUpdated()` の `url.searchParams.get("date")`
- 原因: `load` では `onloadHdr` が先に走る。その中の `scrollToDate(..., push_flag=false)` が `replaceDateInUrl()` で URL に `date=<cur_day>` を書き込む。そのあとに走る `flashUpdated()` は、書き込まれた `date` を `?date=` 付きで開いたものとして読んでしまう
- 実測: 今日の予定を 40 件、`SHORT_VIEWPORT` の画面で `GET /ytsched/`（date なし）を開いた
  → URL は `?date=2026-11-08` になり、`.my-flash` は `date-2026-11-08` に付いた
- さらに、中身が画面より短いときは `onloadHdr` が `scrollToDate()` の手前で return する（`body_h < win_h`）ので、URL が書き換わらず点滅しない（予定が無いときの実測: URL は `/ytsched/` のまま、`.my-flash` は 0）。date なしで開いたときに点滅するかどうかが、ページの長さで変わる
- 項目の範囲は「`?date=` 付きで読み込んだとき」。トップ（ブックマークや、date を付けないリンク）でも点滅させてよいかは、利用者に聞かないと決められない。実害は見た目だけ

### 2. 【検討】画面内の移動から戻る/進むで戻ったときは点滅しない（コメントと違う）

- 場所: `flashUpdated()` は `load` だけに登録されている（`main-page.js:855`）。`popstate` に登録されているのは `popstateHdr`（nav.js）だけで、そこから `flashUpdated()` は呼ばれない
- どういうときか: 範囲内の移動（`scrollToDate()` → `pushDateInUrl()`）は読み直しが起きないので、その履歴へ戻る/進むと `popstate` しか来ない。このアプリでは戻る/進むのほとんどがこれ
- 実測: `?date=今日` で開き、5 秒の点滅が終わるのを待ってから `scrollToDate(明日)` → `go_back()` とした。読み直しは無く（`window.__m` が残った）、URL は `?date=今日` に戻ったが、`.my-flash` は 0 件だった。文書をまたぐ戻る（`location.href` で移ってから戻る）では点滅した
- 利用者と決めた「戻る/進むでも毎回」を、画面内の履歴まで含む意味で取るなら抜けている。docstring の「リロードや戻る/進むでも点滅する」も、画面内の履歴では当てはまらない
- 文書をまたぐ戻るで点滅したのは Playwright の Chromium での結果。普通のブラウザで bfcache から戻ったときは `load` ではなく `pageshow` だけが来るので、点滅しない可能性がある（未確認）

## 確信度の低いもの

- 月の表示（`view=month`）には `#date-YYYY-mm-dd` が無い（実測で `querySelector` が null）。`?date=…&view=month` では点滅しない。null は既存のガードで飛ばすのでエラーにはならない。月の表示も含めるつもりだったかは分からない（実害は未確認）

## 再レビュー（指摘 1 の直しと docstring・`src/README.md`）

### 問題の無い点

- `linkDate` はスクリプトを読んだとき（`base.html` の `<head>` にある同期の `<script>`）に取る。URL を書き換えるのは `scrollToDate()` / `pushDateInUrl()` だけで、どちらも `load` か操作のあとに走るので、取れるのは書き換える前の値。指摘 1 は直っている
- リロードでは、そのときの URL（画面内で移動したあとなら、積まれた `date`）を新しく読むので点滅する。docstring の「リロードでも点滅する」と合っている
- `test_flash_needs_date_param` は、書き込みが起きたこと（`"date=" in page.url`）を前提として確かめてから、点滅が 0 件であることを見ている。ページが短くて書き込みが起きないときにも、黙って通ることはない
- `src/README.md` に足した 2 行は実装と合っている
- 「戻る/進むでは点滅させない」に決めたことと、popstate に手を入れていないことは食い違っていない
- 作り込みすぎ: なし

### 指摘

#### 1. 【好みの範囲】JSDoc と `flashUpdated` の間に `linkDate` が挟まっている

- 場所: `main-page.js:451-462`
- `/** ... */` のすぐ下が `// …` と `const linkDate` になったので、エディタや JSDoc では、この説明が `linkDate` に付いたものとして扱われる。`linkDate` を JSDoc の上へ移せば解ける。動作には関係しない

### 範囲外で気づいたこと（今回の差分の外。直さなくてよい）

- `src/README.md:236` の「3 秒点滅させて」は今回より前からある文言だが、`my.css:657` の `animation: my-flash calc(5s / 6) step-end 6` は 5 秒になる。どちらに合わせるかは確かめていない
