# TODO-038. HTML・CSS のリファクタリング

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer + wording |
| 実施 | Opus 5 / effort high | implementer × 3 + verifier + reviewer + wording |
| 消費 | output 86,322 / cache_creation 1,219,282（全体） | implementer 38% + main 31% + verifier 19% + reviewer 6% + wording 5% |

## きっかけ

TODO-037 で外部 CDN をやめたときに、`base.html` まわりを読んで気づいた
ものをまとめて挙げた。使っていない Bootstrap のクラスを削る話も
TODO-037 では見送っていて、その受け皿でもある。

挙げたのは 6 件。

- `sde.html` の `{% if sde.is_canceled() %}` が 7 か所で繰り返されている
- `style` 属性がテンプレート全体で 80 個ある
- 重複した id（`sde_id` / `menu-content` / `<title>`）
- 使われていない CSS と JS（`.my-osd` `.blinkborder` `.longtext:focus` /
  `editStr()` `clearBusyFlag()`）
- `edit.html` の `const detail_h` の再代入（**横向きで TypeError**）
- `main.html` の `doPost({{ url_prefix }}, …)` に引用符が無い

**見た目を 1 画素も変えないこと**を目標にした。

## 3 段に分けた

1 回でやると、見た目が変わったときに原因を切り分けられない。消す作業と
書き換える作業を混ぜると、差が出たときにどちらのせいか分からなくなる。
段ごとに画素単位の比較を挟めるようにした。

分担と、その理由は
[archives/agents/TODO-038/README.md](../agents/TODO-038/README.md)。

### 1 段目 ── 片付け

- 重複した id を 3 種類とも消した（`sde_id` の hidden input は `<form>` の
  外にあって誰も読んでいなかった。`menu-content` は `id` だけ消し、
  `<div>` と `class` は残した）
- `pagetop.css` と `my_cookie.js` を削除。`my.css` は 112 → 75 行、
  `my.js` は 477 → 424 行
- `const detail_h` → `let detail_h`。**修正前は横向きで
  `TypeError: Assignment to constant variable.` が出ていた**
  （`detail_h < 100` の再代入で落ちる）
- `doPost()` の第 1 引数に引用符を付けた（7 か所を洗った）

### 2 段目 ── `style` 属性を CSS へ

- `style="` が **80 → 1**。残したのは `<main id="main">` の 1 つだけで、
  `visibility` を JavaScript が書き換えるので、どのみち属性が要る
- 取り消し線を `.my-canceled` と `.my-canceled-items > *` の 2 つに分けた。
  1 つでは同じ見え方にならない。本文の欄（`col-11`）に直接引くと
  `<span>` どうしの間の空白にも線が入り、ToDo の日付・時刻の欄は
  `display: inline-flex` なので**親からの取り消し線が中へ伝わらない**
- `{% if sde.is_canceled() %}` を **7 か所 → 1 か所**。上の 2 つの
  クラス名を変数に入れ、各所ではその変数を書くだけにした
- 効かない宣言を 2 種類そのまま落とした。`style="vertical-align; middle;"`
  （`:` ではなく `;` で宣言として成立していない）と、`font-width: bold`
  （そんな CSS プロパティは無い）。**どちらも元から効いていない**ので、
  クラスに置き換えると逆に見た目が変わる
- `.my-bar-content` に `z-index: 100` を足した。インラインの `z-index` を
  外したら、閉じているはずのメニューがメニューバーの上に出た。Bootstrap の
  `.fixed-bottom`（`z-index: 1030`）をインラインの 100 が打ち消していた。
  **画素単位の比較で見つけた**

### 3 段目 ── クラス名の付け直し（当初の見込みには無かった）

2 段目で `.my-fs-xx-small` `.my-lh-12` のような**値をそのまま名前にした
クラス**が 61 か所入り、利用者から「定義する意味は？」と問われて足した段。

`style` を CSS へ寄せる利点は（1）インライン `style` を無くす、
（2）同じ役割の箇所を 1 か所で変えられるようにする —— の 2 つで、
**(2) は役割で名付けたときだけ効く**。`.my-fs-xx-small` は
`style="font-size: xx-small"` の別名でしかなく、`xx-small` をやめたく
なった時点で名前が嘘になる。

- Bootstrap 4.5 にあるものは自前で定義しない。`.my-va-middle` →
  `.align-middle`、`.my-fw-bold` → `.font-weight-bold`、`.my-va-bottom` →
  `.align-bottom`、`.my-hidden` → `.d-none`。定義ごと消した
- 役割で名付け直した（`.my-sde-time` `.my-sde-type` `.my-sde-title`
  `.my-sde-place` `.my-sde-detail` `.my-edit-row` など）
- **値のままの名前を残したのは `main.html` の 10 か所だけ。** メニューバー・
  検索欄まわりで、役割が 1 か所ずつ違ってまとめられないところ

最終的に `my.css` は 112 → 353 行。インラインから移した分だけ増えている。

## 決めたこと

- **取り消し済みの予定の「詳細」を開いたときだけ、上下の空行が 2 行ずつ
  減るのを受け入れた**（1 行の詳細で欄の高さが 122px → 62px。普通の予定と
  同じ見え方になる）。元は取り消し線の `<span>` が入れ子になっていたぶんだけ
  テキストの塊が増え、`white-space: pre-wrap` で余分な空行が出ていた。
  入れ子をやめるのがこの項目の眼目なので、ここだけは合わせられない
  （合わせるには `is_canceled()` で改行の数を変えることになり、消したはずの
  条件分岐が戻ってくる）。**意図した余白ではなく、テンプレートの書き方から
  出ていたもの**と判断した
- **`!important` は外さない。** 取り消し線に元から付いていた。外すと
  Bootstrap に負ける可能性があり、確かめるより残すほうが安全

## テスト

新しいテストは足していない。**既存のテストは本文の語と `id="date-…"` しか
見ておらず、崩れは捕まえない。** 確かめ方の中心はテストではなく画素単位の
比較にした（`chromium --headless --screenshot` ＋ `compare -metric AE`）。

verifier の結果（`archives/agents/TODO-038/verifier-report.md`）。比べた
相手は `cca8269`。

| 画面 | 幅 | 違う画素 |
|---|---|---|
| 編集（普通） | 412 / 740 | **0** |
| 編集（取り消し） | 412 / 740 | **0** |
| 編集（重要） | 412 / 740 | **0** |
| 一覧 | 412 / 740 | 137,773 / 277,075 |
| 検索 | 412 / 740 | 46,133 / 80,155 |

**一覧・検索の数字は、実装の差ではない。** 切り分けると 2 つに分かれた。

- 上に書いた「取り消し済みの詳細の空行」。テストデータに該当する予定が
  2 件あり、詳細を全部開いて撮っているので、そこから下の行がすべて
  ずれた位置と比較される
- **chromium 自身のレンダリングの揺らぎ。** 該当データを外して**同じ
  HTML を同じ chromium で 2 回**撮って比べると **AE=11,812**、旧×新は
  **11,813**。ほぼ同じ。`--fuzz 5%` を付けると 0 になるので、色の値が
  1〜数段階ずれる程度のもので、内容の違いではない

3 段目は implementer が検証に入る直前に落ちていて確認が取れておらず、
**特に怪しいとしていた 2 点**（`edit.html` の `<span class="my-fs-large">@</span>`
を `<span>` ごと外した件、`my-fs-large` が `col` から `row` へ移った件）は、
verifier が**どちらも画素単位で完全に一致**することを確かめた。

そのほか。

- `mise run lint` — ruff format / ruff check / basedpyright / mypy すべて通る
- `uv run pytest -q` — **412 passed**
- 起動確認（一時ディレクトリを `--datadir` に指定）— 一覧・編集・検索が
  200、サーバのログに `Traceback` 無し
- ブラウザの JavaScript の例外 — 一覧・編集 × 412 / 740 の 4 通りで
  `Uncaught` / `TypeError` / `ReferenceError` が 0 件

reviewer の結果（`archives/agents/TODO-038/reviewer-report.md`）は、
確信度の高い指摘は無し。消したものが本当に使われていないか、
`.my-canceled-items > *` が直接の子を取りこぼしていないかを別に洗い直して、
どちらも問題無しだった。

## 気になったが直さなかったもの

- `my.css` の `.my-gage` にある `/* background-color: #FFF; */` と、
  `edit.html` のコメントアウトされた `window.addEventListener('resize', …)`。
  どのやることにも挙げていなかったので触っていない
- `main.html` の `<script>` の中が、1 段目でインデントが 1 段ぶん浅くなっている。
  挙動には影響しないが、`git diff` が実際の変更より大きく見える一因
- `.longtext` `.longtext-sw` `.longtext-sw-label` `.blink` には `my-` を
  付けていない

## コミットの注意

**`pagetop.css` と `my_cookie.js` の削除だけは、この項目のコミットに
入っていない。** 1 段目の implementer が `git rm` したものがステージに
残ったまま、別件のコミット
`74a480a feat(agents): 実験的に、implementerとreviewerのモデルを
Opusから Sonnetに変更` に巻き込まれた。利用者の判断で、そのままにした。

この項目の変更を後から追うときは `cca8269..` の範囲で見ること。
