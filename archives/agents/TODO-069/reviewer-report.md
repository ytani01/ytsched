# TODO-069 reviewer 報告

対象: `git diff`（未コミット）。

## 確信度の高い指摘

### 1. 検索モードで `popstateHdr()` が常に読み直しになる（回帰）

`my.js` の `popstateHdr()` は次のようになった。

```js
const offset = weekOffsetOfDate(date);
if ( offset !== null ) {
    setActiveWeek(offset, false);
    scrollToId(`date-${date}`, "top", "auto");
    return;
}
location.reload();
```

`weekOffsetOfDate()` は `.my-week-panel[data-monday="..."]` を探して
`offset` を決めるが、検索モードの panel には `data-monday` が付かない
（`main_handler.py` で `search_mode` のとき `"monday": None` にし、
`main.html` 側も `{% if w['monday'] %}` で属性ごと出さない）。その
ため **検索モードでは `weekOffsetOfDate()` が常に `null` を返し、
`popstateHdr()` は常に `location.reload()` になる。**

TODO-057 までの実装では、検索モードの唯一の週にも `pos == 'cur'` として
`id="date-..."` が付いていたので、`popstateHdr()` は
`scrollToId()` を先に試し、成功すれば読み直さずに済んでいた
（`git show HEAD` の旧 `popstateHdr()` を参照）。今回、その分岐が
「`weekOffsetOfDate()` が `null` でなければ移動、`null` なら即
`reload()`」に変わったことで、**検索モードでは「DOM 内にあるかを見て
から読み直すかどうかを決める」という元の動きそのものが失われ、常に
読み直しになった。**

再現の筋道: 検索モードで Home キー（`scrollToDate()` 経由、こちらも
`weekOffsetOfDate()` を使うが `null` のときは素通しして
`scrollToId()` を試すのでここは壊れていない）で今日の日付へ移動し
`pushDateInUrl()` で履歴が 1 つ積まれたあと、ブラウザの「戻る」を押すと
`popstateHdr()` が呼ばれ、対象の日付が検索結果の中に**まだ表示されて
いても**問答無用で `location.reload()` になる。

`scrollToDate()` 側は `offset !== null && offset !== activeWeekOffset`
のときだけ `setActiveWeek()` を呼び、`offset === null`（＝検索モード）
では素通しして今までどおり `scrollToId()` を試す作りになっているので、
`popstateHdr()` も同じ形（`offset === null` のときは
`scrollToId()` を試してから駄目なら `reload()`）に揃えるのが自然だと
思う。いまの `popstateHdr()` は「`offset` が分からない＝範囲の外」と
決め打ちしてしまっている。

影響は小さい（検索モードの戻る/進むは頻度が低い操作）が、
「持っている範囲の外へ出るときだけ読み直す」という TODO-069 の狙いに
検索モードだけ反しており、`tests/test_browser.py` にも
`popstate`／ブラウザの実際の戻る操作を通す検索モードのテストが無いので
気づきにくい。

## 確信度が低い指摘（参考）

- `slideWeekWrap()` が走っている最中（`swipeDragging` で指を追従させて
  いる途中）に `popstateHdr()` や `scrollToDate()` から
  `setActiveWeek()` が直接呼ばれると、`elWeekWrap.style.transform` が
  即座に `""` にリセットされ、`my-week-wrap-dragging` クラスも外れる。
  指はまだ画面に触れたまま（`swipeStart`/`swipeDragging` は生きている）
  なので、次の `touchmove` で `swipeDragTo()` が再び
  `transform` を上書きするまでの一瞬、見た目が飛ぶ可能性がある。
  ただし「ブラウザの戻る/進むを操作中に指も触れている」という状況は
  かなり稀で、実機で確かめないと実害があるか分からない。確信度は低い。
- `moveToMonday()` の `console.log(...)` が 1 行追加されている
  （`console.log(\`moveToMonday:next_offset=${next_offset}\`);`）。
  他のデバッグログと並んでいて実害は無いが、既存のログの粒度に対して
  1 行だけ足された経緯が分からず、要不要の判断は main に委ねる。

## 良かった点（参考）

- `setActiveWeek()` で `layoutWeeks()`（`left` の振り直し）と
  `elWeekWrap.style.transform = ""` を同じ同期処理内で行っており、
  スライド分の `transform` と新しい `left` の相対値が算術的に一致する
  ため、見た目のジャンプは起きない設計になっている（確認済み）。
- サーバ側の `get_load_months()` は `set_conf()` を呼ばず、
  `check_int_range()` / `convert_value()` という既存の TODO-027 の
  枠組みをそのまま使っており、他の設定の読み方から逸脱していない。
- `#cur_day` / `#date` / `#date_from` / ゲージ / URL / スクロール位置は
  `setActiveWeek()` でまとめて揃えており、取りこぼしは見当たらない
  （`modified_sde_id` は編集後の全ページ読み直し経路でしか使われず、
  今回の DOM 内移動とは無関係なので対象外）。
