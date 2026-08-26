# TODO-055 wording 報告

対象は `TODO.md`、`archives/todo/TODO-055. 週表示に合わせて、ヘッダと日付欄を
直す.md`、`archives/agents/TODO-055/`（`README.md`、依頼書 3 つ、報告 2 つ）。
前例の有無は `git grep -cF <語> HEAD -- '*.md'` で数えた（この 7 ファイル自体は
まだコミットされておらず HEAD に入っていないので、これで数えて問題ない）。

候補 14 語を、前例の件数が少ない順に挙げる。

## 週の帯

- `archives/todo/TODO-055....md:27` 「上部に週の帯を新設した」ほか、
  `request-verifier.md:7,15`、`verifier-report.md:14` にも出てくる
- `git grep` 件数: 前例なし
- 見立て: 今回新しく置いた UI 部品の名前で、依頼書が気にしていたとおりの
  箇所。TODO-049 以降のこれまでの報告では、この帯に近いものを指す既存の
  呼び方が見当たらなかった（`帯` 自体は他の意味で 3 件ヒットする程度）。
  一般には通じない呼び方なので、このリポジトリだけの言い換えに見える。
  ただし「週の帯」は素直な複合語で、今後もこの意味で使い続けるなら
  問題は無さそう。**言い換えるべきかは判断できない**

## 週の差

- `archives/todo/TODO-055....md:32,38,77,81,94`、`request-verifier.md:8`、
  `verifier-report.md:14`
- `git grep` 件数: 前例なし
- 見立て: 既存の「日数差」（前例 1 件）と対になる新語。「週として何週
  離れているか」を指す語として自然で、混同もしにくい。**このままで
  よさそう**

## 出し分け

- `archives/todo/TODO-055....md:71` 「出し分けはテンプレートの `{% set %}`
  で属性の中身を組み立てている」、`request-reviewer.md:22`
- `git grep` 件数: 前例なし
- 見立て: 一般の IT 用語としてよく使われる言い方（条件によって表示内容を
  変える、の意味）。このリポジトリでは初出だが、一般に通用する語に見える

## 干渉

- `reviewer-report.md:21` 「ソフトキーボード追従とは干渉しない」
- `git grep` 件数: 前例なし
- 見立て: 一般語。初出だが問題は無さそう

## ちぐはぐ

- `archives/todo/TODO-055....md:16` 「画面に残っていた 2 つのちぐはぐを
  直す」
- `git grep` 件数: 1（`archives/agents/TODO-028/reviewer-report.md`）
- 見立て: 前例があり、一般語でもある。問題なし

## 日数差

- `archives/todo/TODO-055....md:19,75,77,81`、`request-verifier.md:14`
- `git grep` 件数: 1（`TODO.md:64`、TODO-055 を立てたときの記述）
- 見立て: 今回の文書内で定着した語で、前例も TODO-055 自身の立てた
  項目にある。問題なし

## 食い違わない

- `request-reviewer.md:16` 「ソフトキーボードの `followKeyboard()` と
  食い違わないか」
- `git grep` 件数: 1
- 見立て: 一般語。問題なし

## 境目

- `request-reviewer.md:13` 「月曜・日曜の境目で誤らないか」
- `git grep` 件数: 2
- 見立て: 一般語。問題なし

## 潰さない

- `archives/todo/TODO-055....md:69` 「その操作は残っているので、そちらを
  潰さない」
- `git grep` 件数: 2
- 見立て: 「（機能・操作を）無くす」の意味の口語的表現。一般にも通じる
  言い回しに見える

## 踏襲

- `reviewer-report.md:25` 「既存の『＋』ボタンと同じパターンを踏襲して
  おり」
- `git grep` 件数: 4
- 見立て: 一般語。問題なし

## 通常モード

- `archives/todo/TODO-055....md:49,64,97`
- `git grep` 件数: 5
- 見立て: 「検索モード」（前例 59 件）と対になる語として自然。問題なし

## 日付の欄

- `archives/todo/TODO-055....md:21,62,104`、`README.md:7`、
  `request-reviewer.md:20`、`request-verifier.md:11,33,34`
- `git grep` 件数: 6
- 見立て: 依頼書が気にしていた語のひとつだが、前例が複数あり
  （TODO-049 以降ですでに使われている呼び方と見える）、ずれは無さそう

## 先読み

- `TODO.md:126` 「前後の週を先読みして DOM に持つ」（TODO-057）
- `git grep` 件数: 7
- 見立て: 一般語（プログラミングでよく使う語）。問題なし

## 見送った

- `archives/todo/TODO-055....md:79,111`、`README.md:16`
- `git grep` 件数: 8
- 見立て: 一般語。問題なし

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-055. 週表示に合わせて、ヘッダと日付欄を直す.md`
- `archives/agents/TODO-055/README.md`
- `archives/agents/TODO-055/request-reviewer.md`
- `archives/agents/TODO-055/request-verifier.md`
- `archives/agents/TODO-055/reviewer-report.md`
- `archives/agents/TODO-055/verifier-report.md`

（`request-wording.md` は依頼書本体なので対象読み込みはしたが、語の
抽出対象には含めていない。）

## まとめ

前例なしの語数: **4 語**（週の帯・週の差・出し分け・干渉）。
このうち「週の帯」「週の差」は、依頼書が気にしていた新しい画面の部品の
呼び方に当たる。言い換えるかどうかは main の判断。
