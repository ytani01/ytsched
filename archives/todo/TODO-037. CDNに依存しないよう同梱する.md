# TODO-037. CDNに依存しないよう同梱する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + wording |
| 実施 | Opus 5 / effort high | implementer + verifier + wording |
| 消費 | output 35,992 / cache_creation 173,326（全体） | main 50% + implementer 21% + verifier 17% + wording 12% |

## きっかけ

利用者から「ユーザー目線で改良すべき点はないか」と言われて画面を見た
ときに見つけた。`base.html` が Bootstrap 4.5.0・Font Awesome 5.6.1・
jQuery 3.5.1・popper.js 1.16.0 を外部 CDN から読んでいた。

chromium で CDN への通信を止めて開くと、**レイアウトが崩れてアイコンが
すべて消え、ボタンがどこにあるか分からなくなる**。スマホで持ち歩く
前提のソフトなので、回線が細いときや外に出られない環境で効く。

## 決めたこと

- **丸ごと同梱する。** 実際に使っている Bootstrap のクラスは
  グリッド・余白・文字寄せ・`fixed-bottom`・`border`・`alert` だけで、
  使うクラスだけ書き直すこともできた。そうしなかったのは、**見た目を
  変えずに依存だけ外す**ためで、使っていないクラスを削るのは TODO-038 の
  側でやる。同じコミットに混ぜると、崩れたときにどちらのせいか分からない
- **jQuery・popper・`bootstrap.js` は同梱せず消す。** `webroot` 全体を
  探して、`$(` も `data-toggle` も `modal` も `dropdown` も 1 件も無かった。
  メニューの開閉は `#menu-sw:checked ~ .my-bar-content`（`my.css`）で、
  CSS だけで動いている
- **`brands` のフォントは入れない。** `fab` を使っている箇所が無い。
  `all.css` に `@font-face` の定義は残るが、`fab` を使わない限り
  ブラウザは取りに行かないので 404 にはならない
- **フォントの形式は `woff2` と `woff` だけ。** README のとおり
  クライアントは Chrome 前提で、`eot` / `ttf` / `svg` は使われない
  （`fa-solid-900.svg` は 1 つで 700KB 近くある）

## やったこと

- `base.html` の `<link>` 2 本を `static_url()` に差し替え、
  `integrity` / `crossorigin` を消した（同一オリジンになるため）
- `</body>` 直前の `<script>` 3 本（jQuery・popper・`bootstrap.min.js`）を
  消した
- `src/ytsched/webroot/static/vendor/` に置いた

  ```
  bootstrap/bootstrap.min.css            160,403 bytes
  bootstrap/LICENSE                      MIT
  fontawesome/css/all.css                 53,741 bytes
  fontawesome/webfonts/fa-solid-900.woff2 79,072
  fontawesome/webfonts/fa-solid-900.woff 102,120
  fontawesome/webfonts/fa-regular-400.woff2 14,868
  fontawesome/webfonts/fa-regular-400.woff  18,164
  fontawesome/LICENSE.txt                 アイコン CC BY 4.0 /
                                          フォント SIL OFL 1.1 / コード MIT
  ```

- `README.md` に「同梱しているライブラリ」の節を足した

**Bootstrap が取得の途中で変わっていないことは、`base.html` に書いて
あった `integrity` の値で照合した。** `openssl dgst -sha384 -binary` の
出力が `9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk`
と一致した。CDN から消えたあとに同じものを入れ直せるよう、ここにも
書き残しておく。

## テスト

`mise run test` は 412 件が通り、lint・型チェックも通った。
新しいテストは足していない（テンプレートの `<link>` の中身は、既存の
テストが見ている範囲の外にある）。

**確かめ方の中心は、テストではなく画面の比較にした。** chromium を
CDP で動かし、同梱の前後で同じ画面を撮って画素単位で比べた。

| 比べたもの | 違う画素 |
|---|---|
| 編集画面（前 / 後） | 0 |
| メニューを開いた画面（前 / 後） | 0 |
| 一覧（前 / 後） | 7,331 / 1,507,920（0.486%）。最大の差は 21/255 で、文字の縁のなめらかさだけ。目では区別できない |
| 一覧（後、CDN 遮断あり / なし） | **0** |

同じ版で 2 回撮ると 0 画素だったので、一覧の差はブレではない。ただし
すべて文字の縁にあり、切り出して並べても見分けが付かなかった。

verifier が別に確かめたこと（`archives/agents/TODO-037/verifier-report.md`）:

- 出力 HTML とソース全体に `stackpath.bootstrapcdn.com` /
  `use.fontawesome.com` / `code.jquery.com` / `cdn.jsdelivr.net` が
  1 件も残っていない
- 同梱した 4 つが 200 で配信され、`.woff2` の先頭が `wOF2` になっている
  （フォント本体が届いている）
- `uv build` した wheel に vendor の 8 ファイルが入る
- サーバのログに例外も 404 も出ない

## やらなかったこと

- **`uv tool install --reinstall .` での確認。** 立てたときのチェック
  リストには入れていたが、このマシンに `ytsched` はツールとして入って
  いなかった（`uv tool list` に無い）。確認のために利用者の環境へ新しく
  入れることになるので、`uv build` した wheel の中身を見る形に変えた
- **`static/css/pagetop.css` の扱い。** どこからも読み込まれておらず、
  冒頭のコメントに jQuery の `<script>` 例が残っている。implementer が
  気づいたが、TODO-038 の範囲として手を付けていない
