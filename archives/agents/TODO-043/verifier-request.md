# verifier への依頼（TODO-043）

## 何を変えたか

ゲージの針（▶）と基準線（＝）を、Font Awesome のアイコンから
**インライン SVG** に置き換えた。**見た目は変えないつもり**で、大きさは
以前のアイコンの字面の実寸に合わせてある。

- `main.html` — `<div><i class="fa-caret-right fa-2x"></i></div>` →
  `<svg id="gage_r" viewBox="0 0 14 21"><polygon .../></svg>`、
  基準線も同様に `<rect>` 2 つの SVG に
- `main.html` — `elGageRBase.style.bottom` を `centerY - 9` から
  **`centerY` に戻した**
- `my.css` — TODO-042 で入れた補正 2 つ（`--fa-width: auto`、
  `.my-gage-r .my-gage-text` の `translate(-0.127em, 50%)`）を削除。
  `.my-gage-r` / `.my-gage-base` に `width` / `height` / `fill` と
  `transform: translateY(50%)` を指定

### 大きさの根拠

`fa-solid-900.woff2` から fontTools でグリフの輪郭を取り出して決めた
（unitsPerEm = 512）。

| | 字面（units） | 実寸 | SVG |
|---|---|---|---|
| `fa-caret-right`（`fa-2x` = 36px） | 194 x 298 | 13.6 x 21.0px | 14 x 21 |
| `fa-grip-lines`（`fa-xs` = 13.5px） | 448 x 192 | 11.8 x 5.1px | 12 x 5 |

基準線の棒は 64 units（1.7px）、隙間も 64 units（1.7px）、角丸 32 units
（0.85px）。

### 位置合わせの考え方

以前は、大きさの違う 2 つのアイコンの `<i>` に同じ
`transform: translate(0%, 50%)` をかけていたため、下へずれる量が
それぞれ違った。その差を吸収していたのが `centerY - 9`。

今回は `<svg>` 自身に `translateY(50%)` をかけている。SVG は
`width` / `height` が確定した箱で、その箱＝図形そのものなので、
**針も基準線も「図形の中心が `bottom` の値に来る」で揃う**。だから
`centerY - 9` は要らなくなった、というのが実装側の見立て。

## 確かめてほしいこと

比較対象は `HEAD`（`5c7d18f`。Font Awesome 版）と、いまの作業ツリー
（SVG 版）。

1. **針の左端が画面の左端（x = 0）に来ているか。** TODO-042 で
   そこに合わせたので、動いていないこと
2. **針と基準線の重なり方が変わっていないか。** ここが今回いちばん
   怪しい。`centerY - 9` は利用者が実機で見て決めた値で、SVG 版では
   「図形の中心どうしを揃える」に変わっている。**変わっているなら、
   どう変わったかを数値と拡大画像で示してほしい**（直すかどうかは
   利用者が決める）
3. 針・基準線の**縦位置**（`dispGage()` が決める）と、**目盛りの
   ラベル**が変わっていないか
4. **ゲージ以外の画面に差が出ていないか**

## 撮り方

TODO-042 の `archives/agents/TODO-042/verifier-report.md` に、この画面を
静的化して撮る手順が書いてある。**先にそれを読むこと。** とくに:

- `window.addEventListener('load', onloadHdr);` を丸ごと消すと、ゲージの
  縦位置が設定されず針が画面外へ消える。`onloadHdr` の後半（実際に
  スクロールする部分）だけを止める
- 静的サーバでは `doPost()` の送り先が無いので、スクロールを走らせると
  再帰的に発火してタイムアウトする
- **針と基準線を重ねて見るには、静的化した `onloadHdr` の最後で
  `dispGage('<今日の日付>')` を呼ぶ**（`days2yOffset(0)` が 0 を返すので、
  針の `bottom` が基準線と同じ値になる）

## 決まり

- アプリを起動するときは `--datadir` に必ず一時ディレクトリを指定する
- 自分で立てたプロセスは、`pgrep` で PID を確かめてから kill する
  （`pkill` はパターンで自分のシェルを巻き込む）
- **コードは直さない。** 見つけたことは報告する

## 報告

`archives/agents/TODO-043/verifier-report.md` に書く。
スクリーンショットは `~/tmp/playwright-mcp/` に `todo043_` で始まる
名前で保存し、チャットにも添付すること。
