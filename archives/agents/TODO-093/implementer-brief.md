# TODO-093 implementer への依頼

`TODO.md` の TODO-093 を読んでから始めること。範囲はそこに書いてある
2 つのチェック項目だけ。挙動は変えない（初回ロード直後の細かな差だけは
TODO 本文が承知のうえで消す。下記「初回ロードの扱い」参照）。

## やること

表示中の週の月曜日（`YYYY-MM-DD` 文字列）を `ytState` に 1 つ持たせ、
読むときはそこから読む。`#cur_day` / `#date` / `#date_from` に 3 重に
持っているのをやめる。

### 1. `state.js` — `ytState` にフィールドを足す

`activeWeekOffset` の下に追加する:

```js
  // 表示中の週の月曜日 ('YYYY-MM-DD')。週表示は DOM の中だけで週を
  // 移るので (TODO-069)、どの週を見ているかをここで覚える (TODO-093)。
  // 読み込み時に main.html の #week_wrap の data 属性から入れる
  activeMonday: "",
```

state.js 冒頭のコメントの「外へ出すもの」は `ytState` としか書いていない
ので、そこは触らなくてよい。

### 2. `main.html` — `#date_from` の hidden input を `data-*` 属性にする

- 76〜77 行の
  `<input id="date_from" name="date_from" type="hidden" value="{{ date_from }}" />`
  を**削除する**。
- 138 行の `<div id="week_wrap" class="my-week-wrap">` に
  `data-monday="{{ date_from }}"` を足す。改行して属性を並べてよい
  （近くの `.my-week-panel` が `data-offset` / `data-monday` を改行して
  並べているので、それに揃える）。短いコメントを添える:
  「表示中の週の月曜（検索表示なら結果の一番古い日）。読み込み時に
  `ytState.activeMonday` へ移す (TODO-093)」

`sde_align` の hidden input（74〜75 行）は**触らない**。別の話。
`#cur_day`（309 行）と `#date`（336 行）の input は**残す**。
`form_filter` 内の `name="cur_day"` の hidden（378 行）も残す。

`#date_from` はどのフォームにも入っていない（74〜77 行は
`<div class="container-fluid p-0">` 直下で、`<form>` の外）。
`name="date_from"` はサーバに送られていないので、消して問題ない。

### 3. `main-page.js` — 読み込み時に `ytState.activeMonday` へ入れ、`#date_from` を読むのをやめる

`onloadHdr()`:

- `ytState.elWeekWrap = document.getElementById("week_wrap");` の直後に:
  ```js
  // 表示中の週の月曜 (検索表示なら結果の一番古い日)。サーバが
  // #week_wrap の data-monday に入れて渡す (TODO-093)
  ytState.activeMonday = ytState.elWeekWrap.dataset.monday;
  ```
- 104〜105 行
  ```js
  const date_from_str = document.getElementById("date_from").value;
  dispGauge(date_from_str);
  ```
  を `dispGauge(ytState.activeMonday);` にする。
- 125〜126 行の同じ 2 行も `dispGauge(ytState.activeMonday);` にする。
- 110 行の `const el_date = document.getElementById("date");` と、
  それを使う `scrollToDate(location.pathname, el_date.value, ...)` は
  **そのまま**。初回スクロールの目標は基準日（`#date`）で、月曜とは
  別の値。ここは `#date` を読み続ける。

`changeSearchN()`（129〜136 行付近）:

- `date: document.getElementById("cur_day").value,` を
  `date: ytState.activeMonday,` にする。

冒頭コメントの「外から使うもの」に `#date_from` を名指ししている箇所は
無い（`ytState` の列挙に `activeMonday` を足すだけでよい。無理に
足さなくてもよい。既存の粒度に合わせる）。

### 4. `week.js` — 週を移ったら `ytState.activeMonday` を書く

`setActiveWeek()`（139〜146 行）:

```js
  const monday = panel.dataset.monday;

  for (const id of ["cur_day", "date", "date_from"]) {
    const el = document.getElementById(id);
    if (el) {
      el.value = monday;
    }
  }
```

を、次のように変える:

```js
  const monday = panel.dataset.monday;
  ytState.activeMonday = monday;

  // 画面に出ている日付入力だけ値を合わせる。#cur_day は POST で
  // 送るときに doSubmit() が書くので、ここでは触らない (TODO-093)
  const el_date = document.getElementById("date");
  if (el_date) {
    el_date.value = monday;
  }
```

`moveToMonday()`（247〜268 行付近）:

- `const el_cur_day = document.getElementById("cur_day");` を消す。
- `let cur_day = new Date(el_cur_day.value);` を
  `let cur_day = new Date(ytState.activeMonday);` にする。
- `let d1 = new Date(el_cur_day.value);` を
  `let d1 = new Date(ytState.activeMonday);` にする。
- `console.log(...)` はそのままでよい。

week.js 冒頭コメントの「外から使うもの」で `ytState (state.js)` の行に
`activeMonday` を足す（`elWeekWrap・activeWeekOffset` の並びに）。
114 行付近の docstring が `#cur_day`・`#date`・`#date_from` を月曜に
揃えると書いているので、実態に合わせて書き直す（`ytState.activeMonday`
と、画面の `#date` を合わせる、という趣旨に）。

### 5. `nav.js` — `#cur_day` を読み書きしている箇所を `ytState.activeMonday` に

`doSubmit(id)`（106〜110 行）: フォームを送る直前に、そのフォーム内の
`cur_day` に月曜を載せる。

```js
const doSubmit = (id) => {
  loadingSpinner(true);
  const el = document.getElementById(id);
  // 表示中の週の月曜を hidden の cur_day に載せてから送る (TODO-093)
  for (const cd of el.querySelectorAll('[name="cur_day"]')) {
    cd.value = ytState.activeMonday;
  }
  el.submit();
};
```

`popstateHdr()`（258〜261 行）:

```js
    const el_cur_day = document.getElementById("cur_day");
    if (el_cur_day) {
      el_cur_day.value = date;
    }
```

を

```js
    ytState.activeMonday = date;
```

にする。

`scrollToDate()`（360 行と 373 行）:

- 360 行 `const el_cur_day = document.getElementById("cur_day");` を消す。
- 373 行 `el_cur_day.value = date;` を `ytState.activeMonday = date;` に
  する。

nav.js 冒頭コメントの「外から使うもの」の `ytState (state.js)` の行に
`activeMonday` を足す（`elMain・activeWeekOffset` の並びに）。

## 初回ロードの扱い（判断はもう済んでいる。実装だけ）

読み込み直後、サーバは `#cur_day` に基準日（`{{ date }}`）を、
`date_from` に週の月曜を入れて渡していた。今回の変更で、初回でも
`ytState.activeMonday` は月曜になる（`#week_wrap` の `data-monday`）。
つまり「週を 1 回も移らずに検索・絞り込みを送ると、`cur_day` が基準日
ではなく月曜で送られる」ようになる。これは TODO 本文が承知していて、
3 つの値を 1 つ（月曜）に畳むのが今回の狙い。**そのままでよい。**
`cur_day` はサーバ側で `date` が無いときの弱い手がかりなので、
数日ずれても検索結果はほぼ変わらない。

## テストの修正

`tests/test_main_handler.py` の
`test_search_mode_max_days_when_nothing_is_found`（373〜384 行付近）が
`assert f'value="{date_from}"' in body` で hidden input を見ている。
`#week_wrap` の属性に移すので、
`assert f'data-monday="{date_from}"' in body` に直す。docstring の
「hidden の `date_from`」も実態に合わせて 1 語直す（「`#week_wrap` の
`data-monday`」など）。

他に `date_from` の hidden を前提にしたテストが無いか、
`grep -rn 'date_from\|cur_day' tests/` で確認すること。
`test_web.py` / `test_main_handler.py` の `cur_day` 系テストは、
サーバへ `cur_day=` を直接渡していて DOM の hidden とは無関係なので
触らなくてよい（念のため中身を見て確認）。

## 確認（自分でも動かす。最終確認は verifier が別に行う）

- `mise run fmtjs` `mise run lintjs`
- `mise run test`（特に `tests/test_browser.py`）
- 直したところを一通り直してからまとめて走らせる。

## 決まり

- 最小限の変更。範囲外に手を出さない。
- git commit / TODO.md 編集はしない。
- 報告は `archives/agents/TODO-093/implementer-report.md` に。返事は 5 行以内。
