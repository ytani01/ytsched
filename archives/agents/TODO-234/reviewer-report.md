# TODO-234 reviewer 報告

対象: `e3375c5`。テストは流していない（読んで判断）。

## 要修正

無し。

## 検討

### 1. `scrollToId()` の `"home"` の変更（今日の週の月曜を探す）を守るテストが無い

- 場所: `nav.js` 383〜389 行（`el_monday`）、`tests/test_browser.py` の
  `test_home_button_keeps_today_in_view`
- 何が起きるか: `el_monday` を元の `el` に戻しても（＝今日の欄を上端に合わせても）、
  既存のテストは通ると読める。
  - 日曜の場合: `_wait_today_above_footer` は「日曜の欄が上端〜ゲージの間にある」しか
    見ない。日曜を上端に合わせても満たす
  - 月曜の場合: `date` も月曜なので `el` と `el_monday` が同じ
  - 新しい 4 件は点滅と URL だけを見る
- 今回 `date` に今日を渡すようになったので、「今日が週の途中で、はみ出さないときは
  月曜が上端」は、この変更で初めて `el_monday` に頼るようになった。完了条件 3（位置は
  今のまま）を直接見るテストが無い。実装者の「直す前は落ちる」は点滅の 4 件だけを
  確かめている
- 重さ: 今の実装は正しいと読める。抜けているのはリグレッションの検出。
  実際に `el` に戻して流してはいないので、通るかどうかは未確認

### 2. URL の `date` が今日になったことで、ホームのあとの位置が経路で変わる

`homeButtonHdr` のシングルクリックは `pushDateInUrl(today)` で、ダブルクリックは
`?date=<今日>&sde_align=home` になる。ここから先の経路は `"home"` を通らないか、
通っても `date` が今日ではないので、合わせる位置が直す前と変わる。項目の「URL の
`date` も今日」の結果なので、壊れているとまでは言えない。実害は未確認。

- (a) シングルクリックのあとに F5、または戻る/進むでその履歴に来たとき:
  `?date=<今日>`（`sde_align` は無い）なので、`onloadHdr` と `popstateHdr`（`nav.js` 293 行）が
  `"top"` で**今日の欄を上端**に合わせる。直す前は月曜が上端で、ホームボタンを押した
  直後の位置と同じだった。今日が週の後半だと、月曜〜前日が画面の上へ隠れる
- (b) ダブルクリックのあと、URL には `sde_align=home` が残る。`pushDateInUrl` は `date`
  しか書き換えないので、2 週以上離れた週へ送ってから F5 すると
  `?date=<離れた週の月曜>&sde_align=home` で読み直す。`scrollToId` は今日の週の月曜を
  探し、それは `display: none` のパネル（`my.css` の `.my-week-panel`）にあるので
  `offsetTop` が 0 になり、`top = -30`（先頭）へ移る。直す前は `el`（その週の月曜）で
  合わせていた。隣の週（`my-week-near`）だと、`offsetTop` の基準が絶対位置のパネルになる。
  ずれは月の見出しの高さ程度と見込むが、測っていない

### 3. 実装者が挙げた 2 点の中身

- 検索画面の基準日: `sched_load.py` の `search()` は `date_to = date` から日を遡り、
  `search_n` 件に達したら打ち切る。`date` が月曜から今日になったので、
  **火曜〜今日の予定も検索結果に入る**ようになった。直す前は、今日が週の途中だと今日の
  予定が結果に出なかった。そのぶん `search_n` で打ち切る位置も新しい方へずれ、
  いちばん古い側の結果が最大 6 日ぶん減ることがある。良くなる方向の変化と読めるが、
  挙動の変化ではある
- 月間表示: `scrollToDate` → `setActiveBlockOfDate(today)` なので、URL・`activeMonday`・
  ゲージの基準が今日になる。もう 1 つ、**今日と今週の月曜が別の 6 ヶ月ブロックに入る週**
  （1/1 か 7/1 が月曜でない年の、その週）では、移る先のブロックが変わる。直す前は
  月曜側（前のブロック）へ移っていた。月間表示には `#date-… .my-date-col` が無い
  （`main.html` 185 行は週間表示の分だけ）ので、`flashDate` は何もしない。完了条件は
  月間表示の点滅を求めていないので、問題とは読まない

## 好みの範囲

- `src/README.md` の追記は、「ホームボタンとキーの `Home` は…画面の位置は、
  `scrollToId()` の `"home"` が…」と続けて書いてある。しかしキーの `Home` は `"top"` で
  今日を上端に合わせ、`"home"` を通らない（`keyboard.js` 116 行。直す前と同じ）。
  キーも月曜を上端に合わせるように読めてしまう
- `gauge.js` 11〜12 行の依存コメントに、`mondayOf()` の呼び出し元として
  `main-page.js (homeButtonHdr)` が残っている。今は呼んでおらず、`nav.js (scrollToId)` が
  抜けている

## 問題なしの観点

- 完了条件 1（ホームの 4 経路とキーの `Home` で今日へ移動し、今日が点滅、月曜は点滅しない）:
  満たす。ダブルクリックと検索画面の点滅は、読み直し先の `?date=<今日>` を TODO-233 の
  `linkDate` が拾う形で、`flashDate` は使っていない
- 今日の週へ横に流す動き（TODO-217）: `slideToWeekOfDate(today)` は月曜と同じ週なので変わらない
- 検索画面のダブルタップ判定（TODO-165）とダブルクリックでの読み直し（TODO-069）:
  `date` の値が変わっただけで、分岐は変わっていない
- TODO-233・TODO-213・TODO-215 の点滅: `flashEl` への切り出しは元の処理と同じ
- `"home"` のほかの呼び出し元: `reloadHome` と、読み直し後の `onloadHdr` だけ
  （`rg '"home"'`）。`#sde_align` の hidden は form の外（`main.html` 81 行。form は 366 行から）
  なので、フォームの送信では持ち越されない。URL で持ち越される件は検討 2(b)
- bfcache: `flashDate` は `load` に頼らないので、変化は無い
- 足したテストの強さ: 点滅の 4 件は、直す前のコードでは点滅しないか月曜が点滅するので
  落ちる（`today_str` を月曜＋2 日に書き換えている）。キーの `Home` と検索画面の 1 件は、
  今日が月曜だと月曜の点滅を見分けられないが、点滅が無いことは捕まえる。抜けは検討 1

## 確信度の低いもの

無し。

作り込みすぎ: なし（`flashEl` の切り出しは 2 か所で使っている）。

---

# 再レビュー（`d9c3601`）

読んで判断した。テストと実測はしていない。

## 要修正

### R1. `sde_align=home` が URL から消えず、ホーム以外で積んだ履歴にも残る。戻る/進むと読み直しで位置が変わる

- 場所: `nav.js` の `pushDateInUrl()`（229 行〜）、`scrollToDate()`（465 行）、`popstateHdr()`（300〜305 行）
- 何が起きるか: `pushDateInUrl()` は `sde_align` を渡されたときに**書くだけで、消さない**。
  `new URL(location.href)` から作るので、ホームボタンで一度 `sde_align=home` が付くと、
  そのあと積む履歴にも全部残る。経路は `setActiveWeek()`（`week.js` 200 行、週送り）、
  `scrollToDate(..., "top")`（ミニカレンダーの `scroll-date`、キーの `Home`、`gauge.js`、
  `week.js` 573 行）の 2 つ。`popstateHdr()` は今回から URL の `sde_align` を読むので、
  これらの履歴へ戻る/進むと `"home"` で合わせる。読み直したとき（URL を開き直す、
  `popstateHdr` の `location.reload()`）も、サーバが `sde_align=home` を引き継ぐので同じになる
- 例（直す前 `534930a` との違い）: ホームボタンをシングルクリックし、続けてミニカレンダーで
  同じ週の金曜を押す → `?date=<金>&sde_align=home` が積まれる → 戻る → 進む。
  `534930a` では `"top"` で金曜が上端に来た。今回は `"home"` なので、その週の月曜が上端になる
  （今日の欄がはみ出すなら、今日の下端に合わせる）
- 週送りのほうは、月曜に合わせるので `"top"` とほぼ同じ位置になる。ただし `"home"` は
  `el_today` が今の週にあるかを見ない。今日の週が隣の週（`my-week-near` は
  `display: flow-root` なので寸法を持つ）で、その週が長いと、今日の下端に合わせる計算が
  見えていない週で効いて、下へずれることがあると読める。実害は未確認
- ダブルクリックの読み直しのあとは、直す前から URL に `sde_align=home` が残っていた。
  ただ `534930a` の `popstateHdr` はそれを読まなかったので、戻る/進むは `"top"` だった。
  今回 `popstateHdr` が読むようになったので、ダブルクリックの経路でも上と同じことが起きる
- 重さ: 読み筋ははっきりしている（`set` しかなく `delete` が無い）。保つと決めた戻る/進むの
  位置（TODO-050）が、ホームボタン以外の操作で変わるので要修正とした。実測はしていない
- TODO-233 の点滅は `date` だけを見る（`linkDate`）ので、`sde_align` が残っても変わらない

## 検討

### R2. 足したテストの「戻る → 進む」は、`popstateHdr` を通っていないかもしれない（確信度低）

- 場所: `tests/test_browser.py` `test_home_button_aligns_monday_to_top_when_today_fits` の末尾
- 何が起きるか: 直前の `page.goto(page.url)` で文書が新しくなっている。そのあとの
  `go_back()` / `go_forward()` は文書をまたぐ移動なので、同じ文書の中の `popstate` では
  なく、読み直しか bfcache からの復元になる。`scrollTo(0, 200)` をするのは `go_back()` 先の
  文書で、`go_forward()` で戻る文書は bfcache ならスクロール位置ごと戻る。その場合、
  `popstateHdr` の `sde_align` 読み取りを壊しても通る可能性がある。実装者は「e3375c5 の src に
  戻すと落ちる」と確かめているが、それはおそらく開き直しの部分で落ちている。
  `popstateHdr` の変更だけを戻して落ちるかは確かめられていない
- R1 を直すときに、同じ文書の中での戻る/進むのテストにするかを決める材料として挙げる

## 問題なしの観点

- 前回の指摘 2(a)（シングルクリックのあとに開き直す、戻る/進む）: 実装者の実測表のとおり、
  月曜が上端に戻る形になっている
- 前回の指摘 2(b)（離れた週で `sde_align=home` のまま開き直す）: `el_monday` が `id` の週の
  月曜になったので、`display: none` のパネルを測ることは無くなった
- `"home"` が `id` の日付の週の月曜に合わせる形: `id.slice(5)` は `date-YYYY-mm-dd` の日付部分で、
  呼び出し元は全部この形の id を渡す。足したテストの、クリック直後と開き直しの部分は、
  `el_monday` を `el` に戻すと落ちる強さがある（`day_top > top_expected + 30` で、取り違えを
  見分けられることを先に確かめている）
- `src/README.md`（キーの `Home` は `"top"`、`sde_align=home` の履歴）と `gauge.js` の依存コメント:
  実装と合っている

作り込みすぎ: なし。

---

# 3 回目（最終の方式。`git diff 534930a 898af11 -- src docs tests`）

読んで判断した。テストは流していない。

## 要修正

無し。

## 検討

### T1. `_wait_for_top_screen` が、読み直しの前に通ってしまう

- 場所: `tests/test_browser.py` 1364 行 `_wait_for_top_screen`。これを使う週間表示・月間表示の
  ダブルタップのテスト（`test_home_button_double_tap_reloads_the_week_view`、
  `..._returns_to_the_week_view_from_month`、`test_home_button_double_click_flashes_today_not_monday`）
- 何が起きるか: 前は「URL に `sde_align=home` がある」ことも待っていた。これは読み直したあとに
  しか付かない目印だった。今は `date=<今日>` だけを見る。ところが週間表示・月間表示では、
  1 回目のタップ（シングルの経路）が `scrollToDate` / `setActiveBlockOfDate` で、もう
  `date=<今日>` を URL に積む。そのため `wait_for_url` は、2 回目のタップの POST が終わる前に
  通りうる
  - `test_home_button_double_click_flashes_today_not_monday`: 1 回目のタップの `flashDate()` で
    今日がもう点滅しているので、**ダブルクリックの読み直しが壊れていても通る**。
    「読み直したあとに TODO-233 が今日を点滅させる」は見ていない
  - `..._reloads_the_week_view`（`assert not _marked`）と `..._from_month`（`_assert_top_screen`）:
    読み直しの途中や前に判定が走りうる。待ちが効かないので、落ちたり通ったりする形になる。
    実害は未確認（ページの遷移が速ければ通る）
- 検索画面のテストは、1 回目が `doPost` で URL を積まないので、この問題は無い
- 前の目印に代わるものとしては、`_mark` が消えたことを待つ（`wait_for_function("() =>
  window.__ytsched_mark !== 1")`。検索画面のテストが使っている）などが考えられる。直し方は
  main の判断

## 好みの範囲

- `main-page.js` 35 行の依存コメント `getLocaltimeDateString() (nav.js) -- homeButtonHdr` が残っている。
  今の `homeButtonHdr` は `ytsched.today_str` をそのまま使い、呼んでいない。10 行の `flashDate()` の
  説明は「homeButtonHdr が使う」だけで、`keyboard.js` が抜けている

## 問題なしの観点

- 方針どおりで、余計な処理は無い: `"home"` の分岐を消し、`date` を今日にして、読み直さない 2 経路で
  `flashDate()` を呼ぶだけ
- `sde_align=home` の残り: `src/ytsched` で渡す箇所も読む箇所も無い。古い URL に `sde_align=home` が
  残っていると、`scrollToId` は `"top"` にも `"bottom"` にも当たらず、スクロールしないで `true` を返す
  （表示は出て、位置は合わない）。値の検証が無いのは前からで、知らない値と同じ扱い。壊れはしない
- `homeButtonHdr` の `scrollToDate(url_prefix, today_str)`: 既定は `"top"`・`"smooth"` で、キーの `Home` と
  同じ位置になる
- `flashEl` の切り出し: 元の処理と同じで、TODO-213・TODO-233 の点滅は変わらない
- 戻る/進む（TODO-050）: `popstateHdr` と `pushDateInUrl` は変わっておらず、ホームボタン以外の履歴に
  変化は無い。ホームのシングルクリックの履歴は `date=<今日>` で、戻る/進むすると `"top"` で今日が上端に
  来る。押した直後と同じ位置
- テストの強さ（T1 以外）: シングルクリックのテストは、月曜日を上端に合わせると今日の位置が
  `top_expected` からずれて落ちる。点滅の有無と月曜日の点滅も見ている。キーの `Home` のテストは、
  直す前の点滅しないコードで落ちる。TODO-199 のテスト 2 件を消したのは、方針で `"home"` をやめたので妥当
- `src/README.md` と `docs/UsersGuide.md` の記述: 実装と合っている

作り込みすぎ: なし。
