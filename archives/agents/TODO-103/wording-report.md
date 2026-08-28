# TODO-103 wording 報告

対象は、このコミットに入る `.md` 全部（下記「読んだファイル」参照）。
`git grep -cF <語> HEAD -- '*.md'` で前例を数えた（作業ツリーではなく
`HEAD` を基準にしたので、TODO-103 自身の文書は数に入らない）。

前例の件数が少ない順に並べる。

## 埋めセル

- 出てくる箇所: `implementer-request.md`（決めてあること／確かめること）、
  `implementer-report.md`、`reviewer-report.md`、`verifier-request.md`、
  `verifier-report.md`、`README.md`、`archives/todo/TODO-103. 月間ミニ
  カレンダー.md` の複数箇所。「前後の月の埋めセル（`in_month` が偽）は
  タップさせない」など
- `git grep` の件数: 前例なし（0 件）
- 見立て: カレンダー UI で前月・翌月にはみ出す日付マスを指す語として、
  一般に「パディングセル」「先頭・末尾の空白セル」等の言い方もあるが、
  「埋めセル」という言い方自体は一般に定着したものではなさそう。ただし
  意味は文脈から明確で、リポジトリ内では一貫して同じ意味に使われている。
  このリポジトリだけの言い換えに見える

## 曜日ヘッダ

- 出てくる箇所: `implementer-report.md` 57 行目
  「テンプレートに曜日ヘッダ（月火水木金土日）を足した」
- `git grep` の件数: 前例なし（0 件）
- 見立て: 「曜日」＋「ヘッダ」は一般的な IT 用語の組み合わせで、
  特に不自然ではない。一般に通用しそう

## キャプション

- 出てくる箇所: `verifier-report.md` 85 行目
  「隣接する 2 ヶ月分のキャプション（例: `2026/08`→`2026/09`）」
- `git grep` の件数: 前例なし（0 件）
- 見立て: `.my-mini-cal-caption` という実装側のクラス名をそのまま
  日本語化した語。一般の IT 用語としては通用する（見出し・表題の意）。
  このリポジトリでは初出というだけ

## 枠色

- 出てくる箇所: `implementer-report.md` 25 行目
  「`.my-date-block-today` の枠色 `#28F` を流用」、`reviewer-report.md`
  58 行目、`archives/todo/TODO-103. 月間ミニカレンダー.md` 35 行目
- `git grep` の件数: 前例なし（0 件）
- 見立て: 「枠の色」を詰めた言い方。普通の日本語の範囲内で、造語という
  ほどではなさそう

## 軽さを取った

- 出てくる箇所: `README.md` 28 行目「反映しない（軽さを取った）」、
  `archives/todo/TODO-103. 月間ミニカレンダー.md` 38 行目
  「ToDo も数えない（軽さを取った）」
- `git grep` の件数: 前例なし（0 件）
- 見立て: 「（処理の）軽さを優先した」の意味で使われている。「軽さを
  取る」という言い回し自体は一般的とは言えず、造語ではないが独特の
  短縮表現に見える。「軽さを優先した」であれば普通の言い方になる。
  判断できないので、そのまま挙げる

## 見分けが付く／見分けられる

- 出てくる箇所: `implementer-request.md` 44 行目「見分けが付くように
  する」、`implementer-report.md` 22・47 行目、`verifier-report.md`
  33 行目、`verifier-request.md` 25 行目、いずれも「見分けられる」
- `git grep` の件数: 前例なし（0 件）
- 見立て: ごく普通の日本語の言い回し。造語ではない

## 読んだファイル

- `TODO.md`（TODO-103 の節を archives へ移した差分）
- `archives/todo/TODO-103. 月間ミニカレンダー.md`
- `archives/agents/TODO-103/README.md`
- `archives/agents/TODO-103/implementer-request.md`
- `archives/agents/TODO-103/implementer-report.md`
- `archives/agents/TODO-103/verifier-request.md`
- `archives/agents/TODO-103/verifier-report.md`
- `archives/agents/TODO-103/reviewer-request.md`
- `archives/agents/TODO-103/reviewer-report.md`
- `src/README.md`（差分箇所）

前例の無い語: 6 語（うち「見分けが付く／見分けられる」は普通の言い回し
で問題は薄いと見立てている）。
