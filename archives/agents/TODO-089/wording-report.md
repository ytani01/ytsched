# TODO-089 wording 報告

このコミットに入る `.md` 7 本を読み、`git grep -cF <語> HEAD -- '*.md'` で
前例を数えた。基準は HEAD（43d43d2）。前例なしの語を、件数の少ない順に挙げる。
**直すかどうかは main が決める。**

## 前例の無い語

### 1. デデント / ディデント

- **出てくる箇所**
  - `implementer-report.md`「全体を 4 スペースぶん**ディデント**（`main-page.js`
    はトップレベルが桁 0）」
  - `verifier-request.md`「全体を 4 スペースのインデント、行末スペースの除去」
    （ここは「インデント」）
  - `verifier-report.md`「4 スペース**デデント**・行末スペース除去」
    「先頭コメント追加 / … / 4 スペース**デデント**・行末スペース除去」
  - `TODO-089` archive にはこの語は無く「インデントだけ」と書かれている
- **`git grep` の件数** — 前例なし（`インデント` は 7 件、`字下げ` は 6 件）
- **見立て** — 英語 dedent の音写。表記が 2 通り（`ディデント` と `デデント`）に
  割れており、担当それぞれの造語に近い。一般には「インデントを外す」「字下げを
  戻す」「桁を 0 に戻す」などと書く。**言い換えたほうがよい**。

### 2. 定数ブロック

- **出てくる箇所**
  - `implementer-request.md`「`main.html` のような**定数ブロック**は要らない」
  - `implementer-report.md`「テンプレートの値（`{{ }}`）は 1 つも使っていないので
    **定数ブロック**は作っていない」
  - `TODO-089` archive「`main.html` のような**定数ブロック**は要らなかった」
- **`git grep` の件数** — 前例なし（`定数` 単独は 65 件）
- **見立て** — `<script>` 内にテンプレート値の `const` を並べた部分を指す
  この文書群だけの略称。造語寄り。「テンプレートの値を置く `<script>`」の
  ような説明にできる。判断は main。

### 3. 許容差分

- **出てくる箇所** — `verifier-report.md`「依頼書の**許容差分**（先頭コメント
  追加 / `onloadHdr`→`onloadEdit` の 2 か所 / … / 4 スペースデデント …）を
  適用して `edit-page.js` と diff」
- **`git grep` の件数** — 前例なし
- **見立て** — 「依頼書が許している差分」の圧縮表現。造語寄り。「許してある
  差分」「認めた差分」などで足りる。判断は main。

### 4. 読み込み時ハンドラ

- **出てくる箇所** — `TODO-089` archive「`spinner.js` の `pageshow` の説明に
  あった『各ページの `onloadHdr()`』を『**読み込み時ハンドラ**（`onloadHdr()`
  / `onloadEdit()`）』に直した」
- **`git grep` の件数** — 前例なし（`load ハンドラ` 2 件、`load リスナー` 0 件、
  `リスナー登録` 4 件）
- **見立て** — `load` イベントで呼ぶ関数をまとめて指す言い換え。造語というより
  素直な説明句だが、リポジトリでは `load` ハンドラ / `load` リスナーと英語で
  書いてきたので表記がここだけ揺れる。判断は main。

### 5. 名前衝突

- **出てくる箇所**
  - `implementer-request.md`「`onloadHdr()` の**名前衝突**を解く」
  - `TODO-089` archive「`main-page.js` との**名前衝突**を解く」
- **`git grep` の件数** — 前例なし（`衝突` 単独は 15 件。`名前の衝突` は 0 件）
- **見立て** — name collision / naming conflict の定訳で、一般に通用する
  専門用語。**このリポジトリでは初出**というだけ。造語ではない。

### 6. 字句（字句レベル / 字句一致 / 字句比較 / 字句レベルで一致）

- **出てくる箇所**
  - `implementer-report.md`「関数・定数の中身は不変」の周辺、
    `verifier-request.md`「**字句レベル**で一致していることの確認」「`<script>` の
    中身と `edit-page.js` を比べる」
  - `verifier-report.md` 見出し「4. **字句一致** — おおむね一致」
  - `README.md`（agents）「元のインライン `<script>` との**字句一致**の確認」
  - `TODO-089` archive「元の `edit.html` の `<script>` の中身と `edit-page.js` を
    **字句比較**し」
- **`git grep` の件数** — 前例なし（`字句` を含む語すべて 0 件）
- **見立て** — 「字句」はコンパイラ用語（字句解析 = lexical analysis）としては
  一般的だが、ここでは「一字一句そのまま」「文字どおり」の意味で使っている。
  厳密には別概念で、やや独自の使い方。「一字一句の比較」「文字どおり一致」に
  すると誤解が無い。判断は main。

## 前例はあるが一応触れておく語

- **行末スペース**（`implementer-report.md` / `verifier-request.md` /
  `verifier-report.md`）— `行末スペース` そのものは 0 件だが、`行末の余分な
  空白`（TODO-004）・`行末の `\r``（TODO-029 ほか多数）と、概念は既出。
  圧縮しただけで造語ではない。
- **退行**（`implementer-report.md` / `verifier-report.md`「退行なし」
  「退行していない」）— 59 件。TODO-056 のタイトルで既に使用。前例あり。
- **揺れ**（`implementer-report.md`「タイミングの揺れ」「既知の揺れ」）—
  13 件。フレーキーなテストの言い換えとして既出。前例あり。
- **新事実 / 事実関係**（`implementer-report.md`「単独で決めた判断」）—
  どちらも 0 件だが普通の日本語。造語ではない。

## まとめ

- **読んだファイル（7 本）**
  - `src/README.md`（HEAD との差分。「ブラウザ側のスクリプト」の節）
  - `archives/agents/TODO-089/implementer-request.md`
  - `archives/agents/TODO-089/implementer-report.md`
  - `archives/agents/TODO-089/verifier-request.md`
  - `archives/agents/TODO-089/verifier-report.md`
  - `archives/agents/TODO-089/README.md`
  - `archives/todo/TODO-089. edit.html の JavaScript を edit-page.js へ出す.md`
- **前例なしの語** — 6 件（`デデント`/`ディデント` を 1 件、`字句`系を 1 件と
  数えて）。うち造語寄りは `デデント`/`ディデント`・`定数ブロック`・
  `許容差分` の 3 つ。`名前衝突` は一般的な専門用語の初出。`読み込み時
  ハンドラ`・`字句`系は独自寄りの言い換え。
- 語数は 10 未満で、依頼書・archive としては想定どおりの範囲。`src/README.md`
  の差分そのものには前例の無い語は無い（`初期化とハンドラ` は既存の
  `main-page.js` 行の写し）。
