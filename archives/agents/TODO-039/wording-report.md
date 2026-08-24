# TODO-039 wording 報告

対象 10 ファイル（`git diff --cached --name-only -z -- '*.md'`）を読んだ。
前例の有無は `HEAD`（`e146a11`）基準。

## 前例の無い語（前例の件数が少ない順）

### 追従（0 件）

- 出てくる箇所
  - `archives/todo/TODO-039. スマホ用の設定を追加.md:35`
    「キーボードの上にボタンを**追従させる**」に決めた
  - 同 `:113` 見出し「### ソフトキーボードの**追従**（implementer）」
  - `archives/agents/TODO-039/README.md:12,14`
    「キーボード**追従**の JavaScript」
  - `archives/agents/TODO-039/implementer-report.md:50`
    「`visualViewport` を使ったキーボード**追従**は」
- `git grep -cF 追従 HEAD -- '*.md'` → 前例なし
- 見立て: 一般的な IT 用語としては通用する（「キーボード追従」で検索すると
  他のアプリでも使われる言い回い）。ただし `CLAUDE.md` に既にある
  「追随」（TODO-033 のタイトル「URL_PREFIX の改名に**追随**できていない
  箇所を直す」、前例 30 件）と字面が近く紛らわしい。**別の語として
  使い分けているのか、同じ意味で書き分けてしまったのか**は本人しか
  分からない。今回の意味（バーがキーボードの動きに合わせて位置を変える）
  では「追従」の方が動きのニュアンスに合ってはいる

### 引き出しメニュー（0 件）

- 出てくる箇所: `archives/agents/TODO-039/implementer-request.md:159`
  「`main.html` の `.my-bar-content`（**引き出しメニュー**）には付けない」
- `git grep -cF 引き出しメニュー HEAD -- '*.md'` → 前例なし
- 見立て: 一般に通用する UI 用語（drawer menu の訳語として普通に使われる）。
  このリポジトリでは初出だが、`.my-bar-content` という実装名への
  説明的な呼び名で、造語というより注釈に近い

### クランプ（0 件）

- 出てくる箇所: `archives/agents/TODO-039/reviewer-report.md:20`
  「`Math.max(0, …)` で負の値を切り捨てている」の直後、
  「この**クランプ**で見た目には影響しない」
- `git grep -cF クランプ HEAD -- '*.md'` → 前例なし
- 見立て: プログラミングでは一般的な用語（`clamp` のカタカナ）。
  他の担当が読んで通じるかは、この言葉だけ切り出すと判断できない
  （直前に `Math.max(0, …)` という具体的なコードが添えてあるので、
  文脈からは読み取れる）

### 同期読み込み（0 件）

- 出てくる箇所: `archives/agents/TODO-039/reviewer-report.md:21`
  「`my.js` は `<head>` で `defer` 無しに**同期読み込み**され」
- `git grep -cF 同期読み込み HEAD -- '*.md'` → 前例なし
- 見立て: 一般的な Web 開発用語（synchronous loading の訳語）で、
  このリポジトリで初出なだけと思われる。造語というより専門用語

## 前例はあるが、書き手が意識していないと思われる語（参考）

- **申し送り**（`verifier-request.md`「申し送り（TODO-040 で verifier が
  つまずいた点）」）は前例 6 件、**つまずいた**も前例 6 件。いずれも
  一般語で問題無いと見立てる
- **確信度**（reviewer 報告で多用）は前例 50 件、**同梱**は前例 71 件。
  定着した語なので問題無い

## 判断できないもの

- 「追従」を「追随」と使い分けている意図が本文から読み取れない
  （前述のとおり）。同じ意味で 2 つの語を使ってしまっているなら
  表記のゆれとして直す価値があるかもしれないが、これは main の判断

## 読んだファイル

- README.md
- TODO.md
- archives/agents/TODO-039/README.md
- archives/agents/TODO-039/implementer-report.md
- archives/agents/TODO-039/implementer-request.md
- archives/agents/TODO-039/reviewer-report.md
- archives/agents/TODO-039/reviewer-request.md
- archives/agents/TODO-039/verifier-report.md
- archives/agents/TODO-039/verifier-request.md
- archives/todo/TODO-039. スマホ用の設定を追加.md

## 前例の無い語の数

**4 語**（追従・引き出しメニュー・クランプ・同期読み込み）
