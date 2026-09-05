# TODO-187 reviewer 報告

`git diff`（未コミット）を対象に読んだ。コードは直していない。

## まず、依頼で名指しされた点の結論

- **針・ラベル・`my-gauge-r-no-transition` の反映漏れは無い。**
  down / move / up / cancel / `placeGaugeWithoutTransition()` のすべてが
  `setGaugeNeedles()` / `setGaugeNoTransition()` を通っている。直に
  ループしているのは `dispGauge()` の `display = "none"` の分岐だけで、
  これも両方に効く（なお、いったん `none` にすると戻す経路が無いのは
  TODO-187 より前からの作りで、今回の変更で増えた話ではない）
- **`elGaugeR0` → `elGaugeRs` の置き換えで意味が変わった判定は無い。**
  `state.js` の初期値が `[]` なので、`elGaugeRs.length === 0` は
  「検索モード」と「`onloadHdr()` より前」の両方で、元の `!elGaugeR0` と
  同じところで真になる
- **`mondayFromClientX()` の帯の持ち回りは down / move / up で一貫している。**
  `elBar` は pointerdown でだけ入り、pointerup / cancel では
  `gaugeBarDragStart` ごと捨てられる。参照が残る経路は無い。
  pointerup から消した `document.querySelector(".my-gauge-bar")` の
  null ガードも、帯が無ければドラッグが始まらないので落として問題ない
- **`paddingBottom` の計算順は正しい。** `body_h` / `win_h` の測定より前に
  入っている。ゲージの中身（軸・針・目盛り）はすべて `position: absolute`
  なので、`dispGaugeMarks()` より前に `offsetHeight` を測っても値は変わらない
- **z-index の関係は CSS の実値と合っている**（50 < `.my-bar-content` 100 <
  `.my-menu-bar` 200）。`--my-gauge-shift` は `:root` で定義されているので、
  フッター側でも継承される

以下が指摘。

## 確信度の高い指摘

### 1. 利用者向け文書とコード内の説明が、実際と合わなくなった

- `README.md:48`「画面の**上部**に横向きのゲージを表示」
- `docs/User.md:19`「**画面上部**の横向きのゲージは…」
- `src/README.md:348`「`gauge.js` | **ヘッダ**の横ゲージ」
- `src/ytsched/webroot/static/js/week.js:134`「…・**ヘッダーの**ゲージ）を」

ゲージが上下 2 つになったので、どれも今の画面と食い違う。とくに前の 2 つは
利用者が読む文書。TODO-187 のチェックリストに文書の項目が無いので、
**範囲に入れるかどうかは main の判断**。

### 2. 「フッター側の帯にも目盛りが描かれる」ことを見るテストが無い

`tests/test_browser.py:1914` を `#week_bar .my-gauge-label` の 14 個に
絞ったため、**`dispGaugeMarks()` が上の帯にしか描かなくなっても、どの
テストも落ちない**。`.my-gauge-label` を見ている他の 2 箇所
（`_gauge_mark_left()` と `test_gauge_marks_sit_below_the_top_of_the_bar`）も
先頭＝ヘッダー側しか見ない。依頼 3 の中心にあたる動きなので、穴としては
大きい。`#footer_gauge_bar .my-gauge-label` の 14 個を足すだけで塞がる。

同じ種類の穴として、**検索モードで下のゲージが出ないこと**も見ていない。
`_assert_search_screen()`（`tests/test_browser.py:852` 付近）が
`#week_bar` の 0 件しか見ていないので、`{% if not search_mode %}` を
落としても気づけない。ここも 1 行で足せる。

### 3. 依頼 4（帯の矩形の持ち回り）は、いまのテストでは守れない

implementer が自認しているとおり
（`test_footer_gauge_drag_moves_to_the_released_week` の docstring）、
上下の帯は幅も左右位置も同じなので、`mondayFromClientX()` が上の帯の
矩形を見る実装に戻っても、このテストは通ってしまう。
**安く意味を持たせる手が一つある**: ドラッグの前に

```python
page.evaluate(
    "() => { document.querySelector('#footer_gauge_bar .my-gauge-bar')"
    ".style.margin = '0 60px'; }"
)
```

のように下の帯だけ幅を変えてからドラッグすると、上の帯の矩形で計算した
場合と移り先の週が変わるので、回帰を捕まえられる。入れるかどうかは
main の判断（テストが実装の内部事情に寄る、という見方もできる）。

### 4. `bottom` が入るまでの間、下のゲージが 42px 低い位置に出る

`my.css` の `.my-footer-gauge-bar` は `bottom: 0`、実際の値は
`main-page.js` の `onloadHdr()`（`window` の **`load`**）が入れる。
`<main>` は `visibility: hidden` で隠れているが**フッターは隠れていない**
ので、`load` が遅い（画像・アイコン待ち）ときに、メニューバーの裏に
潜り込んだゲージが一瞬見えてから 42px 飛ぶ。

CSS の既定を `bottom: 42px` にしておけば初期描画から合う。JS が入れる
インラインの値が勝つので、実測値に基づく位置合わせは今までどおり効く。
`.my-bar-content` が `#menu-sw:checked ~ .my-bar-content { bottom: 42px }`
と直書きしている前例もあるので、この書き方はこのプロジェクトから
外れてはいない。

## 確信度の低いもの（気になった程度）

- **メニューバーの高さは読み込み時に一度しか測らない。** 画面の回転や
  文字サイズの変更で `#menu_bar` の高さが変わると、下のゲージが浮くか
  重なる。ただし既存の `paddingTop`（週バー）もまったく同じ作りなので、
  この項目で新しく持ち込まれた弱点ではない。TODO.md も「読み込み時に
  一度だけでよい」と決めている
- **メニューを開いたときに隠れ切るかは `.my-bar-content` の高さ次第。**
  下のゲージは 68px（帯 60 + padding 8）で、開いたメニューの高さが
  それに届かないと、差分ラベルの上端が数 px はみ出す余地がある。
  実機（幅 390px）では隠れたと報告があるので、確度は低い
- **`main.html` にゲージのマークアップが 2 回ある。** 「中身は上と全く
  同じ」が前提なので、片方だけ直す事故が起きうる。`{% include %}` に
  切り出す手はあるが、上の方には TODO-066 / 072 / 078 のコメントが
  ぶら下がっていて、切り出すと説明の置き場所を決め直すことになる。
  いま直すほどではないと思う
- **`document.body.style.paddingBottom` を 2 回書いている**
  （`main-page.js:356` と `:365`）。1 回目はすぐ上書きされるので、
  読み手が「なぜ 2 回?」と迷う。検索モードでは 1 回目だけが効く、という
  作りではあるので誤りではない
- `scrollToId()` の `sde_align == "bottom"`（`nav.js:355`）は
  `menu_bar_h + 30px` しか避けないので、下のゲージ 68px の裏に対象が
  隠れる計算になる。ただしこの経路に入るのは
  `edit.html` が `search_str` 有りのときに `bottom` を渡す場合だけで、
  そのときは検索モード＝ゲージが出ない。`search_str` が不正な正規表現で
  `search_mode` が false になるときだけ噛み合うので、ほぼ起きない
