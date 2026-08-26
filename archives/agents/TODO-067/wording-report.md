# TODO-067 wording 報告

## 対象

- `TODO.md`（差分は TODO-067 節の削除と、完了済み目次への 1 行追加のみ。
  新規の語は無い）
- `archives/todo/TODO-067. フッターの入力欄とアイコンの縦位置を揃える.md`（新規）
- `archives/agents/TODO-067/README.md`（新規）
- `archives/agents/TODO-067/verifier-report.md`（確認時点でまだ作成されて
  いなかった。verifier の担当範囲であり、他の 3 ファイルで見立てを出す）

## 候補語と前例

`git grep -cF <語> HEAD -- '*.md'` で前例を数えた。件数が少ない順。

| 語 | 出てくる箇所 | 件数 | 見立て |
| --- | --- | --- | --- |
| `justify-content` | 「`text-end` の列は `justify-content: flex-end` にする」 | 前例なし | CSS プロパティ名そのもの。造語ではない |
| `my-row-middle` | 「`.my-row-middle` を足して、付けた行の列を…」 | 前例なし | 今回の変更で新設した CSS クラス名。命名であって言い回しの造語ではない |
| `align-items` | 「`display: flex; align-items: center` にした」 | 1 | CSS プロパティ名。造語ではない |
| `my-fs-medium` | 「search の列（`my-fs-medium`、16px）」 | 2 | 既存の CSS クラス名（TODO-048 系由来）。文書での言及は少ないが命名自体は既存 |
| `align-self` | 「列は `align-self: stretch` で」 | 5 | CSS プロパティ名 |
| `孫` | 「列から見ると孫なので、列だけでなく `form` にも…」 | 6 | DOM 構造の比喩だが、他の文書でも既に使われている。専門的比喩として一般に通用する |
| `my-icon-2x` | 「filter … `my-icon-2x`（2em）」 | 6 | 既存の CSS クラス名 |
| `不揃い` | 「横位置の不揃い（列の幅と…）」 | 7 | 普通の日本語。問題なし |
| `gap` | 「`gap: 0.25em` で戻した」 | 7 | CSS プロパティ名 |
| `横位置` | 「横位置の不揃い（…）も目につくが」 | 9 | 「縦位置」と対で使う普通の語 |
| `my-icon-lg` | 「全部 `my-icon-lg`（1.25em）に揃えた」 | 9 | 既存の CSS クラス名 |
| `フッター` | 節タイトル・本文各所 | 10 | UI 用語として一般的。既出多数 |
| `computed` | 「computed 値は `-2px` だった」 | 11 | CSS/DevTools の一般用語 |
| `align-bottom` | 「編集画面（`edit.html` の `align-bottom`）」 | 12 | CSS ユーティリティクラス名（Bootstrap 由来） |
| `ユーティリティ` | 「ユーティリティの節から `.my-icon*` の後ろへ移した」 | 16 | CSS の一般的な言い回し（Bootstrap の "utility classes" の訳語として定着） |

このほか `縦位置`（46）・`align-middle`（26）・`詳細度`（30）・`分担`
（168）・`reviewer`（603）・`verifier`（1032）・`wording`（431）は、
件数が多く既に定着している語として除外した。

## 判断が要る点・見立ての補足

- `my-row-middle` は前例なしだが、これは**新設したクラス名**であって
  言い回しの造語ではない。ソースコードの命名であり、文書上の呼び名の
  問題ではないと考えるが、判断は main に委ねる
- `孫` は DOM 構造を家族関係の比喩で呼ぶ言い回し。前例が既に 6 件ある
  ため、この文脈での定着した比喩と見てよさそうだが、比喩そのものが
  一般的なプログラミング用語というより、このリポジトリ内で定着した
  言い回しである可能性はある

## 結論

前例の無い語（0 件）: `justify-content`、`my-row-middle` の 2 語。
どちらも CSS のプロパティ名・クラス名で、一般に通用する技術的な命名と
見立てている（言い回しの造語ではない）。

その他は件数の多寡はあれ、いずれも一般的な日本語表現、CSS の標準用語、
または既存のプロジェクト内クラス名であり、造語と見立てられるものは
無かった。

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-067. フッターの入力欄とアイコンの縦位置を揃える.md`
- `archives/agents/TODO-067/README.md`
- `archives/agents/TODO-067/verifier-report.md`（未作成のため対象外）
