# TODO-037 implementer への依頼

`TODO.md` の TODO-037 を読んでから始めること。範囲はそこに書いてある
チェックリストのとおり。

## 背景

`base.html` が Bootstrap・Font Awesome・jQuery・popper を外部 CDN から
読んでいる。CDN が届かないとレイアウトが崩れ、アイコンが消えてボタンが
押せなくなる（実測で確認済み）。これを同梱して、外部への通信を無くす。

**見た目は変えない。** 使っていない CSS クラスを削るのは TODO-038 の
仕事で、この項目ではやらない。

## やること

### 1. 使っていない 3 つを消す

`base.html` の jQuery（`code.jquery.com`）・popper（`cdn.jsdelivr.net`）・
`bootstrap.bundle.min.js`（読み込んでいれば）の `<script>` を消す。

`webroot` 全体を grep したが、`$(` も `data-toggle` も `modal` も
`dropdown` も 1 件も無い。メニューの開閉は `#menu-sw:checked ~ ...`
（`my.css`）で、CSS だけで動いている。**消す前に自分でも確かめること。**

### 2. 同梱する

置き場所はこの形にする。Font Awesome の `all.css` は
`../webfonts/...` を参照するので、`css/` と `webfonts/` を並べること。

```
src/ytsched/webroot/static/vendor/
  bootstrap/
    bootstrap.min.css
    LICENSE
  fontawesome/
    css/all.css
    webfonts/fa-solid-900.woff2
    webfonts/fa-solid-900.woff
    webfonts/fa-regular-400.woff2
    webfonts/fa-regular-400.woff
    LICENSE.txt
```

取得元（到達を確認済み）:

- `https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css`
- `https://use.fontawesome.com/releases/v5.6.1/css/all.css`
- `https://use.fontawesome.com/releases/v5.6.1/webfonts/fa-solid-900.woff2`
  （`.woff` と `fa-regular-400` の 2 形式も同じ場所）

**Bootstrap は改竄されていないことを確かめること。** `base.html` に
`integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk"`
が書いてある。取得したファイルから同じ値が出るかを見る。

```sh
openssl dgst -sha384 -binary bootstrap.min.css | openssl base64 -A
```

**`brands` は入れない。** `fab` を使っている箇所は 1 つも無い。
`all.css` の中に `@font-face` の定義は残るが、`fab` を使わない限り
ブラウザは取りに行かないので 404 にはならない。

**フォントの形式は `woff2` と `woff` だけにする。** README のとおり
クライアントは Chrome 前提で、`eot` / `ttf` / `svg` は使われない
（`svg` は 1 ファイルで 700KB 近くある）。この判断は報告に書くこと。

### 3. `base.html` を差し替える

`<link>` の `href` を `static_url()` に変える。`integrity` と
`crossorigin` は、同一オリジンになるので消す。

### 4. ライセンス表記

- Bootstrap 4.5.0 — MIT
- Font Awesome Free 5.6.1 — アイコンが CC BY 4.0、フォントが SIL OFL 1.1、
  コードが MIT

それぞれの配布物に入っている `LICENSE` をそのまま置くこと。加えて
`README.md` に、同梱していることと出典を 1 節書く（既存の見出しの並びに
合わせる。どこに置くかは自分で決めてよい）。

## 確かめること（自分の範囲で）

- `mise run test` が通る
- `mise run lint` が通る
- `--datadir` に**一時ディレクトリ**を指定してアプリを起動し、画面が
  出ること（`~/ytsched/data` は絶対に使わない）

崩れていないかの確認と `uv tool install` 後の配信確認は verifier がやる
ので、ここでは要らない。

## 決まりごと

- **`TODO.md` は編集しない。** main が行う
- **git commit はしない。** main が行う
- 詳しい報告は `archives/agents/TODO-037/implementer-report.md` に書く。
  返事は 5 行以内で、(1) 終わったか (2) 報告ファイルのパス
  (3) main の判断が要る点、だけ
- 依頼書に無いことを自分の判断で足したら、**足したと分かるように報告に
  書く**（不要なら main が消せるように）
