# TODO

**残っている項目: TODO-212。** これまでに 211 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-213` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-212. 過去のレビュー・提案の文書に残る autoescape の誤りを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5.5 / effort medium | main のみ（文書だけを変え、確かめる中身は書いた内容と実測の一致だけ。`{% autoescape None %}` は `base.html` にしか効かず、子テンプレートは以前からエスケープされていた。TODO-209・TODO-211 で実測済み） |

- [ ] `docs/obsidian-format-review.md:213` の「`base.html` は `autoescape None`
      のまま」を実際の挙動に合わせる
- [ ] `docs/image-attach-proposal.md:254` の「`{% autoescape None %}` なので
      `<img>` を手で書けば表示される」を直す（実際はエスケープされて
      表示されない。提案の前提に関わるので、前後の文脈も読む）
- [ ] `docs/code-review.md:252` の「`{% autoescape None %}` が設定されており、…
      設計方針」を直す（すでに消してある）
- [ ] `rg -n "autoescape" --glob '!archives' docs` で、ほかに残りが無いか確かめる

TODO-211 の reviewer が見つけた。TODO-211 では、過去の文書だからと直さずに
決着させたが、利用者から「誤りが残っているのに完了させたのか」と指摘され、
項目として立てた。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
