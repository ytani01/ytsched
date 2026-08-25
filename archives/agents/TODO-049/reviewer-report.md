# TODO-049 reviewer 報告

対象: `git diff`（`src/` と `tests/` の 12 ファイル）。TODO.md の
「## TODO-049.」、`request-implementer.md`、`implementer-report.md` を
読んだうえでのレビュー。**コードは直していない。**

## 指摘（確信度高い順）

### 1. `dispGage()` が `sessionStorage` に例外時のガードを持たず、
   画面が表示されないまま固まる経路がある

`my.js` の `dispGage()`:

```js
const monday_str = getLocaltimeDateString(mondayOf(date_str));
const prev_monday_str = sessionStorage.getItem(GAGE_MONDAY_KEY);
sessionStorage.setItem(GAGE_MONDAY_KEY, monday_str);
```

`try/catch` が無い。`sessionStorage` へのアクセスは、Safari の
「すべての Cookie をブロック」設定や、`allow-same-origin` の無い
`<iframe>` に埋め込まれた場合など、実在する環境で
`SecurityError` を投げうる。

これが問題になるのは `main.html` の `onloadHdr()` の、次の分岐:

```js
if ( body_h < win_h ) {
  const date_from_str = document.getElementById("date_from").value;
  dispGage(date_from_str);
  elMain.style.visibility = "visible";   // ← dispGage が例外を投げると届かない
  return;
}
```

`#main` は既定で `visibility: hidden` なので、ここで例外が起きると
**`visibility: visible` に一度も切り替わらず、画面が白いまま止まる**。
（別の分岐、`body_h >= win_h` のほうは `scrollToDate()` →
`scrollToId()` が先に `visibility = "visible"` を設定してから
`dispGage()` を呼んでいるので、そちらは影響を受けない。)

**この分岐に入る頻度が、今回の変更で上がっている点が重要。** 以前は
表示範囲が前後 45 日（`DEF_DAYS`）で、`body_h < win_h`（1 画面に
収まる）はほぼ起きなかった。週表示になり 7 日分だけになったことで、
予定の少ない週やウィンドウが広い環境（`tools/screenshot.py` の検証
幅である 800px を含む）では、この分岐に日常的に入るようになった。

`sessionStorage` 自体は依頼書が名指しで懸念していた点（reviewer 依頼
の 2）。

### 2. `.my-gage-r-no-transition` の打ち消しは、CSS のソース順に
   依存している（今は動くが壊れやすい）

`.my-gage-r`（`transition: bottom 0.3s ease-out`）と
`.my-gage-r-no-transition`（`transition: none`）は、どちらもクラス
1 つぶんの詳細度で同じ。今は `my.css` 内で `.my-gage-r-no-transition`
が `.my-gage-r` より後ろに書かれているので、両方付いた状態
（`placeGageWithoutTransition()` が `classList.add`）では後者が勝ち、
意図どおり `transition` を止められている。

ただし、これは**詳細度でなくソース順で勝っているだけ**なので、
将来 `my.css` を並べ替えたとき（例えば `.my-gage-r` 系をまとめ直す
ような、この項目とは無関係のリファクタリング）に `.my-gage-r` の
定義が後ろへ動くと、打ち消しがエラーも出さずに効かなくなる。
効かなくなった場合の症状は「週を切り替えて読み直したときに、前の週の位置から
一瞬でジャンプするはずが、そこにも `transition` が掛かって不要な
アニメーションになる」で、見た目の変化が小さいぶん気づかれにくい。

依頼書（reviewer 依頼の 7）が名指しで懸念していた点で、確認した
限り**現状は問題ない**が、依存関係が暗黙なので指摘しておく。

## 確信度が低いもの

### 3. `test_todo_one_day_over_the_boundary_is_not_shown` が、
   実行する曜日によっては「今日の欄にだけ出ない」ことを実質確かめない

`self.write_todo(datetime.date.today() + datetime.timedelta(4))` で
期限を今日+4日にし、`day_block(body, today)` に TITLE が無いことを
見ている。

`today` の曜日によって、`today + 4` がその週（月曜〜日曜）に
収まるかどうかが変わる。月〜水に実行すれば +4 日はまだ同じ週の中
（他の日の欄には出るが今日の欄には出ない、という意図どおりの確認に
なる）。しかし木〜日に実行すると +4 日は翌週になり、ToDo はどの
欄にも出ない（週表示の外なので）。この場合でも
`day_block(body, today)` に TITLE が無いのは必ず真になり、
テストは「今日の欄にだけ出ない」ことではなく「週の外なら何も出ない」
ことを確認しているに過ぎない。

失敗はしない（不在の確認なので、曜日によって落ちたり通ったりする
ことはない）ので`test_overdue_todo_is_shown_on_today` ほど深刻ではないが、
依頼書が名指しで見てほしいとしていたテスト（reviewer 依頼の 6）
なので、テストの意図が曜日によって半分近くの日で薄まる点は書いて
おく。

### 4. `mondayOf()` の JST/UTC の扱いは `moveToMonday()` と一致している

依頼書の懸念（reviewer 依頼の 3）を確認した。`mondayOf()` は
`new Date(date_str.split('/').join('-'))` → `.getDay()` で曜日を
取り、`moveToMonday()` の既存の計算（`cur_day = new Date(el_cur_day.value)`
→ `.getDay()`、`el_cur_day.value` も `{{ date }}` 由来のハイフン
区切り）と同じ組み立て方になっている。両者は一致しており、この
diff で新たにずれを持ち込んではいない。

（`new Date()` にハイフン区切りの日付だけを渡して `.getDay()` する
やり方自体は、UTC と後ろにずれる方向のタイムゾーン（UTC より
西側）だと日付が 1 日ずれる可能性が理論上ある。ただしこれは
`moveToMonday()` に元からある書き方で、今回の変更が持ち込んだもの
ではないので、この項目の範囲外として報告に留める。）

## 判断が要る点（main 向け）

- 上記 1（`dispGage()` の `sessionStorage` 無保護）は、週表示になった
  ことで発現しやすくなった実害のある経路だと考える。直すかどうかの
  判断を。
- 上記 2・3 は確信度が低い/軽微。直すかどうかは main の判断。
