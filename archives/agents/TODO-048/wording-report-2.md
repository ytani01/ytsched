# TODO-048 wording 報告（2 回目）

対象は次の 8 ファイル。`TODO.md` と `README.md` は `git diff` の差分のみ、
残り 6 つは新規ファイルなので全文を読んだ。

- `TODO.md`（TODO-048 の節の差分）
- `README.md`（「外部のライブラリ」節）
- `archives/agents/TODO-048/implementer-request.md`
- `archives/agents/TODO-048/implementer-report.md`
- `archives/agents/TODO-048/verifier-request.md`
- `archives/agents/TODO-048/verifier-report.md`
- `archives/agents/TODO-048/verifier-request-2.md`
- `archives/agents/TODO-048/verifier-report-2.md`

前例は `git grep -cF <語> HEAD -- '*.md'` で数えた（`HEAD` = `ba1d735`。
TODO-048 の 1 回目のコミットがすでに入っているため、`TODO.md` 自身の
前回分はここでの前例に含まれる）。

## 前例の無い語（件数の少ない順）

### 字送り／字送りの箱

- 箇所: `archives/agents/TODO-048/verifier-request-2.md:12`
  「字面が字送りの箱からはみ出して描かれ」、`TODO.md:143` に同じ文が
  再掲されている
- 前例: 0 件
- 見立て: 「字送り」自体は活字組版の用語（文字を送る幅）として一般に
  通用するが、「字送りの箱」という言い回しはこのリポジトリ初出。
  文脈からは意味が通るが、一般語かこの文書だけの言い換えかは
  判断できない

### 対応表

- 箇所: `implementer-request.md:16`「## 置き換えの対応表」、
  `verifier-request.md:7,34`、`verifier-report.md:24,26`
- 前例: 0 件
- 見立て: 一般的な日本語（対応関係を表にしたもの）で、造語には見えない

### 消し残し

- 箇所: `implementer-request.md:151`「消し残しが無いこと」、
  `implementer-report.md:55,76`、`verifier-request.md:38`、
  `verifier-report.md:32,36,66`
- 前例: 0 件
- 見立て: 「消し忘れ」の言い換えとして自然で、意味も一読で通る。
  一般語だと思うが、このリポジトリでの言い回しとしては初出

### 外部のライブラリ

- 箇所: `README.md:204`（見出し）、`verifier-request.md:56`、
  `verifier-report.md:47`
- 前例: 0 件（「外部の」「ライブラリ」それぞれは既出だが、この組み合わせは
  初出）
- 見立て: 普通の名詞の組み合わせで、造語というほどのものではないと思う

### 検索バー

- 箇所: `verifier-report.md:17,22,28`
- 前例: 0 件
- 見立て: 一般的な UI 用語（検索欄・検索ボックスと同義）。この
  リポジトリでは初出だが、通用する語だと思う

### 効き方

- 箇所: `implementer-request.md:107`「効き方が変わる」、
  `implementer-report.md:42`「同じ効き方になる」
- 前例: 0 件
- 見立て: 「（スタイルなどが）どう作用するか」という意味で通る普通の
  言い回し。造語というより口語的な表現

### 崩れなし

- 箇所: `TODO.md:151`「『崩れなし』と報告してきていて」、
  `verifier-report.md:43`、`verifier-report-2.md:48`
- 前例: 0 件（「崩れ」自体は前例 33 件あるが、「崩れなし」という
  形は初出）
- 見立て: 「崩れ」の対比として自然な省略形。造語というより口語的な
  短縮

## 前例があり、造語ではないと判断した語（参考）

`字面`（55 件）、`崩れ`（33 件）、`縦位置`（十数件）、`詰まり具合`・
`行の詰まり具合`（TODO.md 内に前例）、`スプライト`・`確認用ページ`・
`派生物`・`描き直し`・`帰属表示`（いずれも TODO.md の 1 回目のコミット
分に前例あり）、`対応表`以外の`図案`・`線画`・`字形`・`土台`・`覚書`・
`決着`・`由来`・`塗りつぶし`・`輪郭`・`画素`・`開閉スイッチ`（前例 1 件、
TODO-046 のアーカイブ）は、いずれも前例が複数件あるか、TODO-048 自身の
1 回目のコミットで既に使われている語だったため、今回の指摘からは外した。

## 読んだファイル

上記 8 ファイル（`TODO.md` と `README.md` は差分のみ）。

## 前例なしの語数

**7 語**（字送り／字送りの箱を 1 組として数えた場合）。
