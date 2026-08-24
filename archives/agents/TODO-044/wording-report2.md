# TODO-044 wording 報告（着手後の分）

対象は依頼書どおり: `TODO.md` の差分、`CLAUDE.md` の差分、
`archives/todo/TODO-044. トークン消費の測り方と、担当の走らせ方を見直す.md`、
`archives/agents/TODO-044/` の全ファイル（`README.md`・`*-request.md`・
`*-report.md`）、`.claude/agents/verifier.md`・`implementer.md` の差分。

前例の有無はすべて `git grep -cF <語> HEAD -- '*.md'` で確かめた
（HEAD は今回の変更を含まない）。件数の少ない順に並べる。

## 前例なし（0 件）

- **最大値集計**
  - 箇所: `implementer-report.md:12`「`collect()` を最大値集計に直した」、
    `reviewer-request.md:13`、`reviewer-report.md:12`
  - 見立て: 「最大値」＋「集計」の組み合わせで、意味は読んで分かる。
    一般に通用しそうな技術的な言い回し

- **当たりを付ける**
  - 箇所: `.claude/agents/verifier.md`・`implementer.md` の差分
    「`grep` で当たりを付けてから `sed -n` のように範囲を切る」
  - 見立て: 一般的な日本語の慣用句（「見当をつける」の類）。造語ではなさそう

- **手計算**
  - 箇所: `verifier-request.md:27`、`verifier-report.md:22`、
    `reviewer-report.md:35`、`archives/todo/TODO-044…md:81`
  - 見立て: ごく普通の語。問題なさそう

- **挿入順**
  - 箇所: `reviewer-report.md:72,75,76`「`price_for()` の前方一致は、
    キーの挿入順に依存する設計」
  - 見立て: 辞書・リストの実装でよく使うプログラミング用語。一般に通用しそう

- **ゼロ割**
  - 箇所: `reviewer-report.md:50`「ゼロ割で落ちることは無い」
  - 見立て: ゼロ除算を指す一般的なプログラミング用語

- **割合の合計**
  - 箇所: `verifier-request.md:22`、`verifier-report.md:18`、
    `archives/todo/TODO-044…md:79`
  - 見立て: 普通の日本語の組み合わせ。問題なさそう

- **見込みとの差**
  - 箇所: `implementer-report.md:59`、
    `archives/todo/TODO-044…md:67`（節の見出し）
  - 見立て: 言葉自体は自然だが、**節見出しとして新設**している点は
    判断が要るかもしれない（`CLAUDE.md` のテンプレートには「見込み」
    「実施」の欄はあるが、この見出しは無い）

- **読ませる量**
  - 箇所: `archives/todo/TODO-044…md:25`「減るのは 1 担当あたりの
    リクエスト数と、読ませる量を絞ったとき」
  - 見立て: 「サブエージェントに読ませる分量」の意味で使っている。
    このリポジトリ固有の言い回しに見えなくもない。判断できない

- **料金基準化**
  - 箇所: `reviewer-report.md:47`（小見出し）「`fmt_shares()` /
    `sum_by()` の料金基準化」
  - 見立て: 「〜基準化」という複合の作り方は、一般にはあまり見ない。
    リポジトリ固有の言い換えに見える

- **スクリプトの内部値**
  - 箇所: `verifier-report.md:27`「→ スクリプトの内部値 `0.2319` と一致」
  - 見立て: 「プログラムが計算した実際の値」の意味で使っている。
    意味は通るが、一般的な定訳ではなさそう。判断できない

- **重複した行**
  - 箇所: `reviewer-report.md:21`
  - 見立て: 普通の日本語。問題なさそう

- **確かめ方の目安**
  - 箇所: `implementer-request.md:22`
  - 見立て: 普通の日本語。問題なさそう

## 前例が少ない語（1〜5 件）

- **誤差**（1 件） — `archives/todo/TODO-044…md:71`。一般語
- **途中経過**（3 件） — `implementer-request.md:15`、
  `implementer-report.md:14`、`archives/todo/TODO-044…md:28`。一般語。
  依頼書の「特に見てほしい語」に挙がっていたが、一般的な言い回しに見える
- **導入価格**（3 件） — `implementer-request.md:37`、
  `implementer-report.md:36`、`CLAUDE.md:106`、
  `archives/todo/TODO-044…md:44`。**この 3 件はすべて
  `wording-report.md`（項目を立てたときの分）以降のもの**で、
  最初の報告で一度「前例なし」として指摘済みの語がそのまま定着した形。
  今回のコミットで初めて `.md` に複数回登場するが、指摘そのものは
  既に済んでいる

## 見た範囲で他に気になった語（前例あり、参考）

- **概算料金**（8 件）・**料金の割合**（5 件） — いずれも
  `wording-report.md` で既に指摘済みの語で、このコミットでも使われて
  いる（新規の指摘ではない）
- **前方一致**（8 件） — `TODO-026` に前例があり、造語ではない

## 読んだファイル

- `TODO.md`（差分）
- `CLAUDE.md`（差分）
- `archives/todo/TODO-044. トークン消費の測り方と、担当の走らせ方を見直す.md`
- `archives/agents/TODO-044/README.md`
- `archives/agents/TODO-044/implementer-request.md`
- `archives/agents/TODO-044/implementer-report.md`
- `archives/agents/TODO-044/verifier-request.md`
- `archives/agents/TODO-044/verifier-report.md`
- `archives/agents/TODO-044/reviewer-request.md`
- `archives/agents/TODO-044/reviewer-report.md`
- `archives/agents/TODO-044/wording-request2.md`
- `.claude/agents/verifier.md`（差分）
- `.claude/agents/implementer.md`（差分）

前例の無い語（0 件）は 12 語。1〜5 件の少ないものまで含めると 15 語。
