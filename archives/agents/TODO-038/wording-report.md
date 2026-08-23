# TODO-038 wording 報告

依頼書: `archives/agents/TODO-038/wording-request.md`

## 読んだファイル

- `TODO.md`（差分）
- `archives/todo/TODO-038. HTML・CSS のリファクタリング.md`
- `archives/agents/TODO-038/README.md`
- `archives/agents/TODO-038/implementer-request-1.md` / `implementer-report-1.md`
- `archives/agents/TODO-038/implementer-request-2.md` / `implementer-report-2.md`
- `archives/agents/TODO-038/implementer-request-3.md`（報告は無し）
- `archives/agents/TODO-038/main-note-step3.md`
- `archives/agents/TODO-038/reviewer-request.md` / `reviewer-report.md`
- `archives/agents/TODO-038/verifier-request.md` / `verifier-report.md`
- `archives/agents/TODO-038/wording-request.md`

`git grep` は `HEAD`（コミット `cca8269`）を基準にした。

## 前例の無い語（件数の少ない順。今回は全部 0 件）

### 段目

- 出てくる箇所: `implementer-report-1.md:1`「報告（1 段目・片付け）」、
  `implementer-request-2.md` `3.md`、`reviewer-request.md:11-17`
  「1 段目の依頼」「2 段目の依頼」「3 段目の依頼」、`README.md`、
  `main-note-step3.md` の題、`archives/todo/TODO-038…md` の見出し
  「### 1 段目 ── 片付け」など、全体で多数
- `git grep -cF 段目 HEAD -- '*.md'`: **前例なし**
- 見立て: 作業を 3 段階に分けたことを指す言い回し。「フェーズ」「段階」
  という一般語の代わりに独自の数え方（1 段目・2 段目・3 段目）を
  作った形。今回のコミットの中だけで一貫して使われており、意味も
  一目で通るので造語というより命名だが、**前例が無いことは事実**。
  「段階」「フェーズ」に言い換えられるかは main の判断

### 覚書

- 出てくる箇所: `main-note-step3.md:1`「TODO-038 3 段目についての覚書
  （main）」、`README.md:12`「**無し**（main の覚書）」、
  `reviewer-request.md:16` `verifier-request.md:17`
  「[main の覚書](main-note-step3.md)」、`wording-request.md:13`
- `git grep -cF 覚書 HEAD -- '*.md'`: **前例なし**
- 見立て: 一般語で、意味も明確。「メモ」でも通じるが、和語として
  自然なので置き換える必要は薄いと思う（判断は main）

### 眼目

- 出てくる箇所: `implementer-request-2.md:47`「これを減らすのがこの
  項目の眼目だが」、`implementer-report-2.md:132`「入れ子をやめるのが
  この項目の眼目なので」、`archives/todo/TODO-038…md:94` にも同じ文が
  そのまま転記されている
- `git grep -cF 眼目 HEAD -- '*.md'`: **前例なし**
- 見立て: 一般的な日本語だが硬め。「ねらい」「主眼」でも通じる。
  このリポジトリでは初出

### 揺らぎ

- 出てくる箇所: `verifier-report.md:78`「chromium のレンダリング
  そのものの揺らぎ（テスト環境のノイズ）」、同 89「この揺らぎは
  旧版・新版どちらの」
- `git grep -cF 揺らぎ HEAD -- '*.md'`: **前例なし**
- 見立て: 依頼書が名指ししていた語。スクリーンショット比較で毎回
  結果が微妙に変わる現象を指す一般語（「ばらつき」でも同義）。
  技術文書としては普通の使い方だが、このリポジトリでは初出

### 非決定性

- 出てくる箇所: `verifier-report.md:85`「アンチエイリアス/
  ラスタライズの非決定性で、内容の違いではない」
- `git grep -cF 非決定性 HEAD -- '*.md'`: **前例なし**
- 見立て: 一般に通用する専門用語（non-determinism）だが、このリポジトリ
  では初出。「揺らぎ」と同じ現象を指しており、1 つの報告の中で
  2 通りの言い方（揺らぎ／非決定性）が併存している

### 裏が取れた

- 出てくる箇所: `verifier-report.md:57`「2 点は、これで両方とも画素
  単位で**裏が取れた**」
- `git grep -cF 裏が取れ HEAD -- '*.md'`: **前例なし**
- 見立て: 慣用句（「裏付けが取れた」の口語形）。一般語だが、
  「確認できた」「裏付けが取れた」など、このリポジトリの他の報告での
  言い方と表記が揺れている可能性がある

### 辻褄が合っている

- 出てくる箇所: `reviewer-report.md:65`「という説明で**辻褄が合って
  いる**」
- `git grep -cF 辻褄が合 HEAD -- '*.md'`: **前例なし**
- 見立て: 一般的な慣用句。「整合している」「矛盾しない」でも通じる。
  意味は明確

### たたみ方

- 出てくる箇所: `implementer-report-2.md:101`「Tornado の**空白の
  たたみ方**が変わって」、`reviewer-report.md:55`「Tornado の**空白の
  たたみ方**が変わり」
- `git grep -cF たたみ方 HEAD -- '*.md'`: **前例なし**
- 見立て: Tornado テンプレートが連続する空白・改行をまとめる挙動を
  指す独自の言い回し。一般的な IT 用語ではなく、この文脈のための
  言い換えに見える。「空白の畳み込み」「空白の圧縮」などとも言えそうで、
  造語の可能性が比較的高い

### 所感

- 出てくる箇所: `reviewer-report.md:71`「## 確信度の低い**所感**（参考）」
- `git grep -cF 所感 HEAD -- '*.md'`: **前例なし**
- 見立て: 一般語。`reviewer.md`（担当定義）の「確信度が低いと明記する」
  という指示に沿って見出しに使った語で、造語というより一般語の範囲

### 怪しいところ

- 出てくる箇所: `verifier-request.md:50`「### 3. 3 段目で特に**怪しい
  ところ**」
- `git grep -cF 怪しい HEAD -- '*.md'`: **前例なし**
- 見立て: 一般語（口語寄り）。「疑わしい箇所」でも通じる。意味は明確

### 字下げ

- 出てくる箇所: `reviewer-report.md:73`「`<script>` 内が全体的に
  **1 段字下げ**が浅くなっている」、`implementer-report-2.md:188`
  「HEAD から 1 桁ぶん**字下げ**が変わって」、
  `archives/todo/TODO-038…md:152`「1 段目で**字下げ**が 1 段ぶん
  浅くなっている」
- `git grep -cF 字下げ HEAD -- '*.md'`: **前例なし**
- 見立て: 「インデント」の和語。一般的で意味は明確。このリポジトリでは
  カタカナ語（「インターフェース」等）を使う方針（`CLAUDE.md`）とは
  逆に和訳しており、揃っていないと見ることもできる（判断は main）

## 見立てをまとめると

- **明確に造語寄りと感じたもの**: 「段目」（数え方そのものを作っている）、
  「たたみ方」（Tornado の空白の扱いを指す言い換え）
- **一般語・慣用句で意味が明確なもの**: 覚書、眼目、揺らぎ、非決定性、
  裏が取れた、辻褄が合っている、所感、怪しいところ、字下げ

## 読んだファイル一覧・前例なしの語数

上の「読んだファイル」節のとおり。**前例の無い語は 11 語。**
