# TODO-088 wording 報告

## 前置き（判断が要る点）

`archives/agents/TODO-088/implementer-request.md` は、`git log` で見ると
TODO-087 のコミット（`a5f8edf`）で既に入っており、`HEAD` に含まれている。
今回の依頼で対象に挙がっていたが、**今回のコミットの新規差分ではない**
（TODO-087 の wording 報告で一度読まれている）。以下では他のファイルを
中心に見て、このファイルは参考程度に留めた。

## 語ごとの確認（前例の件数が少ない順）

### 偽の差分

- 出てくる場所:
  - `verifier-report.md`「テストデータ作成の手順ミス（…）で『一覧が
    全部空になる』という偽の差分が一度出た」
  - `README.md`（結果の節）「途中、自分のデータの作り方の誤りで偽の
    差分を 1 度出した」
- `git grep -cF 偽の差分 HEAD -- '*.md'` → 前例なし
- 見立て: 「見かけ上の差分（実装のバグではない）」という意味で自然に
  通じる言い回しだが、この語自体は初出。一般語としても問題なさそうで、
  造語というより偶然の初出に見える

### 型的に

- 出てくる場所: `implementer-report.md`「`get()` 側で `search_mode` 判定後
  `search_re` を `SchedSearchCond` に渡す箇所は型的に
  `re.Pattern[str] | None` → `re.Pattern[str]` の絞り込みが要るため」
- `git grep -cF 型的に HEAD -- '*.md'` → 前例なし
- 見立て: 「型の面で」「型チェック上」の意で言いたいことは分かるが、
  「〜的に」を型に付ける言い方はこのリポジトリでは初出。判断できない
  （一般に通じるかは微妙）

### 型を絞り込む

- 出てくる場所: `README.md`「implementer が型を絞り込むために入れた
  `assert search_re is not None` を…」
- `git grep -cF 型を絞り込む HEAD -- '*.md'` → 前例なし
- 見立て: 型チェッカ文脈で「narrowing」を指す言い方として一般的に通じる
  表現に見える。このリポジトリでは初出なだけで、言い換えが必要とは
  思えない

### 潜り込み

- 出てくる場所: `verifier-report.md`「`cp -r data-old data-new` が
  `data-new/data-old/` に潜り込んでいた」
- `git grep -cF 潜り込み HEAD -- '*.md'` → 前例なし
- 見立て: 普通の日本語の比喩表現で、造語には見えない

## 前例が少数あった語（参考）

- **同着**（1 件、`archives/agents/TODO-028/reviewer-report.md`）—
  `reviewer-report.md` の「同着のときの並びに効く」で使用。同じ意味・
  同じ文脈（ソートの同順位）での前例が既にあり、問題なさそうに見える
- **実害無し**（1 件、`archives/agents/TODO-003/report-reviewer.md`）—
  `README.md`「main が直したもの」の節で使用。前例も同じ意味
- **書き分けた**（1 件、`archives/todo/TODO-017…md`。ただし文脈は
  「基準を文書ごとに書き分けた」で、今回の「分割前後のコードを
  1 行ずつ突き合わせて書き分けた」とは指すものがやや違う）—
  reviewer-report.md の結び近くで使用。同じ動詞の用法として大きな
  逸脱ではなさそう

## 読んだファイル

- `TODO.md`（差分）
- `src/README.md`（差分）
- `tests/README.md`（差分）
- `archives/todo/TODO-088. 一覧の組み立てと検索を分ける.md`
- `archives/agents/TODO-088/README.md`
- `archives/agents/TODO-088/implementer-request.md`（既に `HEAD` にあり、
  今回の新規差分ではない。参考として読んだのみ）
- `archives/agents/TODO-088/implementer-report.md`
- `archives/agents/TODO-088/verifier-request.md`
- `archives/agents/TODO-088/verifier-report.md`
- `archives/agents/TODO-088/reviewer-request.md`
- `archives/agents/TODO-088/reviewer-report.md`

## 前例の無い語の数

4 語（偽の差分、型的に、型を絞り込む、潜り込み）。
