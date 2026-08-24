# TODO-041. 追加読み込みのたびに自動スクロールが起きるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + wording |
| 実施 | Opus 5 / effort high | verifier + wording |
| 消費 | output 38,501 / cache_creation 150,666（全体） | main 69% + wording 17% + verifier 14% |

**消費は `--since '2026-08-24 11:37:40'` で測った。** 規約どおりに
`docs(todo):` のコミット（12:23:59）を始点にすると、**症状の再現と原因の
切り分けが数に入らない**。この項目では、それが main の仕事のほとんど
だった。指定した時刻は、直前のコミット（`21a11af`、11:37:38）の直後。

## きっかけ

利用者から「スクロールしていて追加読み込みが発生すると、必ず下から上に
自動的にスクロールが発生する。今、実機で確認できないので確かめてほしい」。

TODO-040（Bootstrap 4.5.0 → 5.3.8）の直後で、それまでは起きていなかった。

## 原因

追加読み込みは、**POST でページごと読み直してから位置を合わせ直す**作り。

```
下端に着く → scrollHdr() が doPost() → サーバが次の範囲を返す
→ 新しいページの onloadHdr() が scrollToDate(..., "auto") で位置を合わせる
```

この最後の位置合わせがアニメーションになっていた。`scrollTo()` の
`"auto"` は「即座に」ではなく「**CSS の `scroll-behavior` に従う**」という
意味で、Bootstrap 5.3.8 の reboot が次の 1 行を持っている。

```css
@media (prefers-reduced-motion:no-preference){:root{scroll-behavior:smooth}}
```

4.5.0 にはこの指定が無く、`"auto"` は瞬時だった。`my.js` を書いた 2021 年
当時はそれで正しく、Bootstrap を上げたことで意味が変わった。

新しいページは先頭（`scrollY = 0`）から始まるので、そこから狙いの位置まで
下へアニメーションする。**画面のコンテンツは下から上へ流れる**。
`scrollToId()` は動かす前に `elMain.style.visibility = "visible"` にするので、
その途中経過が全部見える。

### 切り分けに使った性質

**headless の Chromium は smooth スクロールを実行しない。** そのため
「smooth 扱いになっているかどうか」が、スクロールが起きるか起きないかで
そのまま分かる。

```
CSS が smooth のまま scrollTo({top:2500, behavior:'auto'}) → 1000 のまま動かない
scroll-behavior を auto に戻して同じ呼び出し               → 2500 へ即座に移動
```

なお、headless では `scroll` イベントから `scrollHdr()` が発火しなかった
ので、下端へ `instant` で移してから `scrollHdr()` を直接呼んだ。
`doPost()` から先は同じ経路を通る。

## やったこと

分担と、その理由は
[archives/agents/TODO-041/README.md](../agents/TODO-041/README.md)。

`src/ytsched/webroot/templates/main.html` の 1 か所だけ。

```
     scrollToDate(location.pathname,
                  el_date.value, el_sde_align.value,
-                  "auto");
+                  "instant");
```

`"instant"` は CSS に関係なく常に瞬時。**ボタン操作で使っている
`"smooth"` は残した**（`scrollToDate` / `moveToMonday` の既定）。
これは意図したアニメーションで、追加読み込みのときの位置合わせとは別。

なぜ `"auto"` ではいけないのかがコードから読めないので、呼び出しの直前に
3 行のコメントを置いた。

**Bootstrap の指定そのものを `my.css` で打ち消す案は採らなかった。**
`:root { scroll-behavior: auto; }` を書けばアンカーリンクなど他の暗黙の
スクロールにも効くが、今回直したいのは「即座に移したい 1 か所」なので、
そこだけを明示するほうが意図が読める。同じ症状が他で出たら、そのときに
考え直す。

## テスト

**テストは足していない。** 直したのはテンプレートに書いた JavaScript の
引数 1 つで、Python 側のテストからは触れない。

verifier の結果（[verifier-report.md](../agents/TODO-041/verifier-report.md)）。

- `mise run lint` / `mise run test` — **418 件 pass**。`ruff format` /
  `ruff check` / `basedpyright` / `mypy` も通る
- **追加読み込みの直後の `scrollY` が `2611`** で、`scrollToId` が狙った
  位置と一致した（修正前は `0` のまま動かなかった）。`sde_align` は
  `bottom`、コンソールのログも `scrollToDate` → `scrollToId` の流れどおり
- `<` / `>` / ホームボタンを押しても JavaScript のエラーはゼロで、
  遷移するはずのところで遷移する

**実機では確かめていない。** headless では smooth のアニメーションが
そもそも走らないので、「アニメーションが消えたか」を目で見る確認は
できない。ここで確かめたのは「位置合わせが一度で狙った場所に移る」まで。

## 次に同じことをするときの申し送り

- **`scrollTo()` の `"auto"` は「即座に」ではない。** 即座に移したい
  ところでは `"instant"` と書く。`"auto"` は CSS 側の設定に左右されるので、
  ライブラリを上げたときに黙って意味が変わる
- **headless の Chromium が smooth を実行しないことは、確認の道具になる。**
  「smooth になっているか」を目で見なくても、スクロールが起きるかどうかで
  判定できる。逆に、smooth の見え方そのものは headless では確かめられない
- **Playwright は `uv run --no-project --with playwright` で一時的に使える。**
  プロジェクトの依存は増えない。ブラウザは既に
  `~/.cache/ms-playwright/chromium-1200/chrome-linux/chrome` にあるので、
  `executable_path` で指定する

## 文書の語（wording の指摘と、どう決めたか）

`wording` が前例の無い語を 3 つ挙げた
（[wording-report.md](../agents/TODO-041/wording-report.md)）。
**3 つとも、そのままにした。**

- **「判定基準」（前例なし）。** 「判定」（115 件）も「基準」も前例が多く、
  つなげた形が初出というだけ。出てくるのは verifier の報告ファイルで、
  **報告ファイルは直さない**（そのとき何を書いたかの記録）
- **「アンカーリンク」（前例なし）。** `<a href="#id">` によるページ内リンク
  を指す普通の技術用語
- **「reboot」（前例なし）。** Bootstrap が自身の CSS リセット部分に付けて
  いる固有名詞（`_reboot.scss` 由来）。訳さずそのまま使う
