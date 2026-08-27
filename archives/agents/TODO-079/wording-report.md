# TODO-079 wording 報告

対象は依頼にあった 6 ファイル。

- `archives/todo/TODO-079. 表示の条件をまとめて load_sched の引数を減らす.md`
- `archives/agents/TODO-079/README.md`
- `archives/agents/TODO-079/implementer-task.md`
- `archives/agents/TODO-079/implementer-report.md`
- `archives/agents/TODO-079/verifier-task.md`
- `archives/agents/TODO-079/verifier-report.md`
- `TODO.md`（`git diff TODO.md` の差分のみ）

前例は `git grep -cF <語> HEAD -- '*.md'` で数えた（基準はコミット前の
`HEAD`）。

## 前例の無い語（件数の少ない順）

### IDENTICAL（0 件）

- `verifier-report.md`「○ IDENTICAL」（8 パターン全部）、
  `README.md`「HTML に差は無かった」の直前の要約にも同じ言い回し
- `git grep -cF IDENTICAL HEAD -- '*.md'` → 前例なし
- 見立て: `diff` の結果を英語のまま書く言い回し。過去の verifier 報告
  （TODO-018 など）は「差は無い」「一致した」のように日本語で書いており、
  この書き方はこの文書が初出。一般には通用するが、このリポジトリでの
  言い換えとしては新しい

### スパイ／spy（0 件）

- `implementer-report.md`「`mk_todo_by_date()` を spy で差し替え」
- `git grep -cF spy HEAD -- '*.md'` および `スパイ` → いずれも前例なし
- 見立て: テストの技法としての「スパイ」（呼び出し回数を数えるための
  差し替え）は一般に通用する用語だが、このリポジトリでは初出。
  「差し替え」自体は既存の言い回しなので、「spy」という単語だけが新しい

### 組み替える（0 件）

- `README.md`「引数の受け渡しを組み替えるので、実装は分けた」
- `git grep -cF 組み替える HEAD -- '*.md'` → 前例なし（「組み立てる」
  「書き換える」には前例があるが、「組み替える」は無い）
- 見立て: 一般的な日本語で、造語には見えない。単に今まで使う場面が
  無かっただけの可能性が高い

### 同名のローカル変数／ローカル変数（0 件）

- `archives/todo/TODO-079. ….md`「冒頭で `cond` の中身を同名の
  ローカル変数へ展開している」、`implementer-report.md`「同名の
  ローカル変数へ展開し」
- `git grep -cF ローカル変数 HEAD -- '*.md'` → 前例なし
- 見立て: 一般的なプログラミング用語で、造語ではない。判断は main へ

### SchedLoadCond（0 件）

- `archives/todo/TODO-079. ….md`・`README.md`・`implementer-task.md`・
  `implementer-report.md` に出てくる、新しく作った dataclass の名前
- `git grep -cF SchedLoadCond HEAD -- '*.md'` → 前例なし（コードの
  識別子なので当然ではあるが、依頼にあった「命名は釣り合うものに」の
  結果できた名前なので一応挙げる）
- 見立て: 造語ではなく実装上の固有名詞。これ自体の是非は実装の確認の
  範囲で、wording が判断することではない

## 参考（前例はあるが目についたもの）

- 「釣り合うもの」「全件走査」は `git grep` で 1 件だけ一致するが、
  その 1 件はいずれも `archives/agents/TODO-079/implementer-task.md`
  自身（今回の対象ファイルのうち、既に別コミットで `HEAD` に入って
  いたもの）。「全件走査」はさらに `TODO.md`（今回削除される旧
  TODO-079 の節）と `docs/design-review.md` にも前例があるため除外した。
  「釣り合うもの」は他に一致が無いので、造語ではなさそうだが目に留まった

## 読んだファイル

- `archives/todo/TODO-079. 表示の条件をまとめて load_sched の引数を減らす.md`
- `archives/agents/TODO-079/README.md`
- `archives/agents/TODO-079/implementer-task.md`
- `archives/agents/TODO-079/implementer-report.md`
- `archives/agents/TODO-079/verifier-task.md`
- `archives/agents/TODO-079/verifier-report.md`
- `TODO.md`（差分のみ）

## 前例の無い語数

5 語（IDENTICAL、スパイ／spy、組み替える、ローカル変数、SchedLoadCond）
