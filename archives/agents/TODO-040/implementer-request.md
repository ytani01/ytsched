# TODO-040 implementer への依頼

Bootstrap を 4.5.0 → **5.3.8**、Font Awesome Free を 5.6.1 → **7.3.1** に
上げる。**`TODO.md` の TODO-040 を先に読むこと。**

やることと、そう決めた理由は `TODO.md` に全部書いてある。**判断は済んで
いる。** この依頼書のとおりに手を動かしてほしい。範囲を広げないこと。

## 触るファイル

| ファイル | すること |
|---|---|
| `src/ytsched/webroot/static/vendor/bootstrap/bootstrap.min.css` | 5.3.8 に差し替え |
| `src/ytsched/webroot/static/vendor/bootstrap/LICENSE` | 5.3.8 のものに差し替え |
| `src/ytsched/webroot/static/vendor/fontawesome/css/all.css` | 7.3.1 に差し替え |
| `src/ytsched/webroot/static/vendor/fontawesome/webfonts/` | `.woff2` 2 つに（`.woff` 2 つは `git rm`） |
| `src/ytsched/webroot/static/vendor/fontawesome/LICENSE.txt` | 7.3.1 のものに差し替え |
| `src/ytsched/webroot/templates/*.html` | クラス名 3 種を置換（下記） |
| `src/ytsched/webroot/static/css/my.css` | `--bs-body-font-family` の固定を足す |
| `README.md` | 「同梱しているライブラリ」の節（204〜216 行あたり）を書き直す |

**`src/` の Python と `static/js/my.js` は触らない。** `base.html` も
触らない（`<link>` のパスは変わらないため）。

## 1. Bootstrap 5.3.8

取得元と、**取得したものが途中で変わっていないことの照合**。

```
https://github.com/twbs/bootstrap/releases/download/v5.3.8/bootstrap-5.3.8-dist.zip
  → dist/css/bootstrap.min.css
  sha384 = sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB
  sha256 = d85327d99c7a3ee1f9b5d0500d1370acea3ad2db39c163c2f51f232baedbdede
```

照合のしかたは TODO-037 と同じ。

```bash
openssl dgst -sha384 -binary bootstrap.min.css | openssl base64 -A
```

**この sha384 は、jsDelivr の npm 公開版
（`https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css`）
と 1 バイトも違わないことを main が確かめた値。** 一致しなければ手を止めて
報告すること。

**`bootstrap.min.css` だけを置く。** `bootstrap.min.css.map` も
`bootstrap.bundle.min.js` も入れない（TODO-037 で JS は外してある）。

LICENSE は dist の zip に入っていないので、別に取る。

```
https://raw.githubusercontent.com/twbs/bootstrap/v5.3.8/LICENSE
```

## 2. Font Awesome Free 7.3.1

```
https://github.com/FortAwesome/Font-Awesome/releases/download/7.3.1/fontawesome-free-7.3.1-web.zip
```

入れるのは 4 つだけ。**どれも main が jsDelivr の
`@fortawesome/fontawesome-free@7.3.1` と突き合わせて同一を確かめてある。**

| zip の中のパス | 置き場所 | sha384 |
|---|---|---|
| `css/all.css` | `vendor/fontawesome/css/all.css` | `7WvIYI4vLdL28Kb0e0uLmaY+AFg62zUFE8P4OgFsKy0m93wWgDxFmdtVTkKNTJi8` |
| `webfonts/fa-solid-900.woff2` | `vendor/fontawesome/webfonts/` | `TeBDWCQ2a4tojAZRcJzXsEgFI2EzW27W0GYt9HIpqXdUiPIauuYxz9RpAgJM1x9+` |
| `webfonts/fa-regular-400.woff2` | `vendor/fontawesome/webfonts/` | `78Wu/Ea/cmf/TbrN4bDVNmemhBWOSesv4mzA40dUVsj9Hb5E2CTaukY/7qGGVmBg` |
| `LICENSE.txt` | `vendor/fontawesome/LICENSE.txt` | （照合不要） |

- **`fa-brands-400.woff2` と `fa-v4compatibility.woff2` は入れない。**
  TODO-037 と同じ理由で、`fab` を使っている箇所が無い
- **いま置いてある `.woff` 2 つ（`fa-solid-900.woff` /
  `fa-regular-400.woff`）は `git rm` で消す。** Font Awesome 7 は
  `.woff` を配らなくなり、`all.css` の `@font-face` も `.woff2` しか
  参照していない
- **アイコン名の書き換えは要らない。** 使っている 25 個の名前
  （`fa-home` `fa-search` `fa-trash-alt` `fa-arrow-alt-circle-up`
  `fa-list-alt` など）も `fas` / `far` も、7.3.1 の `all.css` に旧名の
  まま残っていることを main が確かめた。テンプレートの `fa-` は
  1 つも触らないこと

## 3. Bootstrap 5 で消えたクラスの置換

`src/ytsched/webroot/templates/` の 4 ファイルが対象。**10 か所。**

| 現状 | 5.3.8 | 箇所 |
|---|---|---|
| `text-left` | `text-start` | `sde.html` 1・`edit.html` 1・`main.html` 2 |
| `text-right` | `text-end` | `edit.html` 1・`main.html` 3 |
| `font-weight-bold` | `fw-bold` | `sde.html` 1・`main.html` 1（どちらも `{% set %}` の中） |

置換したあと、**`grep -rn 'text-left\|text-right\|font-weight-bold'
src/ytsched/` が 0 件になることを確かめる**こと。`src/` 全体を見ること
（Python 側にクラス名が書かれていないことの確認も兼ねる）。

## 4. `my.css` に font-family の固定を足す

**これが表示を保つための要。** Bootstrap 5 の既定は `system-ui, …` で、
4.5 の `-apple-system, …` と、実際に使われるフォントが違って行の高さが
変わる。

`my.css` の**先頭**に、次をそのまま置く（main が実測で効き目を確かめた
もの。値は 4.5 の `bootstrap.min.css` の `body{font-family: …}` と同一）。

```css
/*
 * Bootstrap 5 の既定のフォント (system-ui, ...) は 4.5 のもの
 * (-apple-system, ...) と、実際に使われるフォントが違って行の高さが
 * 変わる。固定しないと日付ブロックが 1 個あたり 2px 高くなり、一覧が
 * 176px 伸びる (TODO-040)。値は 4.5 の bootstrap.min.css と同じ。
 */
:root {
    --bs-body-font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Helvetica Neue", Arial, "Noto Sans", sans-serif,
        "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol",
        "Noto Color Emoji";
}
```

`my.css` の他の行は 1 つも変えないこと。

## 5. `README.md`

「同梱しているライブラリ」の節にある版数を書き直す。Font Awesome 7 は
`.woff` を配らないので、**「`woff2` と `woff` のみ」という説明も
実態に合わせる**こと（いま同梱するのは `woff2` だけになる）。

## 自分でも確かめること

`verifier` が別に確かめるが、任せきりにしないこと。

- `mise run test` が通る（前回は 412 件）
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、一覧・編集が
  200 で返る。**`~/ytsched/data` は絶対に触らない**
- 同梱した 5 ファイルが 200 で配信され、`.woff2` の先頭 4 バイトが
  `wOF2` になっている
- `grep -rn 'text-left\|text-right\|font-weight-bold' src/` が 0 件

**画素単位の比較は `verifier` がやるので、あなたはやらなくてよい。**

## 報告

`archives/agents/TODO-040/implementer-report.md` に書く。返事は 5 行以内。

- 置いたファイルと、照合した sha384 が一致したか（**実際に出た値を報告に
  書くこと**）
- 置換した箇所の数と、grep が 0 件になったか
- 自分で確かめたことの結果
- 単独で決めた判断と、その理由
- 気づいたが直さずに残したもの
