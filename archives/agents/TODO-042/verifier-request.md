# TODO-042 verifier への依頼

## 何を確かめてほしいか

`src/ytsched/webroot/static/css/my.css` の `.my-gage-text` に
`--fa-width: auto;` を 1 行足した。これで、一覧画面の左端にあるゲージの
針（▶ = `#gage_r`、`fa-caret-right fa-2x`）と基準線（`#gage_r_base`、
`fa-grip-lines fa-xs`）が、左端に寄って表示されるようになったかを見てほしい。

背景は `TODO.md` の TODO-042 の節にある。Font Awesome 7 がすべての
アイコンに `width: 1.25em` と `text-align: center` を付けるため、幅
0.5em の `fa-caret-right` が箱の中央に置かれ、`left: 1px` で決めた位置から
約 13.5px 内側（右）へずれていた、という見立て。

**利用者は「画面を見て判断する」と決めている。スクリーンショットは必ず
撮ること。** 数値（`getBoundingClientRect()`）も出せるなら添えてよいが、
画面の代わりにはしない。

## 見てほしい点

1. 針（▶）の左端が、直したあとに `left: 1px` 付近まで戻っているか
2. 基準線（`#gage_r_base`、`left: 3px`）も同じように寄ったか
3. 針・基準線の**縦位置と、目盛りのラベル**（`#gage_r0`, `#gage_r1`, …）が
   直す前と変わっていないか。`--fa-width` は幅の指定なので、縦は動かない
   はずだが確かめること
4. ゲージ以外に変わったところが無いか。`.my-gage-text` はゲージの中でしか
   使っていないはずだが、画素で比べて差がゲージのまわりだけに収まって
   いるかを見る

## 直す前と直したあとの比べ方

**HTML は変えていない。変えたのは CSS 1 ファイルだけ**なので、CSS を
差し替えるだけで両方撮れる。`git stash` は要らない。

```sh
git show HEAD:src/ytsched/webroot/static/css/my.css > <一時ディレクトリ>/my-before.css
```

## 撮り方（TODO-040 で通した手順）

詳しい手順は `archives/agents/TODO-040/verifier-request.md` の
「1. 画素単位の比較」と `archives/agents/TODO-040/verifier-report.md` に
ある。**そちらを読んでから始めること。** 要点だけ再掲する。

- `main.html` は `load` で JavaScript が今日の位置までスクロールするので、
  そのまま撮ると真っ白になることがある。`curl` で HTML を取り、
  `window.addEventListener('load', onloadHdr);` を空にするなどして
  静的な HTML にしてから `python3 -m http.server` で配信して撮る
- **ただしゲージの縦位置は `my.js` が `load` で書き換えている。**
  `onloadHdr` を止めると針が既定の位置のままになる可能性がある。
  止めたときに針と基準線が画面に出るかを先に確かめ、出ないようなら
  スクロールの部分だけを止めるなど、**針が見える形を自分で作ること**
  （どうやったかを報告に書く）
- `chromium --headless --disable-gpu --hide-scrollbars --no-sandbox
  --virtual-time-budget=5000 --window-size=<幅>,4000 --screenshot=…`
- **呼び出しごとに `--user-data-dir=<固有のディレクトリ>` を指定する。**
  指定しないとプロファイルのロック待ちで無期限にハングする（TODO-040 で
  実際に起きた）
- 幅は 412 と 740 の 2 つ。ゲージが見えていれば一覧の画面だけでよい
- 画素の比較は `compare -metric AE 前.png 後.png null:`

## テストデータ

ゲージは今日からの日数で位置が決まるので、一覧に中身が要る。**今日を
またぐ範囲**（過去・今日・未来）に予定を入れること。`~/ytsched/data` は
使わず、`--datadir` に一時ディレクトリを指定する。

## スクリーンショットの置き場所

`~/tmp/playwright-mcp/` に、内容の分かる名前（`todo042_before_412.png`
のような）で保存し、**報告にフルパスを書くこと**。main がチャットに
添付して利用者に見せる。

## 報告

`archives/agents/TODO-042/verifier-report.md` に書く。返事は「終わったか・
報告ファイルのパス・判断が要る点」を 5 行以内で。

**コードは直さないこと。** 見つけたことは報告するだけでよい。

---

# 3 回目の依頼（針と基準線の重なりを見る）

CSS は 2 回目から変えていない。撮り直しだけを頼む。

利用者が「三角形と `＝`（`fa-grip-lines`）の正しい位置関係はこれ」という
画面を出してきた（`~/tmp/image.png`）。main が実測したところ、これは
**TODO-040 のバージョンアップ前（Font Awesome 5）の画面**だった。
fontTools で測った寸法が一致する。

- FA5 の `caret-right`: lsb = 0、字面幅 0.330em
  （FA7 は lsb = 0.127em、字面幅 0.374em）
- FA5 の `grip-lines`: 字面幅 **1.0em**（FA7 は 0.875em）
- 利用者の画像の実測: 三角の字面 x = 1〜12、`＝` の字面 x = 3〜16。
  上の FA5 の値どおり

**利用者の画像では、針が基準線と同じ高さに来ていて、`＝` が三角に
重なっている。** 2 回目までに撮った画面は針がもっと上にあり、この
重なり方が分からない。

## 撮ってほしいもの

**針が基準線と重なる状態（今日を表示している状態）のゲージ付近の拡大。**
次の 2 つを、同じ倍率・同じ切り出し範囲（x = 0 を含むこと）で撮り、
並べて比べられるようにする。

1. **今の作業ツリー**（FA7 + `--fa-width: auto` + `left: 0px` +
   `translate(-0.127em, 50%)`）
2. **TODO-040 の 1 つ前の版**（`e146a11^`。FA5・Bootstrap 4.5 の一式）。
   利用者が「正しい」と言っている状態

2 は `git archive e146a11^ | tar -x -C <一時ディレクトリ>` などで一式を
取り出し、そこから `ytsched webapp -r <その webroot>` で起動する
（Bootstrap も 4.5 に戻るので、ゲージ以外の見た目が違うのは構わない）。

針を基準線に重ねるやり方は任せる。`dispGage()` に今日の日付を渡す、
`#gage_r` の `bottom` を `#gage_r_base` と同じ値にする、などでよい
（どうやったかを報告に書くこと）。

## 測ってほしい数値

1 と 2 のそれぞれで、画素を直接読んで次を表にする。

- 三角（▶）の字面の 左端・右端・上端・下端の x, y
- `＝`（grip-lines）の字面の 左端・右端・上端・下端の x, y
- 三角の右端に対して `＝` の右端が何 px はみ出しているか

## 保存先

`~/tmp/playwright-mcp/` に `todo042c_` で始まる名前で。前のファイルは
上書きしない。フルパスを報告に書くこと。
