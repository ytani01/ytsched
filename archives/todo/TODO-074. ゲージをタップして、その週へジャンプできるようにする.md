# TODO-074. ゲージをタップして、その週へジャンプできるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + wording |
| 実施 | Opus 5 / effort high | implementer + verifier + wording |
| 消費 | output 11,004 / cache_creation 260,697 / 概算 $3.3 |
|      | main 40% + verifier 30% + implementer 30%（料金の割合） |

## きっかけ

ヘッダの横ゲージ（TODO-058）は、いま見ている週が今週からどのあたりに
あるかを出すだけで、そこから移動はできなかった。目盛りを見て「3 ヶ月
先」と分かっても、週送りかスワイプで辿るしかない。タップでその週へ
直接飛べるようにした。ドラッグでの追従は要らない。

## やったこと

ゲージの帯（`.my-gage-bar`）をタップ・クリックすると、その位置が指す
週の月曜へ移る。

- `src/ytsched/webroot/static/js/my.js`
  - `xPercent2days()` を足した。`days2xPercent()`（対数の目盛り）の
    逆算で、同じ定数（`DAYS_GAGE_K`・`DAYS_GAGE_MAX`）を使う
  - `gageBarClickHdr()` を足した。帯の左端を 0%・右端を 100% として、
    中央からの割合を `xPercent2days()` に渡し、今週の月曜からの日数を
    出す。その日を含む週の月曜へ `scrollToDate()` で移る
- `src/ytsched/webroot/templates/main.html` — `.my-gage-bar` に
  `onmousedown="gageBarClickHdr(event);"` を足した
- `src/ytsched/webroot/static/css/my.css` — `.my-gage-bar` に
  `cursor: pointer` と、押している間の `:active` を足した

### ジャンプ先は週の月曜

ゲージは週単位の表示なので、逆算した日をそのまま使わず、その週の月曜へ
丸める。針の位置とも一致する。

### 範囲の頭打ちは設けない

端は約 30 年先・30 年前になる。誤って飛んでも戻るボタンで戻れるので、
上限は設けなかった。実際に端をクリックすると 2055 年・1996 年へ飛ぶ
（verifier が確認）。

### 既存のスワイプと同じ仕組みに乗せた

`mouseDownHdr()` は `window` に capture で登録されていて、
`onmousedown` 属性を持つ要素（日付セル・ボタン）を
`el.closest("[onmousedown]")` で拾い、動かずに離したときだけ
`mouseUpHdr()` から呼び直す（TODO-064）。`.my-gage-bar` にも同じ
`onmousedown` を付けるだけで、**動かさずに離せばジャンプ、横に動かせば
今までどおり週送り**になった。`stopPropagation()` の類は要らなかった。

`gageBarClickHdr()` は `event.target` / `event.currentTarget` に頼らず、
`.my-gage-bar` を取り直している。`mouseUpHdr()` が `mouseup` の event を
そのまま渡して呼ぶため、`target` が指す要素が呼び出し経路によって
食い違うことがある。

### 押している間の色

はじめはボタンと同じ黄色を流用したが、帯が一色に塗り潰され、押している
間だけ目盛りと針が読めなくなった（verifier の指摘）。薄い半透明の白
（`rgba(255, 255, 255, 0.2)`）に変えた。目盛りと針は見えたまま、押した
ことは分かる。

## テスト

- `tests/test_browser.py`
  - `test_x_percent2days_inverts_days2x_percent()` — `days2xPercent()`
    と往復させて元の日数に戻るか
  - `test_gage_bar_click_moves_to_the_tapped_week()` — 帯をクリックして
    3 週間先の月曜へ移るか

`mise run lint` / `test`（457 件）が通る。

verifier の報告は
[archives/agents/TODO-074/verifier-report.md](../agents/TODO-074/verifier-report.md)。
実際にブラウザで中央付近・左右・両端をクリックして移動先を突き合わせ、
すべて月曜になることを確認している。ゲージの上からの横ドラッグでの
週送り、日付セル・ボタンのクリック、検索モード（週バーごと出ない）でも
退行は無かった。分担の理由は
[archives/agents/TODO-074/README.md](../agents/TODO-074/README.md)。
