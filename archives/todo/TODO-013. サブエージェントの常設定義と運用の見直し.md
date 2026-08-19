# TODO-013. サブエージェントの常設定義と運用の見直し

見込み: main = Opus 5 / effort high、担当 = main のみ
実施: main = Opus 5 / effort high、担当 = main のみ

## きっかけ

TODO-002（uv プロジェクトへの移行）を、その場で書いた使い捨ての定義
（`migrator` / `verifier`）で実施した。**実装と確認を別のエージェントに
分けた効果が大きかった**ので、これを常設の仕組みにする。優先順位は
品質 ＞ 利用者の手間削減 ＞ トークン削減。

常設にする理由は 3 つ。

1. **effort は定義ファイルの frontmatter でしか指定できない。**
   Agent ツールに渡せるのはモデルだけ
2. **分担の確認を「項目を立てるとき」に前倒しできる。**
   項目に担当を書いておけば、着手時に分担案を出して承認を待つ手順が要らない
3. プロジェクトの前提（データ形式、`tmr` に揃える、シェルのエイリアス）を
   定義に持たせれば、依頼のたびに書き写さなくて済む。書き写しの漏れも防げる

## やったこと

### `.claude/agents/` に 4 つ置いた

役割は**工程で切った**（ドメインで切ると使い回せない）。4 個に絞ったのは、
使われない定義が読むときのノイズになるため。

| 名前 | model / effort | 役割 | tools |
|---|---|---|---|
| `implementer` | opus / high | 実装。変更・新規作成・リファクタリング | Read, Write, Edit, Bash, Grep, Glob, WebFetch |
| `verifier` | sonnet / medium | 実際に**動くか**。テスト・lint・起動確認 | Read, Write, Bash, Grep, Glob |
| `reviewer` | opus / high | コードが**良いか**。正しさ・設計・決まりからの逸脱 | Read, Write, Bash, Grep, Glob |
| `writer` | sonnet / medium | README、CLAUDE.md、archives などの文書 | Read, Write, Edit, Bash, Grep, Glob |

- **`verifier` と `reviewer` には `Edit` を持たせていない。**
  見つけたことは報告させ、直すかどうかは管理者が判断する
- `verifier`（動くか）と `reviewer`（良いか）は役割が違うので分けた
- 4 つとも末尾に共通のブロック（このプロジェクト / 決まりごと /
  シェルの注意）を持たせた。依頼のたびに書き写さずに済む
- `description` に「main（管理者）から名指しされたときだけ使う。
  自動では起動しない」と書いた。書き方次第で意図しない自動委譲が起きるため
- **報告はファイル、返事は要点のみ**（`archives/agents/TODO-NNN/report-<担当名>.md`）
  を各定義の「報告に書くこと」に入れた

### `~/.claude/CLAUDE.md` の運用を 5 点直した

- `.claude/agents/*.md` を archives へ**移さない**。使い回すものなので
  git 管理下に残し、archives には分担・理由・報告だけを残す
- 「規模の大きい項目は編成する」→ **確認担当は規模によらず必ず立てる。**
  実装担当を分けるかどうかを規模で決める。決めるだけの項目は例外
- **`見込み:` `実施:` の行に、main のモデル・effort と担当を書く。**
  担当のモデルと effort は定義ファイル側にあるので書かない
- 分担は**項目を立てるときに決める**。着手時の分担確認は不要にした
- **報告はファイル、返事は要点のみ**という指示を定型にした

### 残っている項目の `見込み:` 行を直した

TODO-003〜TODO-010、TODO-012 の `見込み:` を新しい形にして、担当を書いた。

**決着済みの項目（`archives/todo/`）の `見込み:` `実施:` 行は書き換えていない。**
そのときの記録なので、古い形式のまま残す。

## テスト

`.claude/agents/` は Claude Code の**起動時にしか読まれない**ので、
利用者が再起動してから確認した。

- 再起動後のセッションで、`implementer` / `verifier` / `reviewer` / `writer`
  の 4 つとも、利用可能なエージェントの一覧に出た
- 一覧に出た `description` と `tools` が、定義ファイルの frontmatter と一致した
  （`verifier` と `reviewer` に `Edit` が無いことも確認）
- 「main から名指しされたときだけ使う」の文言も `description` に載っている

`effort` は一覧に出ないので、frontmatter の記述で確認した。

## この項目自体は分担しなかった

定義そのものを作る項目なので `担当 = main のみ`。
`archives/agents/TODO-013/` は作っていない。
