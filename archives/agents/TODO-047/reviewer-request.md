# TODO-047 reviewer への依頼

TODO-047「Bootstrap をやめて、素の CSS にする」の実装を見てほしい。
**CSS が中心**で、Python はほとんど関係ない。

先に読むもの:

- `~/work/ytsched/TODO.md` の TODO-047 の節
- `archives/agents/TODO-047/implementer-request.md`（依頼書）
- `archives/agents/TODO-047/implementer-report.md`（実装者の報告）

変わったのは `my.css`（398 → 679 行）・`base.html`・`README.md` と、
`static/vendor/bootstrap/` の削除。`git diff` で見られる。

## 見てほしいところ

1. **写し漏れが無いか。** テンプレート 4 つ
   （`base.html` `main.html` `edit.html` `sde.html`）で使っている
   クラスが、全部 `my.css` に定義されているか。
   **`class="..."` を grep するだけでは足りない。**
   テンプレート変数から入るもの（`main.html` の `class_today`、
   `sde.html` の `class_important` → どちらも `fw-bold`）がある
2. **reboot（土台）の写し漏れ。** Bootstrap が無くなって効かなくなる
   指定のうち、テンプレートに出てくる要素にかかるものが落ちていないか。
   実装者は「`<button>` `<a>` `<table>` `<hr>` `<ul>` `<p>` `<h1>`〜
   `<h6>` は使っていないので写していない」と書いている。**それが本当に
   テンプレートに無いかを自分で確かめること。**
   消えた `bootstrap.min.css` は
   `git show HEAD:src/ytsched/webroot/static/vendor/bootstrap/bootstrap.min.css`
   で読める
3. **`row` / `col-N` を CSS Grid に置き換えた判断。** 折り返しが
   起きないという前提が本当に成り立っているか（どの `row` も子の合計が
   12 列か）。ガター（`--my-gutter-x`）の再現が Bootstrap と合っているか
4. **`!important` を 4 か所外した判断。** 並び順（ユーティリティを
   `my-*` より前に置く）で本当に解けているか。**`my.css` の中で、
   ユーティリティより後ろに来る `my-*` が、意図せずユーティリティを
   打ち消していないか**も見てほしい
5. **黙って壊れる書き方が無いか。** CSS は落ちても例外が出ないので、
   「効いていないのに気づけない」書き方があれば挙げる
6. `README.md` の追記が実態と合っているか。ライセンスの告知
   （Bootstrap は MIT）が、`vendor/bootstrap/LICENSE` を消したあとも
   足りているか

## 見なくてよいもの

- 動くかどうか（`verifier` が別に確かめている）
- 見た目が変わっていないか（実装者が DOM の計算値で突き合わせ、
  `verifier` も独立に確かめる）
- 好みの問題（クラスの並べ方の趣味、コメントの多寡）
- 次は今回の範囲外。指摘しなくてよい
  - Font Awesome がまだ入っていること（TODO-048）
  - `my.js` の `"instant"`（TODO-041 の回避）が残っていること。
    **利用者が「今回は触らない」と決めた**
  - `tools/screenshot.py` の問題（TODO-051）
  - テンプレートの構造そのもの（TODO-049・TODO-050）

## 報告

`archives/agents/TODO-047/reviewer-report.md` に書く。返事は 5 行以内。
コードは直さないこと。確信度の高い指摘に絞り、確信度が低いものは
節を分けて明記する。
