# TODO-069 wording 報告（2 回目）

対象は、TODO-069 のコミットに入る `.md` 全部。

- `TODO.md`
- `archives/todo/TODO-069. 数ヶ月ぶんの週を DOM に持ち、週移動でページを読み直さない.md`
- `archives/agents/TODO-069/README.md`
- `archives/agents/TODO-069/reviewer-report.md`
- `archives/agents/TODO-069/verifier-report.md`
- `src/README.md`（差分のみ）
- `tests/README.md`（差分のみ）

`TODO.md` は節の削除と目次への 1 行追加のみで、新しい語は無し。

前例の件数は `git grep -cF <語> HEAD -- '*.md'` の合計（HEAD＝このコミット前）。

## 前例の件数が少ない順

### 巻き添え（で消えない）
- 箇所: `archives/todo/TODO-069...md` 98行「他の設定を保存したときに巻き添えで消えない」
- 件数: 前例なし
- 見立て: 一般語ではあるが、この文脈（設定値が上書きで消えない）を指す言い回しとしてはこのリポジトリ初出。判断できない

### 揃え忘れ
- 箇所: `archives/agents/TODO-069/README.md` 22行「揃え忘れは実装者からは見えにくい」
- 件数: 前例なし
- 見立て: 「揃える」＋「忘れ」の複合。自然な日本語だが、このリポジトリでの言い回しとしては初出。造語というより普通の表現に見える

### ちらつき
- 箇所: `archives/todo/TODO-069...md` 122行「一瞬のちらつき」（reviewer-report.md にも同じ話が「見た目が飛ぶ」表現である）
- 件数: 前例なし
- 見立て: 一般的な IT 用語（画面のちらつき／flicker）。専門用語とみてよさそう

### 体感時間
- 箇所: `archives/agents/TODO-069/verifier-report.md` 49・54行
- 件数: 前例なし
- 見立て: 一般に通用する言い回し（実測値に対して人が感じる時間）。専門用語というより普通の日本語

### スワイプ相当
- 箇所: `archives/agents/TODO-069/verifier-report.md` 22行「スワイプ相当（mouse のドラッグ）でも週が送れる」
- 件数: 前例なし
- 見立て: 「スワイプ」自体は一般語だが、「〜相当」を付けた言い回しはこのリポジトリ初出。判断できない

### 前提の検証
- 箇所: `archives/agents/TODO-069/verifier-report.md` 50行「という前提の検証は、この計測方法では不十分だった」
- 件数: 前例なし
- 見立て: 一般的な言い回し。造語ではなさそう

### 枠組み
- 箇所: `archives/agents/TODO-069/reviewer-report.md` 82行「TODO-027 の枠組みをそのまま使っており」
- 件数: 前例なし
- 見立て: 一般語（framework の訳語として定着）。この文書での使い方も自然

### 揃え直す
- 箇所: `archives/agents/TODO-069/README.md` 22行、`archives/todo/TODO-069...md`（同じ箇所）
- 件数: 2 件（別の文脈）
- 見立て: 「揃える」の活用の一種。既存の「揃える」（79件）から自然に派生した言い回しに見える

### 決め打ち
- 箇所: `archives/agents/TODO-069/reviewer-report.md` 50行「`offset` が分からない＝範囲の外」と決め打ちしてしまっている」
- 件数: 6 件
- 見立て: 一般的な IT 表現として定着している語。問題なさそう

### 描き直し
- 箇所: `archives/todo/TODO-069...md` 28行、`archives/agents/TODO-069/README.md` 21行、`verifier-report.md` 50行
- 件数: 6 件
- 見立て: 「描き直す」の名詞形。既存の使われ方から自然な派生

### ダブルタップ
- 箇所: `archives/todo/TODO-069...md` 88・90行、`verifier-report.md` 20行、`src/README.md` 244行
- 件数: 7 件
- 見立て: 一般的な IT 用語（double tap）。問題なさそう

### フォールバック
- 箇所: `archives/agents/TODO-069/verifier-report.md` 35・36行「既定 1 ヶ月へフォールバック」
- 件数: 7 件
- 見立て: 一般に通用する IT 用語。問題なさそう

## 前例が複数あり、造語の疑いが薄いもの（参考）

- **見せる週**（`archives/todo/TODO-069...md` 61行、`src/README.md` 220行）: 件数 4。
  「表示する週」の言い換えとして自然だが、このリポジトリで定着した
  言い回しかは判断できない
- **絶対位置**（`archives/todo/TODO-069...md` 78行、`src/README.md` 239行）:
  件数 0 だが、CSS の `position: absolute` を指す一般的な IT 用語。
  専門用語とみてよさそう（前例が無いのは単に今回初めて使う概念のため）
- **通常フロー**（`src/README.md` 236行ほか、CLAUDE.md 由来の慣用ではなく
  CSS の normal flow の訳）: 件数 15。この文脈でも自然な用法
- **取り違えていた**（`archives/todo/TODO-069...md` 114行、
  `archives/agents/TODO-069/README.md` 30行）: 件数 0 だが、普通の日本語の
  言い回し。造語ではなさそう

## コード識別子（参考、造語の対象外）

- `LoadMonths`（`conf.json` のキー名）: 件数 0。これは呼び名というより
  新設した識別子そのものなので、一般語の造語とは性質が違う。参考として
  挙げるが、見立ては「該当なし」
- `months2weeks()`（関数名）: 件数 0。同上、識別子

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-069. 数ヶ月ぶんの週を DOM に持ち、週移動でページを読み直さない.md`
- `archives/agents/TODO-069/README.md`
- `archives/agents/TODO-069/reviewer-report.md`
- `archives/agents/TODO-069/verifier-report.md`
- `src/README.md`（差分箇所）
- `tests/README.md`（差分箇所）

## 前例の無い語数

7 語（巻き添え／揃え忘れ／ちらつき／体感時間／スワイプ相当／前提の検証／枠組み）。
参考として挙げた「絶対位置」「取り違えていた」も件数 0 だが、一般的な言い回し・
コード識別子に近く、他 7 語と性質が異なるため分けて記載した。
