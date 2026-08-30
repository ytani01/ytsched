# TODO-125. スケジュールを Obsidian 用の Markdown へ書き出す（対応しない）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | main のみ |

## きっかけ

TODO-118 で「データ形式そのものを Markdown へ移す」案を評価し、移すのは
やめると決めた。その代わりとして、JSON Lines を元のデータのまま残し、
そこから Obsidian 用の Markdown を一方向に書き出す案を立てた
（`ytsched export`、1 日 1 ファイル、更新があった日だけ書き直す、
期間をまとめて 1 ファイルへ出すモード）。狙いは、Obsidian でスケジュールを
参照することと、Obsidian のメモとスケジュールをまとめて AI に読ませること。

## やらないと決めた理由

**Obsidian で予定を参照する使い方自体を、今は考えないことにした。**

書き出す動機がそのまま無くなったので、`ytsched export` も、1 日 1 ファイルの
形式も、差分書き出しも要らない。項目に残っていた「書き出し先に、書き出した
もの以外のファイルがあったときの扱い」も、決める必要が無くなった。

データ形式は JSON Lines のまま（`docs/data-format.md`）。TODO-118 で
「Markdown へ移さない」と決めた判断は、こちらでも変えていない。

## テスト

コードを変えていないので無し。
