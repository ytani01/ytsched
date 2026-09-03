# TODO-182. ゲージを上詰めに戻して、高さを 50px に広げる

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Sonnet 5 / effort medium | main + verifier（2 回） |
| 消費 | output 52,488 / cache_creation 196,197 / 概算 $2.3 |
|      | main 69% + verifier 31%（料金の割合） |

分担の理由と報告は [archives/agents/TODO-182/](../agents/TODO-182/README.md)。

## きっかけ

TODO-178 でヘッダーの横ゲージをスライダーにしたとき、指で操作しやすいよう
帯を 33px から 44px へ広げた。広げたぶんを下に空けると目盛りが指で隠れて
読めない、として中身（軸・今週のしるし・針・目盛り）を下詰めにし、空きを
上に置いた（`--my-gauge-shift: 12px`）。

実際に使うと、指で押す余地は目盛りの下にあるほうがよい、という利用者の
判断。上詰めに戻し、帯をさらに 50px へ広げて下の余地を増やす。

## やったこと

`src/ytsched/webroot/static/css/my.css` だけ。

- `.my-gauge-bar` の高さを 44px → 50px
- `--my-gauge-shift` を 12px → **0px**（中身を上詰めに戻す）。
  帯 50px・中身 32px なので、目盛りの下に 18px の余地が残る
- 上記変数の直前コメントを、下詰めの説明から上詰めの説明へ書き直した

各要素の `top`（`.my-gauge-axis` = `calc(19px + var(--my-gauge-shift))`
など）は触っていない。body の `padding-top` は `main-page.js` が週バーの
実測高を入れるので、帯が 6px 高くなったぶんは自動で追従する。

### 単位なしの 0 で目盛りが潰れた（verifier の 1 回目で発覚）

最初 `--my-gauge-shift: 0`（単位なし）にしたところ、
`top: calc(19px + var(--my-gauge-shift))` が「長さ ＋ 数値」になって
CSS として不正になり、宣言ごと無効化されて軸・今週のしるし・目盛り
ラベルの `top` が 0 へ落ちた。14 個の目盛りが帯の最上段に張り付き、
針の上に出る差分ラベル「±0」と重なって読めない状態。

`0px` にして解決。`.my-gauge-r` だけは `top: var(--my-gauge-shift)` で
`calc()` を使っておらず、単位なしの 0 でも有効なため、たまたま無事
だった。コメントに「0 でも単位を落とさない（calc で長さと数値は
足せない）」を書き添えた。

## テスト

- `tests/test_browser.py` に
  `test_gauge_marks_sit_below_the_top_of_the_bar` を 1 件追加。
  `.my-gauge-label` の bounding_box が帯の上端から十分下がり
  （`> 10px`）、帯の下端との間に余地が残る（`> 8px`）ことを見る。
  単位落ちで `top` が 0 に潰れると前者が落ちる
- verifier が、この新テストを `--my-gauge-shift: 0`（単位なし）の
  webroot コピーに対して走らせ、`label.y - bar.y = 0.00` で
  実際に落ちることを確認（tracked ファイルは書き換えず）
- `mise run lint` ○、`uv run pytest` ○ **674 passed**
- verifier が playwright（幅 360〜600px）で実測。±0 は針の上、
  目盛りは帯の下寄り（top 22〜32）、目盛り下端と帯下端の間に 18px、
  検索モードでは帯ごと消え、console エラー 0 件

## 振り返り

- **CSS カスタムプロパティを `calc()` に混ぜるなら、0 でも単位を
  付ける。** `--x: 0` は `calc(19px + var(--x))` を丸ごと無効化する。
  1 ファイル 3 行の変更でも、実装した本人はテスト緑で「できた」と
  してしまう種類の抜けで、verifier をブラウザで動かす担当として
  分けた効果がそのまま出た（TODO-017 の基準どおり）
- **縦位置を見るテストが無かったので、674 件すべて緑のまま壊れた
  状態が通った。** 横位置（`test_gauge_marks_are_drawn_at_the_same_position`）
  は見ていたが、縦は素通しだった。今回足したテストで、単位落ちと
  `calc()` 無効化の両方をこの経路で捕まえられる
