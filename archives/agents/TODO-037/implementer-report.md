# TODO-037 implementer 報告

CDN への依存を無くし、Bootstrap と Font Awesome を同梱した。

## 変更・作成したファイル

### 変更

- `src/ytsched/webroot/templates/base.html`
  - Bootstrap CSS と Font Awesome の `<link>` を `static_url()` に差し替え、
    `integrity` / `crossorigin` を削除
  - `</body>` 直前の `<script>` 3 本（jQuery 3.5.1 / popper.js 1.16.0 /
    bootstrap.min.js 4.5.0）を削除
- `README.md`
  - 「## 同梱しているライブラリ」の節を追加（`## 開発者向け` の直前）

### 新規（同梱物）

```
src/ytsched/webroot/static/vendor/
  bootstrap/
    bootstrap.min.css        160,403 bytes
    LICENSE                  (MIT / twbs v4.5.0 タグ)
  fontawesome/
    css/all.css               53,741 bytes
    webfonts/fa-solid-900.woff2    79,072
    webfonts/fa-solid-900.woff    102,120
    webfonts/fa-regular-400.woff2  14,868
    webfonts/fa-regular-400.woff   18,164
    LICENSE.txt              (FortAwesome 5.6.1 タグ)
```

取得元は依頼書のとおり。LICENSE は配布物の GitHub タグから取得した
（`raw.githubusercontent.com/twbs/bootstrap/v4.5.0/LICENSE`、
`raw.githubusercontent.com/FortAwesome/Font-Awesome/5.6.1/LICENSE.txt`）。

## 削除前に確かめたこと（jQuery / popper / bootstrap.js）

`src/ytsched/webroot` 全体を grep した結果:

- `$(` … 0 件
- `jquery` … `base.html` の当該行と、`pagetop.css` のコメント（後述）のみ
- `data-toggle` / `data-target` / `data-bs-` / `modal` / `dropdown` /
  `collapse` / `tooltip` / `popover` / `carousel` … 0 件
- メニュー開閉は `main.html` の `<input id="menu-sw" type="checkbox">` と
  `my.css` の `#menu-sw:checked ~ .my-bar-content` で、CSS だけで動く

JS を必要とする Bootstrap コンポーネントは使っていないと判断した。

## Bootstrap の照合

```
$ openssl dgst -sha384 -binary bootstrap.min.css | openssl base64 -A
9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk
```

`base.html` に書かれていた `integrity` の値と一致した。

## Font Awesome のアイコン種別

テンプレートで使っているクラスは `fas`（solid）と `far`（regular）だけで、
`fab`（brands）は 0 件だった。よって brands のフォントは入れていない。

`all.css` の `@font-face` は 3 つとも、2 つめの `src:` が
`eot?#iefix` → `woff2` → `woff` → `ttf` → `svg` の順になっている。
Chrome は `embedded-opentype` を飛ばして `woff2` を採る（対応する最初の
形式だけを取りに行く）ので、`eot` / `ttf` / `svg` を置かなくても 404 には
ならない。`brands` の `@font-face` も、`fab` を使う要素が無い以上
ブラウザはフォントを読み込まない。

## 単独で決めたこと

- **フォントは `woff2` と `woff` の 2 形式だけにした。** 依頼書の指示どおり。
  README にもクライアントは Google Chrome 前提と書いてあり、`eot` / `ttf` /
  `svg` は使われない（`fa-solid-900.svg` だけで 700KB 近い）。
- **LICENSE の取得元。** CDN からは LICENSE が取れないので、それぞれの
  GitHub リポジトリの該当タグ（`v4.5.0` / `5.6.1`）から取った。
- **README の節の置き場所。** `## 開発者向け` の直前に独立した `##` の節を
  作った。`## 使用環境` の下に置くことも考えたが、あちらは使用環境の話で
  内容が違うため分けた。
- **`<link>` の書き方。** 元の Font Awesome の行は `href` が先、
  Bootstrap の行は `rel` が先だったが、2 行とも `rel="stylesheet"` を先に
  して揃えた（同ファイル内の `my.css` の行と同じ順）。

## 依頼書に無くて足したもの

- **`mise run build` でパッケージに入ることを確認した**（下記）。
  ファイルは変えていないので、消す対象は無い。

## 自分で確かめたこと

| 内容 | 結果 |
|------|------|
| `mise run test` | 412 passed |
| `mise run lint` | ruff format / ruff check / basedpyright / mypy すべて通過 |
| `openssl dgst -sha384` で Bootstrap を照合 | `integrity` と一致 |
| 一時 datadir・ポート 10098 で `uv run ytsched webapp` を起動 | 起動する |
| トップページ `/` と `/ytsched/` | いずれも 200 |
| `/ytsched/edit?date=2026-08-23` | 200 |
| 出力 HTML に `http://` / `https://` が残っていないか | 0 件 |
| vendor 配下 6 ファイルの配信 | すべて 200。`.woff2` は `font/woff2`、`.woff` は `font/woff` で返る |
| 起動ログの error / warning / 404 | 0 件 |
| `mise run build` の wheel / sdist に vendor が入るか | 8 ファイルとも入る |
| `git check-ignore` で除外されないか | 除外されない |

`static_url()` が付ける `?v=…` は URL のパスを変えないので、`all.css` の
中の `../webfonts/…` は
`/ytsched/static/vendor/fontawesome/webfonts/…` に解決される。実際に
その URL で 200 が返ることを確認した。

起動確認に使ったデータディレクトリは scratchpad 配下の一時ディレクトリで、
`~/ytsched/data` には一切触っていない。

## 気づいたが直さずに残したもの

いずれも TODO-038（HTML・CSS のリファクタリング）の範囲。

- `static/css/pagetop.css` は、`base.html` からも `my.css` からも
  読み込まれていない（`.pagetop` を使う要素も無い）。冒頭のコメントに
  jQuery や `bootstrap.bundle.js` の `<script>` 例が残っているが、
  コメントなので動作には影響しない
- `base.html` に `<title>` が 2 つある（7 行目と 27 行目）。
  TODO-038 のチェックリストに挙がっている
- Bootstrap CSS 全体（160KB）を同梱している。使っていないクラスを削るのは
  TODO-038 の範囲なので、丸ごと置いた

## うまくいかなかったところ

無し。
