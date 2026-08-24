# TODO-040 wording 報告

読んだファイル 8 つ（依頼書自身を除く）。

- `README.md`
- `TODO.md`
- `archives/todo/TODO-040. bootstrap, fontawesomeのバージョンアップ.md`
- `archives/agents/TODO-040/README.md`
- `archives/agents/TODO-040/implementer-request.md`
- `archives/agents/TODO-040/implementer-report.md`
- `archives/agents/TODO-040/verifier-request.md`
- `archives/agents/TODO-040/verifier-report.md`

基準は `HEAD`（`b9579b5`）。`TODO.md` は `b9579b5` の時点で TODO-040 の
節（見込みの表と、着手前に決めたこと）を含んでいるため、その節で初めて
出てくる語は `HEAD` を基準にすると「前例あり」に見えてしまう。疑わしい
語は `b9579b5^` でも確認した。

## 前例の無い語（8 語、前例の件数が少ない順）

### ハマった（点）

- `archives/agents/TODO-040/verifier-report.md:34`
  「**ハマった点（main への申し送り）:** 複数の chromium プロセスを
  `--user-data-dir` を…」
- `git grep -cF ハマった HEAD -- '*.md'` → **前例なし**
- 見立て: 話し言葉寄りのくだけた表現。「つまずいた点」（このリポジトリ
  では `archives/agents/TODO-026/verifier-report.md` に前例 1 件あり）
  と同じ場面で使われており、言い換えの余地がありそう

### 差分画像

- `archives/agents/TODO-040/verifier-report.md:77`
  「`compare 旧.png 新.png diff.png` で作った差分画像を目視した」
- `git grep -cF 差分画像 HEAD -- '*.md'` → **前例なし**
- 見立て: 一般に通用しそうな複合語（diff 画像）で、造語というより
  ふつうの説明語に見える

### 読み込み中のしるし

- `archives/todo/TODO-040. bootstrap, fontawesomeのバージョンアップ.md:47,161`、
  `archives/agents/TODO-040/verifier-request.md:79`、
  `archives/agents/TODO-040/verifier-report.md:86`
  （`fa-spin` の回転アイコンを指す言い回し）
- `git grep -cF しるし HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: `b9579b5`（TODO-040 の見込みを立てたコミット）で main が
  作った言い回しで、今回のコミットで報告ファイル側にも広がっている。
  一般には「スピナー」「読み込みアイコン」と呼ぶことが多く、この
  リポジトリだけの言い換えに見える

### 絵柄

- `archives/todo/TODO-040. ….md:49,62,157,166`、
  `archives/agents/TODO-040/README.md:27`、
  `archives/agents/TODO-040/verifier-request.md:74`、
  `archives/agents/TODO-040/verifier-report.md:80,84`
  （Font Awesome のアイコンの見た目を指す）
- `git grep -cF 絵柄 HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: 一般語ではあるが、アイコンのデザインを指す語としては
  「デザイン」「アイコンの見た目」のほうが普通かもしれない。
  `b9579b5` で作られ、今回のコミットで報告ファイルへ広がった語

### 回転位置

- `archives/todo/TODO-040. ….md:47,161`、
  `archives/agents/TODO-040/verifier-request.md:79`、
  `archives/agents/TODO-040/verifier-report.md:86`
- `git grep -cF 回転位置 HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: 「回転する角度」の意味で使っており、ふつうの複合語に見える。
  判断できない

### 読み込み中

- 上の「読み込み中のしるし」と同じ 4 箇所
- `git grep -cF 読み込み中 HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: ごく普通の日本語。造語ではなさそう

### 解決先

- `archives/agents/TODO-040/implementer-request.md:101,109`
  「`-apple-system, …` と解決先が違い、行の高さが変わる」
  （CSS の `font-family` フォールバックが実際にどのフォントに
  解決されるか、の意味）
- `git grep -cF 解決先 HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: 一般的な IT 用語（名前解決の「解決」＋「先」）で、通用しそう。
  ただし今回のような「フォントの当たり先」の意味で使うのはやや独特

### 伸びる

- `archives/agents/TODO-040/implementer-request.md:110`、
  `archives/todo/TODO-040. ….md:38`
  「一覧が 176px 伸びる」「ページ全体が…7,119px に伸びる」
- `git grep -cF 伸びる HEAD -- '*.md'` → 1 件（`TODO.md` 自身）。
  `b9579b5^` では **前例なし**
- 見立て: ごく普通の日本語。造語ではなさそう

## 補足

`崩れ` `ズレ` `内訳` `申し送り` `眼目` `切り分け` `桁` `揺らぎ` `塊` `残骸`
`効き目` `突き合わせ` `照合` `食い違って` なども今回のファイルに出てくるが、
いずれも `HEAD`（`b9579b5`）の時点で他の TODO の文書に前例があったため、
候補から外した。
