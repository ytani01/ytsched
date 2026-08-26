# TODO-066 wording 報告

対象ファイル（コミットに入る `.md`、および TODO-066 の diff に含まれる
コード中のコメント）:

- `TODO.md`（差分。TODO-066 の節を削除して archives へ移しただけで、
  新規の文言は無し）
- `archives/todo/TODO-066. ヘッダーの期間表示をやめて、週の差を針と
  一緒に動かす.md`
- `archives/agents/TODO-066/README.md`
- `archives/agents/TODO-066/verifier-report.md`（この時点でまだ存在せず、
  対象外）
- `src/ytsched/webroot/templates/main.html` /
  `src/ytsched/webroot/static/css/my.css` /
  `src/ytsched/webroot/static/js/my.js` の変更部分（コメント）

`git grep -cF <語> HEAD -- '*.md'` は「HEAD 時点（＝この文書が入る前）の
`.md` 全体」を対象に数えた。

## 前例なしの語（0 件、件数が少ない順）

- **勘違い**
  - 箇所: `archives/todo/TODO-066. ....md` の見出し「直した勘違いの
    コメント」。「`placeGageWithoutTransition()` の『`offsetHeight` は
    使えない』という説明は…前提のもの」を指す
  - `git grep` 件数: 前例なし
  - 見立て: ごく普通の日本語で、造語には見えない。この文脈以外でも
    広く通じる語

- **週数**
  - 箇所: `my.js` の `setGagePosition()` のコメント「7 で割って週数に
    する」（archive 本文にも同じ言い回しあり）
  - `git grep` 件数: 前例なし
  - 見立て: 「週の数」の普通の熟語で、一般に通用する語。このリポジトリ
    だけの言い換えではない

- **位置を取り直す**（フレーズ）
  - 箇所: `my.css` の `.my-gage-r-label` のコメント「はみ出す文字は
    中で位置を取り直す」
  - `git grep` 件数: 前例なし（「取り直す」単独でも 0 件）
  - 見立て: 「取り直す」自体は一般語で、造語ではないと思う。ただし
    この文脈だと意味がやや取りにくい（「入れ物の中で改めて基準を
    決める」くらいの意図と読めるが、断定はできない）

## 前例はあるが、初出に近い語（参考。挙げるかは main の判断）

- **入れ物**（針とラベルの `<div>` を指す）: 前例 1 件
  （`TODO-061` の「スクロールの入れ物に…」）。一般語で問題なさそう
- **踏んだ**（過去にバグへ遭遇した、の意味の言い回し）: 前例 3 件
  （`TODO-023` / `TODO-035` 系の報告で既に使われている）。定着した
  言い回しと見てよさそう
- **帯の高さ**: 前例 2 件（`TODO-055`）。定着している

これらは前例が複数あるので「前例なしの語」には含めない。

## 判断できないもの

- 上記「位置を取り直す」は、前例が無く、意味もやや解釈の余地があるため、
  一般語と造語のどちらとも決めきれない。main の判断を仰ぎたい

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-066. ヘッダーの期間表示をやめて、週の差を針と
  一緒に動かす.md`
- `archives/agents/TODO-066/README.md`
- `src/ytsched/webroot/templates/main.html`（該当差分）
- `src/ytsched/webroot/static/css/my.css`（該当差分）
- `src/ytsched/webroot/static/js/my.js`（該当差分）

`archives/agents/TODO-066/verifier-report.md` はこの時点で未作成のため
読んでいない。

## まとめ

前例の無い語: **3 語**（勘違い、週数、位置を取り直す）。
いずれも一般的な日本語に見え、TODO-021 の「足場」のような造語には
見えなかった。
