# TODO-047 wording 報告（決着コミット）

対象は依頼にある 10 ファイル（`TODO.md`・`README.md` は差分のみ、他 8 件は
新規全文）。前例の有無は `git grep -cF <語> HEAD -- '*.md'` で数えた
（`HEAD` はこのコミット前）。前例なしの語数順に並べる。

## 前例なしの語

- **ガター（溝）**
  出典: `archives/todo/TODO-047. ….md`「ガター（溝）は Bootstrap と
  同じ `1.5rem`」、`implementer-request.md`「ガター（溝）を落とさない
  こと」。CSS の gutter の訳語として「ガター」「溝」の両方を使っている。
  前例: 0 件（両方とも）
  見立て: CSS 分野では "gutter" は一般語だが、カタカナ表記も和訳も
  このリポジトリでは初出。技術用語としては妥当な訳に見えるが、初出
  であることは事実

- **写し漏れ**
  出典: `archives/todo/TODO-047. ….md`「写し漏れが無いか」、
  `reviewer-request.md`・`reviewer-report.md` に多数
  前例: 0 件
  見立て: 「写す」＋「漏れ」の複合で意味は通るが、この言い回し自体は
  初出。「写し間違い」（前例 3 件）とは別語

- **総当たり**
  出典: `archives/todo/TODO-047. ….md`「ショートハンドの展開込みで
  総当たりし」、`reviewer-report.md`「機械的に総当たりした」
  前例: 0 件
  見立て: 一般語（総当たり法）だが、このリポジトリでは初出

- **机械的（に集める）**
  出典: `reviewer-report.md`「機械的に集め」「機械的に総当たりした」
  前例: 0 件
  見立て: ごく普通の日本語で問題ないと思うが、初出ではある

- **黙って壊れる**
  出典: `archives/todo/TODO-047. ….md`「黙って壊れる書き方が無いか」、
  `implementer-request.md`「黙って壊れる書き方があれば挙げる」
  前例: 0 件（「黙って」単独では `git grep 静かに` などの類義語に 1 件
  あるのみで別語）
  見立て: 意味は明確だが、この言い回しをこのリポジトリの決まった呼び名
  として使い始めている。造語というより比喩的表現で、次から自然に
  再利用されそうな語

- **位相／位相差**
  出典: `archives/todo/TODO-047. ….md`「`blink` の位相が撮るたびに
  違う」、`verifier-report.md`「blink 位相差のみ」
  前例: 0 件
  見立て: 一般の技術用語（物理・信号処理の「位相」）だが、この
  リポジトリでは初出

- **土台の指定**
  出典: `archives/todo/TODO-047. ….md`「Bootstrap に任せていた土台の
  指定（reboot。…）」
  前例: 0 件（「土台」単独は 6 件の前例あり、「土台の指定」という
  組み合わせは初出）
  見立て: 「土台」は既に使われている語の延長で、大きな飛躍ではない

- **縦の位置**
  出典: `archives/agents/TODO-047/README.md`「アイコンの縦位置」は
  別表記で 0 件、依頼書・報告書中の「縦の位置」（`implementer-request.md`
  「どちらの意味で使っている箇所なのか」の近く。正確には
  TODO-047 archive 内の見出し「縦の位置」）
  前例: 0 件。ただし類義の「縦位置」（送り仮名なし）は 27 件の前例あり
  見立て: 表記ゆれ。意味は同じなので造語というより言い回しの違い

- **permission notice / substantial portion**
  出典: `reviewer-report.md`「MIT が要求している permission notice の
  本文」「substantial portion に当たらない」
  前例: 0 件
  見立て: MIT ライセンス文の引用語句としてそのまま使っており、造語では
  ない。英語の専門用語（ライセンス文の決まり文句）としては妥当

- **告知**
  出典: `reviewer-report.md`「告知はこのコメントに残す」「告知の重さの
  見え方」
  前例: 0 件
  見立て: 一般語で問題なさそうだが初出

- **孫**
  出典: `TODO.md`（TODO-049/050 への追記）「`.longtext`（詳細の欄）を
  `row` の孫にしないこと」、`archives/todo/TODO-047. ….md` にも同旨
  前例: 0 件
  見立て: DOM 木構造の比喩として「子」「孫」を使うのは一般的で自然。
  問題なさそうだが初出

- **百分率／分け合う**
  出典: `reviewer-report.md`「百分率の幅（`91.66666667%`）と Grid の
  `1fr` の丸めの違い」「余った幅を分け合う」
  前例: 0 件（両方）
  見立て: ごく普通の日本語・数学用語で、造語ではない

## 前例が少ないが 0 ではない語（参考）

- **抜けやすい**（`archives/todo/TODO-047. ….md`「ここがいちばん抜け
  やすいところ」）前例 2 件。見立て: 問題なさそうな普通の言い回し
- **撮り直し**前例 2 件。見立て: 問題なさそうな普通の言い回し

## 前例があり、挙げなかった語（判断材料として記載）

「土台」（6 件）「詳細度」（5 件）「reboot」（7 件・そのまま英語表記）
「打ち消す／打ち消し」（8/7 件）「はみ出す」（5 件）「折り返す／
折り返し」（4/13 件）「覚書」（11 件）「継ぐ」（10 件）「突き合わせ」
（36 件）「実測」（100 件）「網羅」（5 件）「縦位置」（27 件）
「写し間違い」（3 件）「specificity」（2 件）「flexbox」（3 件）は
既に使われているので前例ありとして除外した。

## 読んだファイル

- `TODO.md`（差分）
- `README.md`（差分）
- `archives/todo/TODO-047. Bootstrap をやめて、素の CSS にする.md`
- `archives/agents/TODO-047/README.md`
- `archives/agents/TODO-047/implementer-request.md`
- `archives/agents/TODO-047/implementer-report.md`
- `archives/agents/TODO-047/verifier-request.md`
- `archives/agents/TODO-047/verifier-report.md`
- `archives/agents/TODO-047/reviewer-request.md`
- `archives/agents/TODO-047/reviewer-report.md`

## 前例なしの語数

13 語（ガター／溝を分けて数えると 14）。
