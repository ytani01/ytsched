# TODO-203. グローバル設定に合わせて担当の定義を 4 個にまとめる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high） |
| 実施 | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high、2 回） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | high | 42 | 10,303 | 25,593 | 2,249,360 | 82% |
| reviewer | Opus 5.5 | high | 28 | 3,202 | 47,732 | 462,248 | 18% |
| 合計 |  |  | 70 | 13,505 | 73,325 | 2,711,608 | 計 2,798,508 |

- 集計は項目を立てたコミットから。立てる前の突き合わせ（`~/.claude` との差分の洗い出し）は入っていない
- 途中で利用者から ccspk の読みについて 2 回質問があり、その分も main に入っている

## きっかけ

最新の `~/.claude/CLAUDE.md` と `todo-workflow` skill をローカルの設定と突き合わせたところ、
次の食い違いがあった（TODO-202 で反映した 4 点は合っていた）。

- `~/.claude/CLAUDE.md` に「確認・レビューの担当に原因の切り分けをさせない」が入り、
  `runner.md` の「原因を追うのは `verifier` と main の仕事」と矛盾した
- `writer.md` は日本語の規則を書き写していて、2026-09-29 に足された mermaid の規則が
  漏れていた（`todo-workflow` の「規約を定義に書き写さない」にも反する）
- `todo-workflow` は定義を 3〜4 個に絞るとしているのに、6 個あった

これまでの利用は runner・writer とも 7 項目（最後は TODO-174・TODO-170）。verifier も
切り分けをしなくなったので、runner との違いは決まったコマンドとモデルだけになる。
利用者と相談し、implementer / verifier / reviewer / wording の 4 個にまとめると決めた。
Codex 側（`.codex/agents/*.toml`、`.agents/`）は今回触らないことも利用者が決めた。

## やったこと

- `.claude/agents/verifier.md`: 「原因の切り分けをしない」を足し、runner の手順を
  「定型の実行」の節として移した。`ruff` は `format --check` と `--fix` 無しの `check` にして、
  ファイルを書き換えないようにした（reviewer の指摘 A。書き換えると「コードを直さない」に
  反し、reviewer が見ていない変更が後から入る）。落ちたコマンドの出力は
  「エラーの出た部分だけ」にした（指摘 B。報告の節の「その部分だけ貼る」と揃える）
- `.claude/agents/implementer.md`: 役割を「コードと文書を書く」にし、「文書を書くとき」の節を
  足した。日本語の書き方は `~/.claude/CLAUDE.md` を指すだけにした
- `.claude/agents/runner.md`・`writer.md` を消した
- `CLAUDE.md` の「サブエージェントの分担」に、定義が 4 つであることと、定型の実行は
  verifier を haiku に上書きして頼むことを足した

## 確かめたこと

- reviewer に、統合で落ちた内容、移した先での矛盾、`~/.claude/CLAUDE.md` との食い違いを
  見させた（`archives/agents/TODO-203/reviewer-report.md`）。A・B を直したあと、同じ
  reviewer に再レビューさせ、解消を確かめた
- 定型の実行の `ruff` の 2 つを手元で走らせ、通ること、ファイルが変わらないことを確かめた
- 定義の変更は Claude Code の再起動まで効かない。`check-agent-reply.py` では ytsched の定義を
  測れない（TODO-202）

## 残ること

- Codex 側の `.codex/agents/runner.toml`・`writer.toml` と `.agents/agents/runner.md`・`writer.md`、
  `.agents/skills/ytsched-workflow/SKILL.md` の runner の記述が、消した定義を指したまま残る
- verifier を haiku に上書きしたとき、定義の `effort: medium` がどう扱われるかは確かめていない
  （reviewer の指摘 C。`todo-workflow` では Haiku に effort は効かないとしている）

## 分担の振り返り

- **reviewer が見つけたもの:** ruff の書き換えと「コードを直さない」の矛盾（A）、
  落ちた出力の貼り方の食い違い（B）。どちらも main が統合したときに見落としていた。
  A は、グローバルの規則を反映する項目で新しい矛盾を持ち込むところだった
- **見込みとの食い違い:** 担当は見込みどおり。reviewer を 2 回呼んだ。2 回目は直した箇所だけを
  見させたので小さく済んだ
- **次に同じ規模なら:** 定義を統合する項目では、移した手順が移った先の「いちばん大事なこと」と
  ぶつからないかを、main が reviewer に回す前に 1 度読み合わせる。reviewer は省かない
