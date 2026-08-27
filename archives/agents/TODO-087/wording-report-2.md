# TODO-087 wording 報告（2 回目・コミット直前の確認）

対象: `TODO.md`（差分）、`src/README.md`（差分）、
`archives/todo/TODO-087. 更新の実行を MainHandler から出す.md`（新規）、
`archives/agents/TODO-087/{README,implementer-request,implementer-report,
verifier-request,verifier-report,reviewer-request,reviewer-report}.md`（新規）。

`wording-report.md`（項目を立てたときの報告）は対象外・未変更。

前例の確認は `git grep -cF <語> HEAD -- '*.md'`（無ければ 0）。

## 前例の件数が少ない順

### 所見（0 件）— 要注意

- 出てくる箇所: `reviewer-report.md` の見出し「## 確信度の低い所見」
- `git grep -cF 所見 HEAD -- '*.md'` → 0 件
- 見立て: **このリポジトリの reviewer 報告では、同じ意味の節見出しに
  「確信度が低いもの」「確信度が低い指摘」「確信度の低い所感」
  （TODO-005, 006, 020, 021, 026, 027, 029, 038, 039, 044, 047, 049,
  050, 054, 055, 057, 058, 063, 064, 069, 081, 083 など多数）が
  既に定着している。「所感」という近い既存語があるのに「所見」に
  なっており、`.claude/agents/reviewer.md` 側の言い回し
  （「確信度の高い/低い」）とも表記が微妙にずれている。今回は節の
  中身が「無し」の 1 行なので実害は薄いが、TODO-021 の「足場」と
  同型（既存語があるのに言い換えている）に見える

### 実行そのもの（0 件）

- 箇所: `archives/todo/TODO-087. …md`「`exec_update()` — 引数の取り出しを
  除いた、実行そのもの」
- 見立て: 一般的な言い回しで、造語というより単なる説明。前例が無いのは
  単に使う機会が無かっただけに見える

### 引きずる（0 件）

- 箇所: `implementer-request.md`「これらを一緒に引きずることになり」
  （`archives/todo/TODO-087…md` にも同旨の文）
- 見立て: 一般的な比喩表現。専門用語ではない

### ぼやける（0 件）

- 箇所: `implementer-request.md`「モジュールの役割がぼやける」
- 見立て: 一般的な語。問題なさそう

### 旧い（1 件、TODO-070 と別文脈）

- 箇所: `implementer-report.md`「テストの docstring に残った旧い言い回し」
- `git grep -cF 旧い HEAD -- '*.md'` → 1 件（別項目の別文脈）
- 見立て: 「古い」の表記揺れ。誤字ではないが、リポジトリ内で
  「古い」表記が普通に使われている中での「旧い」は目立つ。
  判断できないので main に委ねる

### の受け取り（1 件、TODO-070 と別意味）

- 箇所: `src/README.md`「一覧表示と、追加/修正/削除の**受け取り**を兼ねる」
  （旧文言は「実行」だった）
- `git grep -cF "の受け取り" HEAD -- '*.md'` → 1 件（TODO-070 verifier-report、
  「戻り値の受け取り」という別の意味）
- 見立て: 「`MainHandler` は cmd を受け取るだけ、実行するのは
  `SchedUpdater`」という役割の変化を表す新しい言葉遣いとして自然で、
  一般的にも通じる。造語というより設計変更を反映した用語の更新に見える

## 前例が十分にあり、問題なさそうな語（参考）

- 突き合わせ（96 件）、断る（7 件）、兼ねる（6 件）、含み（3 件）、
  受け取り（4 件）— いずれもこのリポジトリで定着した言い回し

## 読んだファイル

- `TODO.md`（差分）
- `src/README.md`（差分）
- `archives/todo/TODO-087. 更新の実行を MainHandler から出す.md`
- `archives/agents/TODO-087/README.md`
- `archives/agents/TODO-087/implementer-request.md`
- `archives/agents/TODO-087/implementer-report.md`
- `archives/agents/TODO-087/verifier-request.md`
- `archives/agents/TODO-087/verifier-report.md`
- `archives/agents/TODO-087/reviewer-request.md`
- `archives/agents/TODO-087/reviewer-report.md`

## 前例なしの語数

5 語（所見・実行そのもの・引きずる・ぼやける、うち「旧い」「の受け取り」は
前例 1 件ずつで別文脈のため別枠扱い）。うち「所見」は既存語（所感／
確信度が低いもの）への言い換えに見え、要注意。
