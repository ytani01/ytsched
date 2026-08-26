# TODO-064 verifier への依頼

## 何を変えたか

PC のマウスの左右ドラッグでも週を送れるようにした。変更したファイルは 2 つ。

- `src/ytsched/webroot/static/js/my.js`
  - 追従の処理を `swipeDragTo()`、送るかどうかの判定を `swipeFinish()` に
    切り出し、タッチ側（`touchMoveHdr` / `touchEndHdr`）もそれを使うように
    した。**タッチの挙動は変えていないつもり**
  - `mouseDownHdr` / `mouseMoveHdr` / `mouseUpHdr` を足した
- `src/ytsched/webroot/templates/main.html`
  - 上の 3 つを `window` に登録した。**`mousedown` だけ capture**

`mousedown` を capture で拾い、`stopPropagation()` で伝播を止めている。
日付セルなどの `onmousedown` が押した瞬間に遷移してしまうため。動かずに
離したときは `mouseUpHdr` が `closest("[onmousedown]")` の
`onmousedown` を自前で呼ぶ。

タッチ由来の `mousedown`（ブラウザがタッチのあとに作るもの）は、
`lastTouchMsec` を見て素通しさせている。

## 確かめてほしいこと

1. `mise run lint` / `typecheck` / `test` が通ること（`upgradeproject` は
   走らせないこと）
2. `node --check src/ytsched/webroot/static/js/my.js`
3. **アプリを起動して、ブラウザで実際に触ること。**
   `--datadir` には必ず一時ディレクトリを指定する。playwright が使えるので、
   `page.mouse` で次を確かめてほしい
   - 日付セルの上でボタンを押し、左へ 200px ほど動かして離すと、次の週へ
     移ること（URL の `date` が 7 日進む）
   - 同じく右へ動かすと前の週へ移ること
   - **日付セルを動かさずにクリックすると、今までどおり編集画面へ行くこと**
     （`/ytsched/edit/?...`）。これがいちばん大事。ここが壊れると一覧から
     何も開けなくなる
   - 「スケジュール追加」ボタン、メニューバーの前週・次週ボタン、検索
     ボタンが、クリックで今までどおり効くこと
   - 検索欄をクリックしてフォーカスが入り、文字を入力できること
   - 少しだけ（数 px）動かしてから離したときも、クリックとして扱われること
4. `page.touchscreen` またはタッチイベントの合成で、**タッチでの週送りが
   今までどおり効くこと**（できる範囲でよい）
5. 編集画面（`/ytsched/edit/`）のボタンが今までどおり効くこと。
   リスナーは一覧だけに登録しているので、影響が無いことの確認

## 報告

`archives/agents/TODO-064/verifier-report.md` に書く。返事は 5 行以内。
**コードは直さない。** 見つけたことは報告するだけでよい。
