# TODO-039 implementer への依頼

スマホ用の設定を足す。**アイコン画像は main が作り終えているので、
画像には手を出さない**（`tools/make-icons.sh` と
`src/ytsched/webroot/static/icons/` は完成している）。

あなたがやるのは、**HTML・manifest・JavaScript・CSS・テスト・README**。

## 前提（main が既に済ませたこと）

```
tools/make-icons.sh                                （新規）
src/ytsched/webroot/static/favicon.ico             （本物の ICO に差し替え済み。16/32/48）
src/ytsched/webroot/static/icons/icon.svg          （新規。デザインの元）
src/ytsched/webroot/static/icons/icon-192.png      （新規）
src/ytsched/webroot/static/icons/icon-512.png      （新規）
src/ytsched/webroot/static/icons/icon-maskable-512.png （新規）
src/ytsched/webroot/static/icons/apple-touch-icon.png  （新規。180x180・透過なし）
```

**これらは触らない。** 作り直しも要らない。

## 1. `static/manifest.json` を新しく作る

置き場所は `src/ytsched/webroot/static/manifest.json`。

```json
{
  "name": "ytsched",
  "short_name": "ytsched",
  "lang": "ja",
  "start_url": "../",
  "scope": "../",
  "display": "standalone",
  "background_color": "#FFFFFF",
  "theme_color": "#4488CC",
  "icons": [
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "icons/icon-maskable-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

**`start_url` と `scope` を `../` にしているのは意図的。** manifest の中の
相対 URL は manifest 自身の URL から解決されるので、
`/ytsched/static/manifest.json` の `../` は `/ytsched/` になる。URL prefix は
`--urlprefix` で変えられる（`webapp.py` の `DEF_URL_PREFIX`）ので、
**絶対パスを書くと変えたときに合わなくなる。** ここを直すときは、その理由も
一緒に考えること。

## 2. `templates/base.html` の `<head>` を直す

いま入っているのは viewport・charset・title・`favicon.ico`・CSS だけ。
次のようにする（順番は好きにしてよい）。

- viewport を
  `width=device-width, initial-scale=1, interactive-widget=resizes-content`
  にする。**足すのは `interactive-widget=resizes-content` だけ**で、
  既にある 2 つは変えない
- `<meta name="theme-color" content="#4488CC">`
- `<meta name="mobile-web-app-capable" content="yes">` と、
  `<meta name="apple-mobile-web-app-capable" content="yes">` の両方。
  後者は古い名前だが、iOS がまだこちらしか見ない
- `<meta name="apple-mobile-web-app-status-bar-style" content="default">`
- `<meta name="apple-mobile-web-app-title" content="{{ title }}">`
- アイコンと manifest のリンク（`static_url()` を通すこと。今の
  `favicon.ico` の行と同じ書き方）

```html
<link rel="icon" href="{{ static_url('favicon.ico') }}" sizes="32x32">
<link rel="icon" type="image/svg+xml"
      href="{{ static_url('icons/icon.svg') }}">
<link rel="apple-touch-icon"
      href="{{ static_url('icons/apple-touch-icon.png') }}">
<link rel="manifest" href="{{ static_url('manifest.json') }}">
```

`static_url()` は末尾に `?v=…` を付けるが、`../` の解決には効かない
（クエリはパスの一部ではない）ので、manifest でも問題ない。

## 3. ソフトキーボードで下部ボタンが隠れるのを直す

**編集画面（`edit.html`）で textarea に入力すると、`fixed-bottom` の
ボタンがキーボードの下に隠れて押せない。** これを、キーボードの上に
出るようにする。

方針は 2 段構え。

- **Android Chrome**: viewport の `interactive-widget=resizes-content`
  （上で足したもの）で、キーボードが出ると本文の領域そのものが縮む。
  `fixed-bottom` は自然にキーボードの上に来る
- **iOS Safari**: `interactive-widget` を見ないので、上だけでは直らない。
  `window.visualViewport` を見て、バーを自分でずらす

### `static/js/my.js` に足すもの

```javascript
/**
 * 画面下に固定したバーを、ソフトキーボードの上に出す (TODO-039)
 *
 * `.my-follow-keyboard` が付いた要素を、キーボードの高さだけ持ち上げる。
 *
 * Android Chrome は viewport の `interactive-widget=resizes-content` で
 * 本文が縮むので、ここで計算するずれは 0 になる。iOS Safari は縮まない
 * ので、この関数が効く。
 *
 * ピンチで拡大している間 (`scale > 1`) は何もしない。拡大中も
 * `visualViewport` は小さくなるが、それはキーボードのせいではないため。
 */
const followKeyboard = () => {
    const vv = window.visualViewport;
    if ( ! vv ) {
        return;
    }
    let offset = 0;
    if ( vv.scale <= 1.01 ) {
        const gap = window.innerHeight - vv.height - vv.offsetTop;
        offset = Math.max(0, Math.round(gap));
    }
    const els = document.getElementsByClassName("my-follow-keyboard");
    for ( const el of els ) {
        el.style.transform = `translateY(${-offset}px)`;
    }
};

if ( window.visualViewport ) {
    window.visualViewport.addEventListener("resize", followKeyboard);
    window.visualViewport.addEventListener("scroll", followKeyboard);
    window.addEventListener("load", followKeyboard);
}
```

**このコードはそのまま使ってよいが、内容は自分で確かめること。**
`my.js` は今のところ関数の定義と変数の宣言だけで、末尾で
`addEventListener` を呼ぶのは初めてになる。読み込みは `base.html` の
`<head>` で、`defer` は付いていない。それでも `load` は間に合う。

### クラスを付ける先

- `edit.html` の `<div id="menu" name="menu" class="… fixed-bottom my-bar">`
- `main.html` の `<div id="menu_bar" class="… fixed-bottom my-bar my-menu-bar">`

**`main.html` の `.my-bar-content`（引き出しメニュー）には付けない。**
閉じているときは `bottom: -60px` で画面の外にあるので、持ち上げると
出てきてしまう。

### `static/css/my.css` に足すもの

`.my-follow-keyboard` は JavaScript から探すための目印で、見た目は
変えない。**それが分かるコメントを付けて置く**こと（空のルールでよい。
`will-change: transform;` は付けても付けなくてもよいが、付けるなら
理由をコメントに書く）。

## 4. テストを足す

`tests/test_webapp.py` に、同梱されていることの確認を足す
（`test_webroot_is_bundled` と同じ並び）。

- `manifest.json` と、アイコン 5 つ（`favicon.ico`・`icon.svg`・
  `icon-192.png`・`icon-512.png`・`icon-maskable-512.png`・
  `apple-touch-icon.png`）がファイルとしてあること
- `manifest.json` が JSON として読めること
- `start_url` と `scope` が `../` であること
  （**URL prefix を変えても付いてくる、という意図をテストで押さえる**）
- `icons` の `src` が、実際にあるファイルを指していること
  （`static_path` からの相対で開けること）

`tests/test_web.py` には、HTTP で引けることの確認を足す
（`tornado.testing` のクラスがもうある。既存のクラスの書き方に揃える）。

- `/ytsched/static/manifest.json` が 200 で、`Content-Type` が JSON
- `/ytsched/static/icons/apple-touch-icon.png` が 200
- `/ytsched/static/favicon.ico` が 200
- 一覧の HTML に `rel="manifest"` と `rel="apple-touch-icon"` の
  `<link>` が出ていること

**テストは既存のものを壊さないこと。** `mise run test` は今 412 件通る。

## 5. `README.md`

「同梱しているライブラリ」の近くに、アイコンと manifest のことを書く。

- アイコンは独自のデザインで、元は `static/icons/icon.svg` 1 つ。
  `tools/make-icons.sh` で PNG と ICO を作り直せる（ImageMagick が要る）
- `manifest.json` を置いてあるので、スマホのホーム画面に追加すると
  単体のアプリのように開く
- `start_url` が相対なので、`--urlprefix` を変えても付いてくる

**長くしない。** 既存の書き方と分量に揃えること。

## 決まりごと

- **`TODO.md` と `archives/todo/` は触らない**（main が書く）
- **アイコン画像と `tools/make-icons.sh` は触らない**
- `mise run upgradeproject` は走らせない。
  `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい
- アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する
- 報告は `archives/agents/TODO-039/implementer-report.md`
