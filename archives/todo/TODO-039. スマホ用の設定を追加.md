# TODO-039. スマホ用の設定を追加

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer + wording |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + wording |
| 消費 | output 59,645 / cache_creation 368,433（全体） | main 50% + verifier 15% + implementer 13% + reviewer 11% + wording 10% |

**消費は `--since '2026-08-24 10:56:10'` で測った。** この項目は
TODO-037・038 と一緒に立てられた（`f22bafd`）ので、規約どおりに
`docs(todo):` のコミットを始点にすると、TODO-037・038・040 の作業まで
数に入る。指定した時刻は、直前のコミット（`e146a11`、10:56:02）の直後。
コミットの直前に測ったので、この記録を書く分は入っていない。

## きっかけ

利用者が立てた項目（TODO-037・038 と同時に立てた）。やることは 4 つ
書いてあった。

- `manifest.json`、`apple-touch-icon` など
- `favicon.ico` も追加
- アイコン画像は、シンプルなものを、独自にデザイン
- スマホでスケジュール編集時、ソフトキーボードで textarea の下の
  ボタンが隠れてしまう

## 着手前に決めたこと

**アイコンは、候補を 3 つ描いて利用者に見せてから選んだ。**
言葉で「カレンダー風」と説明しても決めようがないので、main が実際に
描き、512px と 32px の両方を並べて見せた。

| 案 | 中身 | 選ばれたか |
|---|---|---|
| A | 青の角丸に、白いカレンダー（留め具・予定を表す帯） | **これに決めた** |
| B | 赤い見出しのカレンダーに、大きなチェック | |
| C | 白地に青枠、中に点を並べた月表示風 | |

C は 32px にすると線が細くて詰まって見えた。青は既存のメニューバーと
同じ `#48C`（`my.css` の `.my-bar`）を使った。

**ソフトキーボードの件は「キーボードの上にボタンを追従させる」に
決めた。** 「入力中はバーを隠す」「固定をやめる」も選択肢として示したが、
どちらも押せない時間ができる。ボタンの位置は今までどおり画面の下。

## やったこと

分担と、その理由は
[archives/agents/TODO-039/README.md](../agents/TODO-039/README.md)。

### アイコン（main）

元は **SVG 1 つだけ**。角丸を落とした版と、中身を 85% に縮めた版は、
`tools/make-icons.sh` の中で `sed` を当てて作る。デザインを直すときに
1 か所だけ直せばよいようにした。

```
src/ytsched/webroot/static/icons/icon.svg          デザインの元
src/ytsched/webroot/static/favicon.ico             16 / 32 / 48 の 3 枚入り
src/ytsched/webroot/static/icons/icon-192.png      manifest 用
src/ytsched/webroot/static/icons/icon-512.png      manifest 用
src/ytsched/webroot/static/icons/icon-maskable-512.png  Android の切り抜き用
src/ytsched/webroot/static/icons/apple-touch-icon.png   180x180・透過なし
tools/make-icons.sh                                作り直す手順
```

決めたことがいくつかある。

- **`favicon.ico` は本物の ICO にした。** 差し替える前のファイルは、
  名前が `.ico` なのに**中身は 540x540 の PNG** だった（TODO-002 で
  移したときから）。今回のものは先頭 4 バイトが `00 00 01 00` で、
  48 / 32 / 16 の 3 枚が入っている
- **maskable 版は中身を 85% に縮めた。** Android はアイコンを機種ごとの
  形（円・角丸・雫）に切り抜くので、外側が削られる。安全なのは中央の
  直径 80% の円の内側。縮めた絵をその円と重ねて、はみ出していないことを
  main が目で見て確かめた
- **apple-touch-icon は角を丸めず、透過も落とした。** iOS が自前で角を
  丸めるので、丸めておくと二重になる。透過はそのまま黒く出る
- **ImageMagick の内蔵 SVG レンダラ（MSVG）は、塗りつぶした図形に
  黒い輪郭を付ける。** `<svg>` に `stroke="none"` を書いて止めた。
  この理由は `icon.svg` のコメントにも残してある

### `manifest.json`（implementer）

`src/ytsched/webroot/static/manifest.json` に置いた。

**`start_url` と `scope` を `../` にしたのが要点。** manifest の中の
相対 URL は manifest 自身の URL から解決されるので、
`/ytsched/static/manifest.json` の `../` は `/ytsched/` になる。
URL prefix は `--urlprefix` で変えられるため、絶対パスを書くと変えた
ときに合わなくなる。`tests/test_webapp.py` の `test_manifest_content`
で、この 2 つが `../` であることを押さえてある。

`static_url()` が付ける `?v=…` は、パスの一部ではないので `../` の
解決には効かない。

### `base.html`（implementer）

`<head>` に足したもの。

```
viewport に interactive-widget=resizes-content
theme-color                          #4488CC
mobile-web-app-capable               yes
apple-mobile-web-app-capable         yes（古い名前。iOS はこちらを見る）
apple-mobile-web-app-status-bar-style default
apple-mobile-web-app-title           {{ title }}
link rel=icon        favicon.ico（sizes="32x32"）と icon.svg
link rel=apple-touch-icon
link rel=manifest
```

**viewport の `content` の値は、1 行に収めた。** implementer は他の
属性と同じように折り返していたが、属性と属性の間で折るのと、値の中で
折るのとは別の話になる。改行を読めないブラウザに当たると、
`width=device-width` ごと効かなくなって影響が大きい。テンプレートの
他の行より長くなるが、そちらを取った。理由はテンプレートにも
コメントで残してある。

### ソフトキーボードの追従（implementer）

2 段構えにした。

- **Android Chrome** — viewport の `interactive-widget=resizes-content`
  で、キーボードが出ると本文の領域そのものが縮む。`fixed-bottom` は
  自然にキーボードの上に来る
- **iOS Safari** — `interactive-widget` を見ないので、これだけでは
  直らない。`window.visualViewport` を見て、`my.js` の
  `followKeyboard()` がバーを持ち上げる

持ち上げる先は `.my-follow-keyboard` が付いた要素で、`main.html` の
`#menu_bar` と `edit.html` の `#menu` に付けた。**`.my-bar-content`
（引き出しメニュー）には付けていない。** 閉じているときは
`bottom: -60px` で画面の外にあるので、持ち上げると出てきてしまう。

## テスト

新しく 6 件足して、**418 件**（直前は 412 件）。

- `tests/test_webapp.py` — `manifest.json` とアイコン 6 つが同梱されて
  いること、manifest が JSON として読めること、`start_url` / `scope`
  が `../` であること、`icons` の `src` が実在するファイルを指すこと
- `tests/test_web.py` — `manifest.json`・`apple-touch-icon.png`・
  `favicon.ico` が HTTP で 200 で返ること、一覧の HTML に
  `rel="manifest"` と `rel="apple-touch-icon"` が出ていること

verifier の結果（[verifier-report.md](../agents/TODO-039/verifier-report.md)）。

- `mise run test` — **418 件 pass**。`ruff format` / `ruff check` /
  `basedpyright` / `mypy` も通る
- `uv build` した wheel に、`manifest.json` とアイコン 6 つが入っている
- 起動して curl — 上の 7 ファイルが全部 200。**`favicon.ico` の先頭
  4 バイトは `00 00 01 00`** で、`file` は
  `MS Windows icon resource - 3 icons` と答えた。PNG 4 つの先頭は
  `89 50 4e 47`
- `--urlprefix /sched` で起動し直すと、`<link rel="manifest">` の
  href が `/sched/static/manifest.json?v=…` になり、`/ytsched/…` は
  残らない
- chromium で、一覧・編集 × 幅 412 / 740 に
  **`visualViewport` を `undefined` にした 2 通り**を加えた 6 通りで、
  JavaScript の例外と `console.error` が 0 件
- `HEAD`（`e146a11`）と画素単位で比べて、**下部バーの位置と見た目に
  変化なし**。残った差はテストデータ（日付と UUID）の違いだけだった

**実機のスマホでは確かめていない。** ソフトキーボードが実際に出る環境が
無いので、キーボードの上にボタンが出るかどうかは利用者が確かめる。
ここで確かめたのは「キーボードが無い状態で今までどおりか」と
「例外が出ないか」まで。

## レビューで出たこと

reviewer の報告（[reviewer-report.md](../agents/TODO-039/reviewer-report.md)）。
**確信度の高い指摘は無し。** 依頼で挙げた懸念（`gap` の計算、
`transform` の競合、`scale` の閾値、登録のしかた、`scope`）は、
いずれも問題無しと判断された。

確信度が低いものとして 1 件挙がり、**それは直した**。

- **`followKeyboard()` のコメントと実装が食い違っていた。**
  「ピンチで拡大している間は何もしない」と書いてあるのに、実際は
  `offset = 0` を書き込んで元の位置へ戻す。キーボードが出ている状態で
  拡大すると、バーがキーボードの後ろへ戻る。**実装のほうが妥当**
  （拡大中の `visualViewport` の縮みはキーボードのせいではないので、
  その分を持ち上げると位置が狂う）なので、コメントを実装に合わせた

## 次に同じことをするときの申し送り

- **JavaScript の例外を見るのに、verifier は CDP
  （Chrome DevTools Protocol）を使った。** `chromium
  --remote-debugging-port=…` に繋いで `Runtime.exceptionThrown` と
  `Log.entryAdded` を拾う。そのために `websocket-client` を
  `pip install --user` で入れている（プロジェクトの `.venv` ではなく、
  利用者のユーザ環境に入った）。TODO-040 のスクリーンショット比較より
  一歩進んだ確かめ方で、`--screenshot` では拾えない例外を見られる
- **`Page.addScriptToEvaluateOnNewDocument` で
  `window.visualViewport` を `undefined` にすると、古いブラウザの
  ふりをさせられる。** 今回はこれで「`visualViewport` が無い環境でも
  例外にならない」ことを確かめた
- **chromium の `--user-data-dir` を毎回変えること**は TODO-040 の
  申し送りどおり。今回もそれで問題は起きなかった

## 文書の語（wording の指摘と、どう決めたか）

`wording` が前例の無い語を 4 つ挙げた
（[wording-report.md](../agents/TODO-039/wording-report.md)）。
**4 つとも、そのままにした。**

- **「追従」（前例なし）。** `wording` は、既にある「追随」
  （TODO-033「URL_PREFIX の改名に追随できていない箇所を直す」、前例
  30 件）と字面が近いので、使い分けているのか判断できないと書いた。
  **使い分けている。**「追随」は、コードが変更に付いていくこと。
  「追従」は、バーがキーボードの動きに合わせて位置を変えること。
  クラス名 `my-follow-keyboard` と関数 `followKeyboard()` にも
  対応している。なお `--urlprefix` の話では「追随」ではなく
  「付いてくる」と平たく書いてあり、2 つの語がぶつかる箇所は無い
- **「引き出しメニュー」（前例なし）。** `.my-bar-content` が何なのかを
  implementer に伝えるための説明で、drawer menu の訳語として普通に
  使われている
- **「クランプ」「同期読み込み」（前例なし）。** どちらも `reviewer` の
  報告にあった語で、一般に通用する専門用語。**報告ファイルは直さない**
  （そのとき何を書いたかの記録なので、TODO-040 と同じ扱い）

## 気になったが直さなかったもの

- **`changeDetailHeight()`（編集画面の textarea の高さ）は、読み込み時に
  1 回しか計算しない。** Android では `resizes-content` で本文の領域が
  縮むが、textarea の高さは変わらないままなので、キーボードが出ると
  ページがスクロールする。`resize` を見て測り直す行は `edit.html` に
  あるが、**もともとコメントアウトされている**（いつからかは追って
  いない）。外すと別の副作用が出る可能性があり、今回の範囲を超える
- **`.my-follow-keyboard` は中身の空の CSS ルール。** JavaScript から
  探すための目印で、見た目は変えない。reviewer も問題無しと判断した
- **`base.html` の `<meta charset>` が `<head>` の先頭ではない。**
  viewport の次に置かれている（今回より前からそう）。1024 バイトの
  内側には収まっているので実害は無い
