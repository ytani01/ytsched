# wording 報告（docs/design-review.md の削除・TODO.md への移し込み）

## 対象

`git diff --cached` で `TODO.md` の**追加行のみ**を対象にした
（`docs/design-review.md` は削除〈`D`〉で、追加行を持たないため）。

- `TODO.md`（追加行）

## 前提

このコミットでは `docs/design-review.md` を削除し、その中身の大半を
`TODO.md` の各項目へ引き写している。そのため、`TODO.md` の追加行にある
語の多くは、削除前の `docs/design-review.md`（`HEAD` にまだ存在する）に
**同じ語がすでにある**。前例を数える基準は「このコミットが入る前
（`HEAD`）」なので、`docs/design-review.md` 側の記述も前例として数えて
いる。**ただし、このコミットが確定すると `docs/design-review.md` は
無くなるため、次にこのコミットのあとで前例を数えるときは、その分が
消えている点に注意。**（例えば「検索側の持ち物にする」「実質もう 1 つの
画面」は今回 `docs/design-review.md` 側にも前例があるため件数に含めたが、
このコミットが入ったあとは `TODO.md` 自身の 1 件だけが残る。）

## 前例の無い語

### 通し番号

- 出てくる箇所: `TODO.md` 冒頭の追記
  「A〜P の記号は、そのレビューでの通し番号。」
- `git grep -cF 通し番号 HEAD -- '*.md'` → 前例なし（0 件）
- 見立て: 一般的な日本語（「連番」と同義）で、このリポジトリ独自の
  言い換えには見えない。おそらく問題ない

## 前例はあるが、前例の入れ物ごと消えるもの（参考）

以下は今回 0 件ではなかったが、前例の大半（または全部）が
`docs/design-review.md`（このコミットで削除される）にあり、
`TODO.md` 単独では前例が薄い。造語ではないが、念のため書いておく。

- **実質もう 1 つの画面** — `git grep -cF` は 2 件だが、うち 1 件は
  `docs/design-review.md`。残る 1 件は `TODO.md` の**削除される側**の
  文（今回の diff で書き換わる元の文）自体で、`TODO.md` に前からあった
  言い回し。造語ではない
- **検索側の持ち物にする** — 6 件のうち、`docs/design-review.md` 以外は
  `TODO.md` 本体と `archives/agents/TODO-087/wording-report.md`
  （TODO-087 を立てたときの wording 報告）。TODO-087 の wording 報告で
  一度「前例なし」として挙げられ、そのまま使われ続けている語

## 見送った語（判断できないもの）

無し。上記以外の語（「型チェッカ」「黙って壊れる」「通常モード」
「名前空間」「宣言なし」「呼ぶ側」「呼ばれる側」「実際の依存」
「dataclass」など）はいずれも `docs/design-review.md` か、それ以外の
既存 `.md` に前例があった。

## 読んだファイル

- `TODO.md`（追加行のみ）
- 前例を数えるために `docs/design-review.md`（`HEAD` 時点）、
  `archives/agents/TODO-087/wording-report.md` 等を参照

## 前例の無い語数

1 語（「通し番号」）
