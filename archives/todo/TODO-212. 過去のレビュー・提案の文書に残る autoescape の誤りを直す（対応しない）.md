# TODO-212. 過去のレビュー・提案の文書に残る autoescape の誤りを直す（対応しない）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5.5 / effort medium | main のみ（文書だけを変え、確かめる中身は書いた内容と実測の一致だけ。`{% autoescape None %}` は `base.html` にしか効かず、子テンプレートは以前からエスケープされていた。TODO-209・TODO-211 で実測済み） |
| 実施 | Sonnet 5.5 / effort xhigh | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | xhigh | 10 | 2,120 | 4,376 | 716,258 | 100% |
| 合計 |  |  | 10 | 2,120 | 4,376 | 716,258 | 計 722,764 |

- effort は TODO-211 の途中で利用者が `/effort xhigh` にしたもの

## きっかけ

TODO-211 の reviewer が、過去のレビュー・提案の文書 3 つに autoescape の誤りが
残っていることを見つけた。

- `docs/obsidian-format-review.md:213`: 「`base.html` は `autoescape None` のまま」
- `docs/image-attach-proposal.md:254`: 「`{% autoescape None %}` なので `<img>` を
  手で書けば表示される」（実際はエスケープされて表示されない）
- `docs/code-review.md:252`: 「`{% autoescape None %}` が設定されており、…
  設計方針」

## やらないと決めた理由

**直さずに、3 つとも削除した**（利用者の指示: 「今となっては、全く役に立たない」）。

- `docs/obsidian-format-review.md`、`docs/image-attach-proposal.md`、
  `docs/code-review.md`
- `docs/obsidian-format-review-comments.md` も、削除した
  `obsidian-format-review.md` へのコメントで、冒頭のリンクが切れるため、
  利用者に確かめて一緒に削除した
- ほかの現行文書から、これらへのリンクは無い
  （`rg -n "obsidian-format-review|image-attach-proposal|code-review\.md"
  --glob '!archives' --glob '!TODO.md' .` が 0 件）
- 中身が要るときは、git の履歴から読める

## 確かめたこと

- 削除したあとに、上の `rg` が 0 件（リンク切れが無い）
- `rg -n autoescape --glob '!archives' docs` の残りは、
  `docs/data-format.md`（TODO-211 で書き直した正しい説明）と
  `docs/web-framework-review.md:96`（別のフレームワークへ変換する検討の中の
  記述で、誤りの主張ではない）だけ

## 残ること

- `docs/web-framework-review.md` などの、ほかの過去のレビュー・検討の文書
  （`docs/token-usage-analysis.md` を含む）も同じく役に立たないなら、
  削除してよい。今回は指示された 3 つ（と、そのコメント文書）だけにした
