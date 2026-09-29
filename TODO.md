# TODO

**残っている項目: TODO-203。** これまでに 202 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-204` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-203. グローバル設定に合わせて担当の定義を 4 個にまとめる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high） |

- [ ] runner の手順（5 つのコマンド、落ちても止まらない、出力を原文で写す）を
      verifier の 1 節へ移し、`.claude/agents/runner.md` を消す。
      「原因を追う」のは main の仕事と書く
- [ ] writer の役割（文書を書く、書く前に実物を確かめる）を implementer へ移し、
      `.claude/agents/writer.md` を消す。日本語の規則は写さず
      `~/.claude/CLAUDE.md` を指す
- [ ] `CLAUDE.md` の「サブエージェントの分担」に、定型の実行は verifier を
      haiku に上書きして呼ぶ、と 1 行足す

`~/.claude/CLAUDE.md` に「確認・レビューの担当に原因の切り分けをさせない」が
入り、`runner.md` の「原因を追うのは `verifier` と main の仕事」と矛盾した。
`writer.md` は日本語の規則を書き写していて、2026-09-29 に足された mermaid の
規則が漏れている。`todo-workflow` skill は定義を 3〜4 個に絞るとしている。

これまでの利用は runner・writer とも 7 項目（最後は TODO-174・TODO-170）。
verifier も切り分けをしなくなったので、runner との違いは決まったコマンドと
モデルだけになる。残すのは implementer / verifier / reviewer / wording。

Codex 側（`.codex/agents/*.toml`、`.agents/`）は今回触らない（利用者が決めた）。
消した定義を指す参照がそちらに残る。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
