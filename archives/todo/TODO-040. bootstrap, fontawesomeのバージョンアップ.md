# TODO-040. bootstrap, fontawesomeのバージョンアップ

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + wording |
| 実施 | Opus 5 / effort high | implementer + verifier + wording |
| 消費 | output 82,415 / cache_creation 568,029（全体） | main 71% + verifier 12% + wording 10% + implementer 7% |

**消費は `--since '2026-08-24 06:10:00'` で測った。** いつもと逆の理由で
`--since` が要った。この項目は**立てるより先に調査した**（上げると表示が
どう変わるかを測らないと、利用者に相談する形にできなかった）ので、始点を
`docs(todo):` のコミットに取ると、その調査分が丸ごと落ちる。実際、
規約どおりに測ると output 32,738 / cache_creation 259,607 で、
**半分以下**になった。指定した時刻は 1 つ前のコミット（`1a6a4fd`、
06:13:36）の少し前。

main が 71% を占めるのは、そのためでもある。担当に渡す前の調査
（版の比較、画素単位の測定、フォント固定の効き目の確認）が全部 main 側に
乗っている。

## きっかけ

利用者が立てた項目。**Bootstrap 4.5.0 と Font Awesome Free 5.6.1 が
古い。** TODO-037 で外部 CDN をやめて同梱したときの版をそのまま置いた
もので、Bootstrap 4 系はサポートが終わっており、Font Awesome 5 系も
2022 年で更新が止まっている。

条件は「基本的に挙動や表示を変えない。どうしても変化する場合は相談して
決める」。

## 上げる前に測った

**上げると表示が変わるのかどうかが分からないと、相談の形にできない。**
そこで main が、一時ディレクトリに現状と新版の `webroot` を並べて
立ち上げ、画素単位で比べた。412 幅・一覧（全 1,648,000 px）。

| 上げるもの | 違う画素 |
|---|---|
| Font Awesome だけ 6.7.2 | 111,842（6.8%） |
| Font Awesome だけ 7.3.1 | 110,296（6.7%） |
| **Bootstrap だけ 5.3.8** | **432,275（26%）** |
| 両方 | 428,859（26%） |

分かったのは 2 つ。

### Bootstrap の 26% は崩れではなくズレで、原因は 1 つだけだった

`body` の `font-family` が **`-apple-system, …` から `system-ui, …` へ
変わった**こと。それだけ。日付ブロック 1 個の高さが **75px → 77px** に
なり、90 日分積み上がってページ全体が 6,943px → 7,119px に伸びる。
以降の行が全部ずれるので、画素の差が大きく出ていた。

グリッドの gutter や `col` の padding は変わっていない（テンプレートが
`p-0` を多用していて、Bootstrap 側の値に依存していないため）。

`my.css` で `--bs-body-font-family` を 4.5 と同じ値に固定したら、
**ページ全体の高さと日付ブロックの高さが完全に一致し**、画素の差は
**432,275 → 17,033（1.0%）** に落ちた。残った差の最大の塊（6,762px）は
**読み込み中のしるし（`fa-spin`）の回転位置**で、実装の差ではない。

### Font Awesome の差は絵柄そのもので、固定では消せない

5 → 6 でアイコンが描き直されている。いちばん目立つのは家（`fa-home`）で、
**輪郭線＋ドアの絵から塗りつぶしの絵**に変わる。リスト（`fa-list-alt`）・
虫眼鏡（`fa-search`）・`fa-backspace` の × も違う。**6 と 7 の差は小さく、
5 → 6 の差のほうが大きい。**

## 決めたこと

利用者に画面を見せて相談し、次のとおり決まった。

- **Bootstrap は 5.3.8 まで上げ、フォントは 4.5 と同じ値に固定する。**
  4.6.2（4 系の最新）に留める案もあったが、4 系はサポートが終わっている
- **Font Awesome は 7.3.1 まで上げ、絵柄が変わるのは受け入れる**
- **アイコン名の書き換えは要らない。** 使っている 25 個の名前
  （`fa-home` `fa-search` `fa-trash-alt` `fa-arrow-alt-circle-up`
  `fa-list-alt` など）も `fas` / `far` も、7.3.1 の `all.css` に旧名の
  まま残っている。FA 6・7 が v5 の名前をエイリアスとして持ち続けている
- **`.woff` は同梱しない。** Font Awesome 7 は `.woff` を配らなくなり、
  `all.css` の `@font-face` も `.woff2` しか参照しない。同梱するフォントは
  4 つ → 2 つになった
- **JavaScript と Python は触らない。** Bootstrap の JS は TODO-037 で
  外してあり、`my.js` は `classList` を一度も使っていない。上げても
  影響が及ばない

## やったこと

分担と、その理由は
[archives/agents/TODO-040/README.md](../agents/TODO-040/README.md)。

### 差し替えたもの

```
bootstrap/bootstrap.min.css      4.5.0 → 5.3.8
bootstrap/LICENSE                MIT (2011-2020 → 2011-2025)
fontawesome/css/all.css          5.6.1 → 7.3.1
fontawesome/webfonts/fa-solid-900.woff2    7.3.1
fontawesome/webfonts/fa-regular-400.woff2  7.3.1
fontawesome/webfonts/fa-solid-900.woff     削除
fontawesome/webfonts/fa-regular-400.woff   削除
fontawesome/LICENSE.txt          7.3.1 のもの
```

**取得したものが途中で変わっていないことは、sha384 で照合した。**
TODO-037 では `base.html` に書いてあった `integrity` の値と突き合わせた
が、今回は同梱済みで `integrity` が無い。代わりに **GitHub のリリースの
zip と、jsDelivr の npm 公開版が 1 バイトも違わないこと**を main が
確かめ、その値を依頼書に書いて implementer に照合させた。CDN から消えた
あとに同じものを入れ直せるよう、ここにも書き残しておく。

```
bootstrap.min.css        sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB
fontawesome/all.css      7WvIYI4vLdL28Kb0e0uLmaY+AFg62zUFE8P4OgFsKy0m93wWgDxFmdtVTkKNTJi8
fa-solid-900.woff2       TeBDWCQ2a4tojAZRcJzXsEgFI2EzW27W0GYt9HIpqXdUiPIauuYxz9RpAgJM1x9+
fa-regular-400.woff2     78Wu/Ea/cmf/TbrN4bDVNmemhBWOSesv4mzA40dUVsj9Hb5E2CTaukY/7qGGVmBg
```

### 書き換えたクラス名（10 か所）

Bootstrap 5 で消えたもの。

| 4.5.0 | 5.3.8 | 箇所 |
|---|---|---|
| `text-left` | `text-start` | `main.html` 2・`edit.html` 1・`sde.html` 1 |
| `text-right` | `text-end` | `main.html` 3・`edit.html` 1 |
| `font-weight-bold` | `fw-bold` | `main.html` 1・`sde.html` 1（`{% set %}` の中） |

そのほか使っているクラス（`container-fluid` / `row` / `col-*` / `p-*` /
`m-*` / `text-center` / `align-middle` / `align-bottom` / `fixed-bottom` /
`d-none` / `border` / `alert`）は 5.3.8 にもそのままある。

### `my.css` の先頭に足したもの

```css
:root {
    --bs-body-font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Helvetica Neue", Arial, "Noto Sans", sans-serif,
        "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol",
        "Noto Color Emoji";
}
```

値は 4.5.0 の `bootstrap.min.css` にあった `body{font-family: …}` と同じ。

### `README.md`

「同梱しているライブラリ」の節の版数を直し、`woff` を配らなくなった
ことを書いた。

## テスト

新しいテストは足していない。**既存のテストは本文の語と `id="date-…"` しか
見ておらず、崩れは捕まえない**（TODO-037・038 と同じ事情）。確かめ方の
中心はテストではなく画素単位の比較にした。

verifier の結果（`archives/agents/TODO-040/verifier-report.md`）。比べた
相手は `1a6a4fd`。

| 画面 | 幅 | 違う画素 |
|---|---|---|
| 一覧 | 412 / 740 | 22,534 / 22,656 |
| 編集 | 412 / 740 | 17,291 / 22,474 |
| 検索 | 412 / 740 | 22,530 / 18,406 |

総画素数は 412 幅で 1,648,000、740 幅で 2,960,000。**差は 1.0〜1.4%** で、
内訳は 2 つだけだった。

- **Font Awesome の絵柄。** 一覧では日付ブロックごとの「＋」
  （`fa-plus-square`）が、旧は太い＋、新は細く小さい＋になる。編集画面の
  複製・削除ボタンとメニューバーのアイコン群も同様。**位置と大きさの
  ずれは無い**
- **読み込み中のしるしの回転位置。** `fa-spin` のアニメーションなので、
  撮るたびに角度が違う

**この 2 つで説明の付かない差は見つからなかった。** chromium 自身の
揺らぎは、同じ版で 2 回撮って **4,590（0.28%）**。上の数字はその数倍
あるので、絵柄の差が確かに乗っている。

**ページ全体の高さと日付ブロックの高さは、旧新で完全に一致した**
（`document.body.scrollHeight` が 6,980px、`.my-date-block` が 75px）。
`--bs-body-font-family` の固定が効いている。

そのほか。

- `mise run test` — **412 件 pass**。`ruff format` / `ruff check` /
  `basedpyright` / `mypy` も通る
- 起動確認（一時ディレクトリを `--datadir` に指定）— 一覧・編集・検索が
  200、サーバのログに `Traceback` 無し
- 同梱した 6 ファイルが 200 で配信され、`.woff2` の先頭が `wOF2`
- **消した `.woff` 2 つは 404。** `all.css` にも `.woff2` 以外への
  `url(…)` は無い
- `uv build` した wheel に `.woff2` 2 つが入り、`.woff` は入っていない
- ブラウザの JavaScript の例外 — 一覧・編集 × 412 / 740 の 4 通りで
  `Uncaught` / `TypeError` / `ReferenceError` が 0 件
- `git diff 1a6a4fd -- src/ytsched/*.py src/ytsched/webroot/static/js/`
  が **0 行**（Python と `my.js` は 1 行も変わっていない）

## 次に同じことをするときの申し送り

verifier が手順でつまずいた点。**依頼書
（`archives/agents/TODO-040/verifier-request.md`）には書いていなかった**
ので、ここに残す。

- **chromium を続けて起動するときは、呼び出しごとに
  `--user-data-dir` に別のディレクトリを渡す。** 指定しないと既定の
  プロファイルのロック待ちで**無期限に止まる**（`timeout` を超えても
  終わらない）。TODO-037・038 では表に出ていなかった
- 詳細を開いた状態を作る置換は、**`class="longtext-sw d-none"`** に
  当てる。依頼書には `class="longtext-sw"` と書いたが、実際の HTML は
  `d-none` が付いていて一致しない

## 文書の語（wording の指摘と、どう決めたか）

`wording` が前例の無い語を 8 つ挙げた
（`archives/agents/TODO-040/wording-report.md`）。main の判断は次のとおり。

**直したのは 2 つ。**

- **「解決先」→「実際に使われるフォントが違って」。** `font-family` の
  フォールバックがどのフォントに当たるか、という意味で使っていた。名前解決の
  比喩としては通じるが、この場面では平たく書けば済む。`my.css` の
  コメントと implementer への依頼書を直した
- **「ハマった点」→「つまずいた点」。** `verifier` の報告にあった。
  「つまずいた」は `archives/agents/TODO-026/verifier-report.md` に前例が
  ある

**「読み込み中のしるし」は残した。** `wording` は「スピナー」のほうが
普通ではないかと見立てたが、**`my.css:124` に
`/* 読み込み中のしるし (display は JavaScript が書き換える) */` が既に
あった**（TODO-038 で付けたコメント）。`.md` に前例が無かっただけで、
リポジトリの中では定着している呼び名なので、そちらに揃えた。

残りの 5 つ（「差分画像」「絵柄」「回転位置」「読み込み中」「伸びる」）は
そのまま。どれも普通の日本語か、一般に通用する複合語と判断した。

**`wording` の報告は直していない。** 引用が直したあとの文と食い違うが、
「そのとき何を指摘したか」の記録なので、そのまま残す。

## 気になったが直さなかったもの

- **`README.md` の Font Awesome の説明から「クライアントを Google
  Chrome 前提としているため」が落ちた。** 5.6.1 のときは `eot` / `ttf` /
  `svg` を入れない理由だったが、7 は `woff2` しか配らないので理由その
  ものが要らなくなった。`solid` と `regular` だけを入れる理由
  （`fab` を使っていない）は残してある
