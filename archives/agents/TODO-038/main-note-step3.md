# TODO-038 3 段目についての覚書（main）

**3 段目の implementer は、実装を終えたあと、検証に入る直前に API エラーで
落ちた。** そのため `implementer-report-3.md` は無い。ここに、main が
代わりに確かめたことを書く。

依頼書は [implementer-request-3.md](implementer-request-3.md)。

## 実装は依頼どおり全部入っている

作業ツリーと、3 段目を始める前の退避
（`/home/ytani/.claude/jobs/795ce790/tmp/webroot-before-step3/`）を
`diff -u` で比べて、1 か所ずつ照らし合わせた。依頼書の 3 つのやること
（Bootstrap への置き換え・役割で名付け直し・使われなくなった定義の削除）は
すべて実施されている。

implementer が依頼書から外れた判断をしたところは無い。依頼書が
「外せるはず。外して画素が変わるなら残して報告」と書いた
`edit.html` の `<span class="my-fs-large">@</span>` は、`<span>` ごと
外して `@` だけになっている。**画素が変わらないことの確認は取れていない**
（落ちたため）。verifier に見てもらう。

## main が確かめたこと

grep だけ。**動かしていないし、画面も見ていない。**

- 消したはずの `.my-lh-*` `.my-fw-bold` `.my-va-middle` `.my-va-bottom`
  `.my-hidden` `.my-fs-x-large` は、テンプレートにも `my.css` にも残って
  いない
- `sde.html` と `edit.html` から `my-fs-*` が全部消えている
- `main.html` に残る `my-fs-*` は 10 か所（`large` 1 / `medium` 1 /
  `small` 6 / `x-small` 1 / `xx-small` 1）。依頼書のとおり
- `style="` は `main.html` の 1 つだけ（`#main`。JavaScript が
  `visibility` を書き換えるので残す）
- `my.css` の `.my-*` とテンプレートの `my-*` が一致している。
  食い違うのは `.my-wday-0`〜`6` だけで、これは
  `my-wday-{{ weekday }}` で組み立てているため（2 段目の報告と同じ）

## 残っていること

**画素単位の比較・lint・テスト・起動確認は、どれもやっていない。**
verifier に依頼する。
