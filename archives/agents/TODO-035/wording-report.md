# TODO-035 wording 報告

対象: `TODO.md`（TODO-035 の節、`git diff HEAD -- TODO.md`）。
このコミットに入る `.md` は `TODO.md` のみ。

## 前例なしの語（件数が少ない順）

### 残枠（0 件）

- 箇所: 「残りトークンを手で書く」案だったが、**残枠**はリセットを
  跨ぐと差が壊れ、…採らない」
- `git grep -cF 残枠 HEAD -- '*.md'`: 前例なし
- 見立て: 一般に通用しそうな語ではある（トークンの残量、の意味で
  自然には読める）が、このリポジトリでの初出。「残りトークン」という
  言い換えが直前の同じ文にあり、そちらとの使い分けが曖昧。造語かどうか
  判断できない

### 指標（0 件）

- 箇所: 「指標は `output_tokens` と `cache_creation_input_tokens` を
  主にする」
- `git grep -cF 指標 HEAD -- '*.md'`: 前例なし
- 見立て: 一般的な IT・統計用語で、造語ではなさそう。ただしこの
  リポジトリでは初出

### トークン消費量（0 件）

- 箇所: 見出し「TODO 項目ごとのトークン消費量を記録する」
- `git grep -cF トークン消費量 HEAD -- '*.md'`: 前例なし
- 見立て: 「トークン」「消費」はいずれも一般語で、組み合わせも
  不自然ではない。問題なさそうに見える

### transcript（1 件）

- 箇所: 「Claude Code の transcript から集計する」
- `git grep -cF transcript HEAD -- '*.md'`: 1 件
  （`archives/agents/TODO-021/report.md` などに既出、要確認だが
  リポジトリ内に前例はある）
- 見立て: Claude Code 自身の用語（`~/.claude/projects/.../transcript`
  のファイル種別）なので専門用語としてそのまま使うのは妥当に見える

## 前例のあった語（参考、指摘には含めない）

- 「集計」: 4 件（TODO-007/018 の報告で既出）
- 「内訳」: 23 件（多数の報告で既出）
- 「見立て」「分担」「着手時」: いずれも 17〜91 件で定着した語
- `output_tokens` / `cache_creation_input_tokens` / `cache_read` /
  `subagents` / `始点` / `終点` / `遡れない` / `リセット` / `跨ぐ`:
  いずれも前例 0 件だが、`output_tokens` 等は Claude Code の transcript
  JSON のフィールド名をそのまま指しており、造語というより固有名。
  `始点` / `終点` / `遡れない` / `リセット` / `跨ぐ` は一般的な日本語
  そのままで、言い換えを作った様子は無い

## 読んだファイル

- `TODO.md`（差分部分。このコミットで唯一変更される `.md`）

## まとめ

前例の無い語（見立てが分かれるものも含め、指摘として挙げたもの）:
**「残枠」「指標」「トークン消費量」の 3 語。** いずれも一般的な語の
組み合わせに見え、TODO-021 の「足場」のような造語という印象は薄い。
`output_tokens` 系のフィールド名は固有名として除外した。

---

## 追記（決着コミット全体）

対象を、決着コミットに入る `.md` 全部へ広げて読み直した。

- `CLAUDE.md`（差分。「トークン消費量の記録」節）
- `TODO.md`（差分）
- `archives/todo/TODO-035. TODO 項目ごとのトークン消費量を記録する.md`（新規）
- `archives/agents/TODO-035/` の 8 ファイル全部（README、
  implementer-request/report、verifier-request/report、runner-report、
  writer-request/report）── 前回の指摘（`残枠` を書いた立案時点の
  `TODO.md` 節）は決着コミットで削除され、現物には残っていない
- `~/.claude/CLAUDE.md`（リポジトリ外。`git -c diff` で差分のみ確認。
  新規に足された文は「消費:」行の見本と、その説明段落）

### 検算スクリプト（0 件）

- 箇所: `verifier-report.md`「検算には、`tools/token-usage.py` とは
  別に自分で書いた検算スクリプトで…」、`README.md`
- `git grep -cF 検算スクリプト HEAD -- '*.md'`: 前例なし
  （「検算」単体は `archives/agents/TODO-021/README.md` に 1 件あり）
- 見立て: 「検算」＋「スクリプト」の組み合わせで、造語というより
  複合語。一般に通用しそうで、問題は薄い

### 見本（0 件）

- 箇所: `writer-request.md`「既にある `archives/todo/TODO-034 ….md`
  を、書き方の見本にする」、`writer-report.md`
- `git grep -cF 見本 HEAD -- '*.md'`: 前例なし
- 見立て: 一般的な日本語。造語ではなさそう

### 重複除去（0 件）

- 箇所: `implementer-request.md`「**重複行の除去（重要）**」、
  `verifier-report.md`「重複除去の妥当性」の見出し
- `git grep -cF 重複除去 HEAD -- '*.md'`: 前例なし
- 見立て: 一般的な IT 用語の複合。問題は薄い

### 割合（0 件）

- 箇所: `~/.claude/CLAUDE.md`「`output` と `cache_creation` の 2 つと、
  担当ごとの**割合**を 1 行で書く」、`archives/todo/TODO-035. ….md`
  「担当ごとの割合を 1 行だけ書く形にした」
- `git grep -cF 割合 HEAD -- '*.md'`: 前例なし（ytsched リポジトリ内）
- 見立て: ごく普通の語で、造語ではない

### 霞む（0 件）

- 箇所: `~/.claude/CLAUDE.md`「桁が 1 つ違い、貼ると他が霞む」、
  `archives/todo/TODO-035. ….md`「貼ると他の数字が霞む」
- `git grep -cF 霞む HEAD -- '*.md'`: 前例なし
- 見立て: 比喩的だが一般的な日本語表現。造語ではなさそう

### 落ち方（2 件）

- 箇所: `verifier-request.md`「**落ち方**（終了コードとメッセージ）が
  まともかを見る」、`verifier-report.md`「いずれも落ち方はまとも」
- `git grep -cF 落ち方 HEAD -- '*.md'`: 2 件（既に定着した言い回し）
- 見立て: 前例ありなので指摘不要（参考として記載）

### 主指標（0 件）

- 箇所: `implementer-request.md`「参考として別に出す（合計欄には
  入れるが、**主指標**と区別が付くように）」
- `git grep -cF 主指標 HEAD -- '*.md'`: 前例なし
  （「指標」単体も前例なし。前回の報告で既に指摘済み）
- 見立て: 「主」＋「指標」の一般的な組み合わせ。問題は薄いが、
  前回指摘した「指標」の変形として一応挙げる

### トークン消費量（0 件、再掲）

- 箇所: `CLAUDE.md`「### トークン消費量の記録」の見出し
  （`~/.claude/CLAUDE.md` には「トークン」の語自体が新規に入っていない）
- `git grep -cF トークン消費量 HEAD -- '*.md'`: 前例なし
- 見立て: 前回の報告と同じ。一般語の組み合わせで問題は薄いが再掲する

### 消費（既存語だが用法が新しい・参考）

- 箇所: `archives/todo/TODO-035. ….md` の `消費: TBD` → 実数、
  `~/.claude/CLAUDE.md` の骨格の見本に「消費:」行が新規に追加された
- `git grep -cF "消費:" HEAD -- '*.md'`: 前例なし（見出し語としての
  `消費:` 行そのものは今回が初出。「消費量」は既に 5 件ある）
- 見立て: 「見込み:」「実施:」と並ぶラベルとしての体裁で、既存の
  形式を踏襲している。造語というより運用ルールの一部

### 参考: 前例のあった語（指摘には数えない）

「鵜呑み」（3 件）「見落とし」（6 件）「潰して」（4 件）「取りこぼす」
（1 件）「決着」（16 件）「揃える」（49 件）はいずれも前例あり。
「検算」単体も前例 1 件（TODO-021）。「取り違える」「直し忘れ」
「ユニーク」「桁区切り」「立て直した」は前例 0 件だが、いずれも
一般的な日本語の言い回しで、見立てとしては問題が薄いと判断し、
指摘の中心には含めなかった（挙げるだけなら候補に入れてよいと
main が判断すれば追加できる）。

### 読んだファイル（追記分）

- `CLAUDE.md`（差分）
- `archives/todo/TODO-035. TODO 項目ごとのトークン消費量を記録する.md`
- `archives/agents/TODO-035/README.md`
- `archives/agents/TODO-035/implementer-request.md`
- `archives/agents/TODO-035/implementer-report.md`
- `archives/agents/TODO-035/verifier-request.md`
- `archives/agents/TODO-035/verifier-report.md`
- `archives/agents/TODO-035/runner-report.md`
- `archives/agents/TODO-035/writer-request.md`
- `archives/agents/TODO-035/writer-report.md`
- `~/.claude/CLAUDE.md`（`git -C ~/.claude diff -- CLAUDE.md` で差分のみ）

### まとめ（追記分）

前例の無い語として新たに挙げたもの: **「検算スクリプト」「見本」
「重複除去」「割合」「霞む」「主指標」「トークン消費量」（再掲）
「消費:」（ラベルとしての初出）の 8 件。** いずれも一般的な語の組み合わせに
見え、TODO-021 の「足場」のような造語という印象は薄いが、判断は main に
委ねる。前回（立案時点）の指摘「残枠」は決着コミットの現物には残って
いない。
