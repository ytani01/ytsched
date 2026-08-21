# TODO-026 wording 確認報告（対象: このコミット、ステージ済み）

`~/work/ytsched/TODO.md` の TODO-026（および決着済みファイル
`archives/todo/TODO-026. 文書の確認の担当と hook を作る.md`）を読んでから、
`.claude/agents/wording.md` の手順に沿って作業した。前例の基準は `HEAD`
（＝ `f5326d5`）。文書は直していない。

## 対象ファイル（16 個、`git diff --cached --name-only -z` で拾った全部）

- `.claude/agents/wording.md`
- `CLAUDE.md`（追記分のみ）
- `TODO.md`（追記・移動分のみ）
- `archives/agents/TODO-026/README.md`
- `archives/agents/TODO-026/implementer-report.md`
- `archives/agents/TODO-026/implementer-report2.md`
- `archives/agents/TODO-026/implementer-request.md`
- `archives/agents/TODO-026/implementer-request2.md`
- `archives/agents/TODO-026/reviewer-report.md`
- `archives/agents/TODO-026/reviewer-request.md`
- `archives/agents/TODO-026/verifier-report.md`
- `archives/agents/TODO-026/verifier-report2.md`
- `archives/agents/TODO-026/verifier-request.md`
- `archives/agents/TODO-026/wording-report.md`
- `archives/todo/TODO-026. 文書の確認の担当と hook を作る.md`

## 前例の無い語（`git grep -cF <語> HEAD -- '*.md'` が 0）

前例の件数が少ない順（すべて 0 件のため、目についた順に近い並びにした）。

### 1. リグレッション

- **出てくる箇所**: `implementer-report2.md:95`
  「### リグレッション（前回すでに確かめてあった経路）」（見出し）
- **件数**: 前例なし（0 件。`リグレッションテスト`で引いても 0 件）
- **見立て**: "regression"（回帰）のカタカナ表記で、一般に通用する
  IT 用語。利用者の `~/.claude/CLAUDE.md` 自体が「回帰テスト」ではなく
  「リグレッションテスト」を使えと明記しており、**むしろ推奨される側の
  語**。造語ではないと判断できる。

### 2. 前方一致

- **出てくる箇所**: `reviewer-report.md:25,40,42`
  （「permission rule の Bash マッチは**コマンド文字列の前方一致**で」等）
- **件数**: 前例なし（0 件）
- **見立て**: 文字列照合の一般的な IT 用語（"prefix match"）。造語では
  ないと判断できる。

### 3. 拾いすぎる側（に倒す）

- **出てくる箇所**: `implementer-report.md:63,162`、`reviewer-report.md:155`、
  `archives/todo/TODO-026. 文書の確認の担当と hook を作る.md:54`
  （「`git commit` の判定を『拾いすぎる側』に倒した」）
- **件数**: 前例なし（0 件。「側に倒す」で引いても 0 件）
- **見立て**: 「安全側に倒す」「〜側に倒す」はエンジニアリングの議論で
  よく使われる一般的な言い回しで、造語には見えない。ただし「拾いすぎる」
  という具体的な言い方自体はこのリポジトリで初出。判断できないというより
  「たぶん自然な日本語」に近いが、念のため挙げる。

### 4. 使い捨てリポジトリ

- **出てくる箇所**: `verifier-report.md:4,10`、`verifier-report2.md:3,5,81`、
  `implementer-report.md:104`、`implementer-report2.md:80`、
  `implementer-request2.md:73`、`reviewer-report.md:85` など計 9 か所
- **件数**: 前例なし（0 件。「使い捨て」単独では既に 3 件の前例あり
  ＝ `TODO-002`・`TODO-013`・`TODO-017` の archive）
- **見立て**: 「使い捨て」＋「リポジトリ」の自然な組み合わせで、
  一般に通用する言い方。造語には見えない。

### 5. 効かせる

- **出てくる箇所**: `CLAUDE.md:188`（「hook を効かせるには
  `.claude/settings.json` が読まれている必要がある」）、
  `archives/todo/TODO-026. 文書の確認の担当と hook を作る.md:123`、
  `implementer-report.md:190`、`implementer-report2.md:158`
- **件数**: 前例なし（0 件）
- **見立て**: 「効く」の使役形で、ごく普通の日本語動詞。造語ではないと
  判断できる。

### 6. 余計に促す

- **出てくる箇所**: `implementer-request2.md:48`、`implementer-report2.md:93`
  （「main が承知のうえで許容した『余計に促す』場面」）
- **件数**: 前例なし（0 件。「促す」単独では 3 件の前例あり）
- **見立て**: 「促す」＋「余計に」の自然な組み合わせ。造語には見えない。

### 7. 見送り（名詞形）

- **出てくる箇所**: `implementer-report2.md:4,135`
  （「見送りの指示どおり」「依頼書の指示どおり見送り」）
- **件数**: 前例なし（0 件。動詞形「見送る」は既に 2 件の前例あり）
- **見立て**: 「見送る」の名詞形で、ごく普通の日本語。造語には見えない。

## 判断できないもの（見つからず）

**今回、リポジトリ固有の言い換えに見える語（TODO-021 の「足場」のような
もの）は見つからなかった。** `まとめ役`・`呼び出し口`・`受け側`・
`かたまり`・`差し戻す`・`素通り`・`足場`・`ゴールデンマスターテスト` は
`archives/agents/TODO-026/wording-report.md` の中で TODO-021 のコミット
（`95895c1`）を再現するために引用されているが、これらの語自体は
すでに `HEAD`（`archives/agents/TODO-021/` 等）に前例があるため、
今回のリストには含めない（それぞれ 1〜14 件の前例あり）。

## 読んだファイル

「対象ファイル」に挙げた 15 個（`CLAUDE.md`・`TODO.md` は追記・移動分
のみ差分で確認）。

## 前例の無い語数

**7 語**（リグレッション・前方一致・拾いすぎる側・使い捨てリポジトリ・
効かせる・余計に促す・見送り）。

TODO-025 の目安（造語入りの報告は 15 語、造語なしの依頼書・archive は
1〜3 語）と比べると、7 語は中間よりやや少ない側。ただし**7 語すべてが、
すでにある語の自然な組み合わせか、一般に通用する IT・日本語の語**で、
「足場」のようなリポジトリ固有の言い換えは 1 つも見つからなかった。
main の判断が要る点は特に無い。
