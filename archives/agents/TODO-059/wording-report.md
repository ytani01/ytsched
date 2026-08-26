# TODO-059 wording 報告

## 読んだファイル

- `TODO.md`（差分）
- `archives/todo/TODO-059. ゲージの目盛りを詰めて、3m・3y・10y を足す.md`
- `archives/agents/TODO-059/README.md`
- `archives/agents/TODO-059/request-verifier.md`
- `archives/agents/TODO-059/verifier-report.md`
- `archives/agents/TODO-059/verifier-report2.md`

## 前例の無い語（前例の件数が少ない順）

### 相乗平均

- 出てくる箇所: `archives/todo/TODO-059. ….md` 49 行
  「対数目盛りなので、1 と 12 の相乗平均 √12 ≒ 3.46 の近く」
- `git grep -cF 相乗平均 HEAD -- '*.md'` → 前例なし
- 見立て: 数学の一般用語（幾何平均の別名）で、意味は通る。ただし
  このリポジトリでは初出。「幾何平均」という言い方も前例なし
  （`archives/agents/TODO-048/wording-report.md` に「幾何」という字は
  出るが文脈は別）。一般に通用する専門用語だと思うが、判断は main に委ねる

### 発散

- 出てくる箇所: `archives/todo/TODO-059. ….md` 19 行
  「対数が発散しないように足していた値」
- `git grep -cF 発散 HEAD -- '*.md'` → 前例なし
- 見立て: 「`log10(0)` が `-∞` に向かう」ことを指した比喩的な使い方。
  数学・工学では一般的な言い回し。造語というより専門用語の転用に見えるが、
  この文書だけを読むと「発散」が何を指すか自明ではない（式を見て
  初めて分かる）ので、言い換えの余地があるかは main の判断

### 割る数

- 出てくる箇所: `archives/agents/TODO-059/request-verifier.md` 16 行
  「割る数 `DAYS_GAGE_K` は 10」
- `git grep -cF 割る数 HEAD -- '*.md'` → 前例なし
- 見立て: 「除数」の言い換えとして作った可能性がある普通の言い方。
  一般的な日本語ではあるが、数式の用語としては「除数」のほうが定着している。
  リポジトリだけの言い換えに見える

### 浮動小数

- 出てくる箇所: `archives/agents/TODO-059/verifier-report2.md` 10 行
  「両者の出力は完全一致（浮動小数の桁まで同一）」
- `git grep -cF 浮動小数 HEAD -- '*.md'` → 前例なし
  （`浮動小数点` という完全形の前例も無し）
- 見立て: 一般には「浮動小数点（数）」で、「浮動小数」は省略形。
  意味は通じるが、正式な用語を短くした独自表記に見える

## 前例はあるが、依頼書で名指しされていた語（参考）

- 「逆算」（`TODO-059. ….md` 48 行）: `git grep -cF 逆算 HEAD -- '*.md'`
  → 3 件（`archives/agents/TODO-043/` 系）。前例あり
- 「頭打ち」（`TODO-059. ….md` ほか）: 10 件（`TODO-058` 系ほか）。前例あり
- 「目盛りの間隔」「余白」「重なり」「重なる」: いずれも前例あり
  （`TODO-042`・`TODO-043`・`TODO-058` などで繰り返し使われている）

## 前例の無い語の数

**4 語**（相乗平均・発散・割る数・浮動小数）
