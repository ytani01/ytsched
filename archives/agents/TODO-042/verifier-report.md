# TODO-042 verifier 報告

比較対象: 現在の作業ツリー（`--fa-width: auto;` 追加後、`new`）と、
`git show HEAD:src/ytsched/webroot/static/css/my.css`（追加前、`old`）。
`old` 用に `webroot` を丸ごとコピーし、`static/css/my.css` だけを
`HEAD` の版に差し替えて使った（HTML・JS は共通）。

作業場所（すべて一時ディレクトリ、`~/ytsched/data` は未使用）:
`/tmp/claude-649/-home-ytani-work-ytsched/d80b5f18-f638-4ed7-a631-1ede9aa7191b/scratchpad/verify042/`

## 手順

1. `old_webroot`（css だけ HEAD 版）と現行 `webroot` を、それぞれ
   `--datadir` に一時ディレクトリを指定して別ポートで起動
   （旧: `-p 18101 -r old_webroot -w old_datadir`、新: `-p 18102
   -w new_datadir`）
2. 両方の datadir に同じ内容のテストデータを直接 `.jsonl` として投入
   （今日をまたぐ範囲。下記「テストデータ」）
3. `curl` で一覧 HTML を取得し、Python スクリプトで静的化
   - `visibility: hidden;` → `visibility: visible;`
   - **`window.addEventListener('load', onloadHdr);` をそのまま消すと
     ゲージの縦位置（`bottom`）が一切設定されず、針が画面外に消えた**
     （最初に試して確認: `test_check.png`）。依頼書の「針が見える形を
     自分で作ること」に従い、`onloadHdr` 本体のうち `scrollToDate(...)`
     以降（実際の画面スクロールを起こす部分）だけを
     `dispGage(date_from_str); elMain.style.visibility = "visible";`
     に差し替えた。ゲージの縦位置を決める前半部分（`gage_r0`〜`r15`・
     `gage_r_base` の `bottom` 設定）はそのまま実行させている
   - 依頼書にある「静的サーバ上で `scrollToDate` の `smooth`/`instant`
     スクロールを走らせるとタイムアウトする」現象を実際に再現した
     （`chromium` が `--virtual-time-budget=5000` でも終わらず
     `timeout 40` で exit 124。静的サーバでは `doPost` の POST 先が
     存在せず、スクロールイベントが再帰的に発火し続けたためと見立てる）
4. `python3 -m http.server` で配信（`ytsched/static` へのシンボリック
   リンクを配信ルート下に作成）
5. `chromium --headless --disable-gpu --hide-scrollbars --no-sandbox
   --virtual-time-budget=6000 --window-size=<幅>,4000
   --user-data-dir=<呼び出しごとに固有のディレクトリ>
   --screenshot=…` で撮影
6. `compare -metric AE 旧.png 新.png null:` で比較
7. 数値確認は、`</head>` の直前に `getBoundingClientRect()` を呼んで
   `document.title` に JSON を書き込む `<script>` を挿し込み、
   `chromium --dump-dom` で `<title>` を読んだ

### テストデータ（今日 2026-08-24 をまたぐ）

- 2026-08-20（過去）: 通常の予定
- 2026-08-24（今日）: 通常の予定
- 2026-08-28（未来）: 時刻未定の予定

## 1. 針（▶）の左端が `left: 1px` 付近まで戻ったか — ○

`getBoundingClientRect()` の実測値（`old` = 直す前、`new` = 直したあと）。

| 要素 | | `left` | `width` |
|---|---|---|---|
| `#gage_r`（▶ 本体、コンテナ div） | old | 1px | **45px** |
| | new | 1px | **18px** |
| `#gage_r_base`（基準線、コンテナ div） | old | 3px | **16.875px** |
| | new | 3px | **11.8125px** |

`#gage_r` は `.my-gage-r { left: 1px; }` のみで幅を指定していない
（`position: fixed` で `left` だけ設定 → 幅は中身に合わせて縮む）ので、
このコンテナ div の幅＝アイコン自身の幅になる。

- 直す前は `width: var(--fa-width, 1.25em)` が効いて `45px`
  （`1.25em × fa-2x` = `1.25 × 18px × 2 = 45px`、TODO.md の見立てと一致）。
  この箱の中でグリフが `text-align: center` により中央寄せされるため、
  見た目のグリフは左に `(45 − 18) / 2 = 13.5px` 内側へ寄っていた
  （TODO.md の「約 13.5px」と一致）
- 直したあとは `--fa-width: auto` により箱の幅がグリフ自身の幅
  （`18px` ≈ `0.5em × fa-2x`）まで縮み、中央寄せの余白が無くなるので、
  グリフは箱の左端＝`left: 1px` の位置にそのまま出る

スクリーンショットの拡大でも、直す前は針が日付ブロックの左端に重なって
中に食い込んでいたのが、直したあとは日付ブロックの外（左の余白）に
完全に収まっている（`todo042_before_gage_zoom.png` /
`todo042_after_gage_zoom.png`）。

## 2. 基準線も同じように寄ったか — ○

`#gage_r_base` も同じ理屈で `16.875px → 11.8125px` へ縮み、
差は `(16.875 − 11.8125) / 2 ≈ 2.53px`。TODO.md の見立て
「約 2.5px」と一致。

## 3. 縦位置・目盛りラベルが変わっていないか — ○

| 要素 | `top`（old / new） | 一致 |
|---|---|---|
| `#gage_r` | 1736.5px / 1736.5px | ○ |
| `#gage_r_base` | 1871.5px / 1871.5px | ○ |
| `#gage_r0`（-30y ラベル） | 1597px / 1597px、`left`/`width` とも一致 | ○ |
| `#gage_r1`（-10y ラベル） | 1631px / 1631px、`left`/`width` とも一致 | ○ |
| `#gage_r2`（-3y ラベル） | 1667px / 1667px、`left`/`width` とも一致 | ○ |

ラベル（`gage_r0`〜）は `.my-gage-text` は付くが Font Awesome アイコンでは
ないため `--fa-width` の影響を受けず、`left`・`width`・`top` とも
1 ピクセルも変わっていない。縦位置・目盛りとも見立てどおり無変化。

## 4. ゲージ以外に変わったところが無いか — ○

一覧を 412 幅・740 幅で撮影し `compare -metric AE` で比較。

| 幅 | 総画素数 | 違う画素（AE） |
|---|---|---|
| 412 | 1,648,000 | **480**（0.029%） |
| 740 | 2,960,000 | **480**（0.016%） |

差分のある画素の座標を Python（PIL）で直接抽出したところ、
両方の幅とも **x: 3〜32px、y: 1904〜2025px の 1 か所だけ**
（ゲージの針・基準線の領域）に収まっていた。それ以外の画素は
1 つも変わっていない。

`chromium` 自身の揺らぎも確認: 同じ `new` 版を 2 回撮って比較すると
AE = **0**（今回のテストデータには読み込み中スピナーが写っていないため、
TODO-040 のときと違い揺らぎ自体が出ない）。よって AE = 480 はすべて
CSS の変更によるもの。

## スクリーンショット

`~/tmp/playwright-mcp/` に保存（チャットにも添付済み）。

- `todo042_before_412.png` / `todo042_after_412.png`（一覧全体、412 幅）
- `todo042_before_740.png` / `todo042_after_740.png`（一覧全体、740 幅）
- `todo042_before_gage_zoom.png` / `todo042_after_gage_zoom.png`
  （ゲージ付近の拡大切り出し。針が日付ブロックへ食い込んでいたのが
  直っている様子が分かる）

## プロセスの後始末

自分で立てたプロセス（`ytsched webapp -p 18101/18102`、
`python3 -m http.server 18201/18202`、それぞれの子プロセス）を
`ps aux` で PID を確認してから `kill` し、全て終了を確認した。
利用者のサーバ（`-p 12345`、PID 134716）は触っていない。

## 見つかった不具合・気になった点

- 実装に問題は見つからなかった。`--fa-width: auto;` 1 行で、針・基準線の
  位置だけが計算どおりに直り、縦位置・ラベル・その他の画面は 1 画素も
  変わっていない
- 依頼書の撮影手順（`window.addEventListener('load', onloadHdr);` を
  空文字に置換するだけ）どおりにやると、ゲージの縦位置が設定されず針が
  画面外へ消える。今回は `onloadHdr` の後半（実際にスクロールする部分）
  だけを止める形に変えて対応した（上記「手順」参照）。次に同種の作業を
  するときのために書いておく

---

## 2 回目の確認（利用者の指示: 針の左端を x = 0 に）

比較対象は 1 回目と同じ `HEAD`（`old2`。`--fa-width` の変更も含めて
一切当たっていない版）と、今回の作業ツリー（`new2`。`--fa-width: auto;`
に加えて `.my-gage-r { left: 0px; }` と
`.my-gage-r .my-gage-text { transform: translate(-0.127em, 50%); }` を
足した版）。手順・撮り方（`onloadHdr` 後半だけを止める静的化）は
1 回目と同じ。作業場所も同じ一時ディレクトリを使い回した
（`old_datadir` / `new_datadir` のテストデータも同じ）。

### 1. 針の字面の左端が x = 0 に来ているか — ○

`after2_412.png` を Python (PIL) で直接読み、針の三角形がある行
（y = 1904〜1926、背景を除く最初の非背景画素）を確認した。

```
y=1905 leftmost_nonwhite=0 color=(221,221,221)
y=1906〜1925          leftmost_nonwhite=0 color=(208,208,208)  ※三角の本体（垂直な背側）
y=1926 leftmost_nonwhite=1 color=(227,227,227)
```

**20 行にわたって x = 0 が三角の本体（`opacity: 0.2` の一様な階調
`rgb(208,208,208)`）で、値が途中で変わらず一定**なので、三角の
左端（垂直な背側）がちょうど x = 0 に来ていて、かつ**そこで切れて
いない**（切れているなら、より外側の画素だけが薄いアンチエイリアス
値になり、本体の一定値が画面の端で急に始まるはずだが、実際は
x = 0 の時点で既に本体の値になっている＝もう少し左まで自然に
伸びている形の縁が x = 0 にちょうど乗っている、と読める）。

`getBoundingClientRect()` の値でも確認: アイコン自身の箱
（`#gage_r i`）は `left: -4.572px, width: 18px` で、
`translate(-0.127em, 50%)` の `-0.127em × 36px = -4.572px` が
そのままボックスの `left` に反映されている。ボックス内で字面が
`lsb = 65/512em ≈ 0.127em ≈ 4.572px` の位置から始まる仕様
（依頼書の見立て）なので、`-4.572 + 4.572 = 0` で字面の左端が
画素の x = 0 に来る計算と、実測（画素の leftmost = 0）が一致した。

拡大画像（`todo042b_after_gage_zoom_x0.png`、x = 0 を含む範囲で
切り出し）でも、針の左端がちょうど画面の左端に接しており、
はみ出て切れている様子は無い。

### 2. 縦位置・ラベル・基準線が変わっていないか — ○

`getBoundingClientRect()` 実測（`old2` = `HEAD`、`new2` = 今回）。

| 要素 | | `top` | `left` | `width` |
|---|---|---|---|---|
| `#gage_r`（コンテナ div） | old2 | 1736.5px | 1px | 45px |
| | new2 | 1736.5px | **0px** | **18px** |
| `#gage_r i`（アイコン自身の箱） | old2 | 1754.5px | 1px | 45px |
| | new2 | 1754.5px | **-4.572px** | 18px |
| `#gage_r_base` | old2 | 1871.5px | 3px | 16.875px |
| | new2 | 1871.5px | 3px | 11.8125px |
| `#gage_r0`（-30y ラベル） | old2 / new2 とも | 1597px | 1px | 19.453125px |
| `#gage_r1`（-10y ラベル） | old2 / new2 とも | 1631px | 1px | 19.453125px |
| `#gage_r2`（-3y ラベル） | old2 / new2 とも | 1667px | 1px | 13.90625px |

- `#gage_r` の `top` は `1736.5px` で 1 回目と完全一致。縦位置は
  今回の変更（`left` と `transform` の X 成分のみ）で動いていない
- `#gage_r_base` の `top`・`left`・`width` は 1 回目の報告と同じ数値
  （`16.875px → 11.8125px`、`left: 3px` は不変）。今回の変更は
  `.my-gage-r .my-gage-text` にしか掛からないので、基準線側は無変化
- ラベル 3 つは `old2`/`new2` で 1 ピクセルも変わっていない

拡大画像（`todo042b_after_base_zoom.png` / `todo042b_before_base_zoom.png`）
でも基準線（`=`）の位置は見た目で変わっていない。

### 3. ゲージ以外に差が出ていないか — ○

`before2_*.png`（`HEAD`）と `after2_*.png`（今回）を
`compare -metric AE` で比較。

| 幅 | 総画素数 | 違う画素（AE） |
|---|---|---|
| 412 | 1,648,000 | **462**（0.028%） |
| 740 | 2,960,000 | **462**（0.016%） |

同じ `new2` 版を 2 回撮って比較した揺らぎは AE = 0（1 回目と同じ、
今回のテストデータには読み込み中スピナーが写っていないため）。よって
AE = 462 は全て CSS の変更によるもの。

差分画素の座標を Python（PIL）で抽出したところ、両方の幅とも
**x: 0〜32px、y: 1904〜2025px の範囲だけ**に収まっていた。行ごとの
差分画素数を数えると、2 つの塊に分かれている。

- **y = 1904〜1926（山型に増減、ピークで 1 行 28 画素）** — 針
  （`#gage_r`）の変化。`left: 1px → 0px` と `transform` による移動分
- **y = 2020〜2025（1 行あたり 7〜8 画素）** — 基準線（`#gage_r_base`）
  の変化。これは **1 回目の `--fa-width: auto` による箱の縮小
  （`16.875px → 11.8125px`）そのもの**で、今回新たに追加した
  `left: 0px` や `transform` は基準線に掛からないので、2 回目で
  新しく生じた差ではない（比較の基準を `HEAD` に取っているため、
  1 回目の差がそのまま乗って見えている）

それ以外の画素は 1 つも変わっていない。ゲージ以外への影響は無し。

### スクリーンショット

`~/tmp/playwright-mcp/` に、1 回目のファイルを上書きせず保存
（チャットにも添付済み）。

- `todo042b_before_412.png` / `todo042b_after_412.png`（一覧全体、412 幅、
  比較の基準は `HEAD`）
- `todo042b_before_740.png` / `todo042b_after_740.png`（一覧全体、740 幅）
- `todo042b_before_gage_zoom_x0.png` / `todo042b_after_gage_zoom_x0.png`
  （針の周辺、x = 0 を含む範囲で切り出し。針が画面の左端に接しており、
  はみ出て切れていないことが分かる）
- `todo042b_before_base_zoom.png` / `todo042b_after_base_zoom.png`
  （基準線「=」の周辺。位置が変わっていないことが分かる）

### プロセスの後始末

自分で立てたプロセス（`ytsched webapp -p 18101/18102`、
`python3 -m http.server 18201/18202`、それぞれの子プロセス）を
`ps aux` で PID を確認してから `kill` し、全て終了を確認した。
利用者のサーバ（`-p 12345`、PID 134716）は触っていない。

### 見つかった不具合・気になった点

- 実装に問題は見つからなかった。針の字面の左端は画素で見ても
  ちょうど x = 0 に来ており、はみ出て切れてもいない。縦位置・ラベル・
  基準線は無変化。ゲージ以外への影響も無い

---

## 3 回目の確認（針と基準線の重なりを見る）

比較対象: **今の作業ツリー**（`new3`。FA7 + `--fa-width: auto` + `left: 0px` +
`translate(-0.127em, 50%)`）と、**`e146a11^`**（`old3`。FA5・Bootstrap 4.5
の一式、利用者が「正しい」と言っている状態）。`git archive e146a11^ | tar -x`
で一式を取り出し、`ytsched webapp -r <old3 の webroot> -w <old3 用一時 datadir>`
で起動（新側は `-w <new3 用一時 datadir>` のみ、webroot は既定＝作業ツリー）。
テストデータは 1・2 回目と同じ「今日をまたぐ範囲」（過去 2026-08-20・今日
2026-08-24・未来 2026-08-28）を新規に投入。

作業場所（一時ディレクトリ、`~/ytsched/data` は未使用）:
`/tmp/claude-649/-home-ytani-work-ytsched/d80b5f18-f638-4ed7-a631-1ede9aa7191b/scratchpad/verify042c/`

### 撮り方

1・2 回目と同じ手順（`onloadHdr` の後半だけを静的化）を踏襲。**今回は
「針を基準線に重ねる」ため、静的化した `onloadHdr` の最後で
`dispGage('2026-08-24')`（今日の日付）を呼ぶように差し替えた。** `days2yOffset(0)`
は `0` を返す実装（`my.js`）なので、`dispGage(今日)` を呼べば
`#gage_r` の `bottom` が `#gage_r_base` と同じ値（`centerY`）になり、
針と基準線が同じ高さに揃う。`old3`・`new3` とも同じやり方で静的化・
同じ日付を渡した。

- `chromium --headless --disable-gpu --hide-scrollbars --no-sandbox
  --virtual-time-budget=6000 --window-size=412,4000
  --user-data-dir=<呼び出しごとに固有のディレクトリ> --screenshot=…`
- 静的サーバ（`python3 -m http.server`）配下に `ytsched/index.html`
  （静的化した HTML）と `ytsched/static -> webroot/static` のシンボリック
  リンクを置き、`http://127.0.0.1:<port>/ytsched/` で配信
- 数値は `getBoundingClientRect()` を `<script>` で `</head>` の直前に
  挿し込み、`document.title` に JSON で書き出して `chromium --dump-dom`
  で読んだ（1・2 回目と同じやり方）

### 数値（`getBoundingClientRect()`、`old3` / `new3` とも同じ手順・同じ日付で計測）

`#gage_r`（針のコンテナ）の `style.bottom` と `#gage_r_base`（基準線の
コンテナ）の `style.bottom` は、**`old3`・`new3` とも文字列として完全一致**
（`"1968.5px"`）。`getBoundingClientRect()` の `top`/`bottom` も両者で
1 ピクセルも違わない。

| 要素 | | `top` | `bottom` |
|---|---|---|---|
| `#gage_r` | old3 / new3 とも | 1852.5px | 1888.5px |
| `#gage_r_base` | old3 / new3 とも | 1871.5px | 1888.5px |

→ **針の縦位置は基準線と完全に一致しており、`old3`・`new3` で差が無い**
（`dispGage(今日)` の効果は両バージョンで同じ）。

字面の画素そのもの（`compare` ではなく PIL で直接、ゲージ付近
x=0〜20 の範囲を 1 行ずつ読み、各行の非白画素の左端・右端を求めた。
`old3`/`new3` は同一バッチ内の別スクリーンショットなので、画像内の絶対
y 座標はこの表の中でのみ比較できる。同じ y 範囲に三角と `＝` が収まって
いること・右端の飛び出し量が縮んだことが要点）。

| | 三角（▶）右端の頂点 | `＝`（grip-lines）右端 | 飛び出し量 |
|---|---|---|---|
| old3（FA5） | x≈12（y の中央付近） | x≈16〜17（2 本のバー） | **約 4〜5px** |
| new3（FA7 + 今回の修正） | x≈13（y の中央付近） | x≈14 | **約 1px** |

**`new3`（今回の修正後）のほうが `old3`（利用者が正しいとする FA5 の
見た目）よりも、三角の右端と `＝` の右端の飛び出し量が小さい**
（4〜5px → 1px）。少なくとも「`＝` が三角の右へ大きくはみ出す」度合いは
FA5 版より今回の修正後のほうが小さく、視覚的にも重なり方は自然に見える
（下記スクリーンショット参照）。

三角の縦幅は old3 が 21 行（y2021〜2041）、new3 が 23 行（y2020〜2042）と
若干違うが、これは 1・2 回目の報告どおり FA5 と FA7 でグリフの実寸
（字面の高さ）自体が異なるため（`my-gage-r` の `font-size`/`fa-2x` の
計算元が FA5/FA7 で異なる)。`＝` が三角の上寄りに乗る、という配置の
関係そのものは old3・new3 とも同じ見え方だった。

### スクリーンショット

`~/tmp/playwright-mcp/` に `todo042c_` で始まる名前で保存（前のファイルは
上書きしていない。チャットにも添付済み）。

- `todo042c_old_fa5_412.png` / `todo042c_new_fa7fixed_412.png`
  （一覧全体、412 幅、今日＝針が基準線に重なった状態）
- `todo042c_old_fa5_gage_zoom.png` / `todo042c_new_fa7fixed_gage_zoom.png`
  （ゲージ付近を 8 倍に拡大して切り出したもの。x=0 を含む同じ範囲・同じ
  倍率で old3・new3 を並べて比較できる）

拡大画像を見比べると、**`＝`（grip-lines）が三角の上端に乗り、三角の
左上の角が `＝` の左端付近と揃う、という構図そのものは old3・new3 で
ほぼ同じ**に見える。利用者が示した「正しい」画像（`~/tmp/image.png`）の
構図（三角と `＝` が重なり、`＝` が三角よりわずかに右へ出る）と、今回の
`new3` の見た目は一致していると判断した。

### プロセスの後始末

自分で立てたプロセス（`ytsched webapp -p 18103/18104`、
`python3 -m http.server 18203/18204`、それぞれの子プロセス）を `ps aux`
で PID を確認してから `kill` し、全て終了を確認した。利用者のサーバ
（`-p 12345`、PID 134716）は触っていない。

### 見つかった不具合・気になった点

- 実装に問題は見つからなかった。今回の作業ツリーでの見た目（`new3`）は、
  縦位置は `dispGage(今日)` により基準線と完全一致し、横方向の
  「`＝` が三角の右へはみ出す量」も、利用者が正しいとする FA5 版
  （`old3`）より小さい（約 1px 対 約 4〜5px）。拡大画像で見比べても、
  構図（`＝` が三角の上に乗り、左端がおおむね揃う）は old3・new3 で
  近い
- 画素での右端測定は、三角と `＝` の色（三角は `opacity: 0.2` の淡い
  灰、`＝` は不透明な黒寄り）を輝度で振り分けて求めた簡易な方法。
  厳密な字面境界の分離ではないので、**数 px 単位の目安**として読んでほしい
  （どちらが「正しい重なり方」かの最終判断は、添付した拡大画像を見て
  行うのがよい）
