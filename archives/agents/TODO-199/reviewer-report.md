# TODO-199 レビュー報告（reviewer）

対象: 未コミットの `git diff`（`src/ytsched/webroot/static/js/nav.js` /
`main-page.js`、`tests/test_browser.py`）。コードは直していない。

## 指摘（確信度が高いもの）

### 1. `nav.js` `scrollToId()` の `"home"` 分岐で、月曜日側と今日側の座標系が食い違う

`src/ytsched/webroot/static/js/nav.js:346-376` 付近。

```js
const top_of_el = el.offsetTop;                       // #week_wrap からの相対位置
...
const alignBottom = (bottom) => bottom - win_h + menu_bar_h + scroll_offset;
if (sde_align == "home") {
  let top = top_of_el - scroll_offset;                 // offsetTop ベース（依頼の説明どおり、文書の上端から68pxずれる）
  const el_today = document.getElementById(`date-${ytsched.today_str}`);
  if (el_today) {
    const bottom_of_today =
      el_today.getBoundingClientRect().bottom + window.scrollY;   // 文書の絶対座標（ずれ無し）
    top = Math.max(top, alignBottom(bottom_of_today));
  }
  scrollTo({ left: 0, top: top, behavior: behavior });
}
```

`top`（月曜日を上端に合わせる候補）は `offsetTop` ベースで、依頼の説明に
ある通り「文書の上端から 68px ずれる」。一方 `alignBottom(bottom_of_today)`
（今日の下端に合わせる候補）は `getBoundingClientRect().bottom + scrollY`
で測っていて、これは文書の絶対座標そのもの（ずれが無い）。

`Math.max()` はこの 2 つを直接比較・合成しているが、**片方だけ 68px 程度
ずれた値**なので、比較結果と最終的な `scrollTo` の目標位置は、本来 2 つとも
同じ座標系で測ったときの結果と一致しない。既存の `"top"` / `"bottom"` は
それぞれ単独で `offsetTop` だけを使っており、内部では常に一貫していたが、
`"home"` は初めて 2 つの座標系を 1 回の比較の中で混ぜている点が今回の diff
固有の変化点になる。

この食い違いが実際に効くのは、月曜合わせで今日の欄がぎりぎり収まるか
どうかの境界（ずれの幅とほぼ同じ 68px 程度の帯）に限られる。この帯では、
本来なら月曜合わせのままで足りるはずの週で不要に今日の下端合わせへ
切り替わったり、逆にわずかに今日がはみ出したまま止まったりする（＝
この項目が直そうとしている症状がこの帯でだけ残る）可能性がある。
どの程度の実害があるかは値を測っておらず未確認。境界線上の判断は
主が決めることなので、ここでは事実の指摘にとどめる。

### 2. `main-page.js` 側の「外へ出すもの」コメントが更新されていない（TODO-097 の決まり）

`nav.js` の先頭コメントには、今回の diff で

```js
//   window.ytsched.today_str (main-page.js の onloadHdr()) -- scrollToId
//     (sde_align が "home" のとき、TODO-199)
```

が足されている。これは正しい（`scrollToId` が `ytsched.today_str` を
新たに読むようになった、という依存の追記）。

一方 `main-page.js` 側では、`today_str` は「外から使うもの」の並びに
`main.html の <script>` の由来としてしか出ておらず、「外へ出すもの」には
挙がっていない。grep で確認した限り、`ytsched.today_str`
（`main-page.js:327` の `onloadHdr()` で `#main` の `data-today` から
入れている値）は、この diff より前は `main-page.js` 内だけで使われていた
（`homeButtonHdr` の 1 箇所）。今回の変更で `nav.js` の `scrollToId()` が
初めての外部からの参照になった。

同じファイルの `window.ytsched.view_month`（`main-page.js:11-12`）は、
`onloadHdr()` が入れて `week.js`・`nav.js`・`swipe.js` が読む値として、
すでに「外へ出すもの」に挙げてある。`today_str` も同じ形（`onloadHdr()`
が入れる値を他ファイルが読むようになった）なので、TODO-097 で決めた
書式（外へ出す側・外から使う側の双方に書く）に揃えるなら、
`main-page.js` の「外へ出すもの」にも `today_str` と `nav.js`
（`scrollToId`）の対を足す形が一貫する。今回は片側（`nav.js`）にしか
足されていない。

## 確認して問題が無かった点

- `alignBottom()` へのくくり出しは、既存の `"bottom"` の式
  （`bottom_of_el - win_h + menu_bar_h + scroll_offset`）と完全に同じで、
  挙動は変わっていない。
- `el_today` が DOM に無いとき（今日が表示中の週の外、検索画面、月間表示）
  は `if (el_today)` で素通りし、`"top"` と同じ月曜合わせだけになる。
  月間表示は `scrollToDate()` の `ytsched.view_month` 分岐で
  `scrollToId()` 自体に入らないので影響を受けない。
- `homeButtonHdr()` の検索画面まわり（1 回目は検索語つきで読み直す、
  2 回目だけ `reloadHome()` で `sde_align: "home"`）は変えられておらず、
  依頼の方針どおり。
- `edit_handler.py` は `sde_align` をリクエストから読んでおらず、
  `edit.html` は検索の有無だけで `"top"` / `"bottom"` を固定で出す
  （`sde_align` を上書きしている）。`main_binder.py:245`
  （`get_sde_align()`）・`main_handler.py:68` は値の検査をせずそのまま
  引き継ぐが、`"home"` が編集画面など他の画面へ流れる道は無い。
  `main_view.py` でも `sde_align` はテンプレートの hidden input 以外に
  使っていない。
- `onloadHdr()` から `scrollToDate(..., el_sde_align.value, "instant", false)`
  を呼ぶ経路（読み込み直後）は、`today_str` を先に代入した後に呼ばれる
  順序になっており、`"home"` を渡されても未定義の `today_str` を参照する
  ことはない。
- `tests/test_browser.py` の `_wait_for_top_screen` を `sde_align=home` に、
  `test_home_button_single_tap_still_reloads_search_screen` の
  `"sde_align=" not in page.url` への変更は、対応する実装側の変更
  （`reloadHome()` が `"home"` を送る／検索画面の 1 回目のタップは
  そもそも `sde_align` を送らない）と整合している。

## 確信度が低い点（節を分けて記載）

- `tests/test_browser.py` の `_wait_today_above_menu_bar` は
  `getBoundingClientRect()` の値をそのまま `<=` で比較しており、
  サブピクセルの丸めで稀に揺れる余地がある。既存の類似待機処理も
  同じ書き方かどうかまでは追っておらず、確信度は低い。
