# TODO-201. エージェント設定ファイルの古い記述を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main（編集）+ verifier（Sonnet 5 / medium） |
| 実施 | Sonnet 5 / effort medium | main（編集）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Sonnet 5 | medium | 4,822 | 81,975 | 80% |
| verifier | Sonnet 5 | medium | 1,125 | 29,316 | 20% |
| 合計 |  |  | 5,947 | 111,291 | 概算 $0.6 |

## きっかけ

`/claude-api prompt-audit`（2026-09-27）で、エージェント設定ファイルと
`.agents/skills/ytsched-workflow/SKILL.md` に古い記述が 4 件見つかった。
実際の運用（`archives/todo/` へ 1 項目 1 ファイルで移す、`rg` を使う、
Bash ツールの `ls` は空を返す）と食い違っていた。

## やったこと

- `.agents/skills/ytsched-workflow/SKILL.md` の完了手順を、
  「目次（`## 完了済み`）へ移動」から「`TODO.md` から完了項目の節を削除する
  （一覧は `archives/index.md` を見る）」に直した
- `.claude/agents/writer.md` の「実際に `ls` する」を
  「実際に `git ls-files` か `find` する」に直した
- `.claude/agents/implementer.md` と `.claude/agents/verifier.md` の
  「`grep` で当たりを付けてから」を「`rg -n` で当たりを付けてから」に直した
- `CLAUDE.md` の CodeGraph 節にあった `ytsched.py:781` / `同 1051` /
  `738 と 1107` のような行番号を外し、`SchedDataFile` / `SchedData` の
  クラス名だけの記述にした

## 確かめたこと

- verifier に 4 か所の反映と、書き換えたコマンド例（`git ls-files`、
  `find`、`rg -n`、`~/.claude/bin/todo-index.py`）を実際に叩かせて確認した
- 4 か所とも編集が反映されており、コマンド例はいずれも期待どおり動作した

## 残ること

- `~/.claude/bin/todo-index.py` は `--help` を引数として解釈せず、通常実行
  されてしまう（引数解析が無い模様）。verifier が確認中に気づいたが、
  TODO-201 の範囲外のため直していない。実害は未確認

## 分担の振り返り

- verifier は、書き換えた 4 か所の反映確認に加えて、コマンド例
  （`git ls-files`、`find`、`rg -n`、`todo-index.py`）を実際に叩いて
  期待どおり動くかまで確認した。`todo-index.py` の引数解析漏れという
  範囲外の気づきも拾えた
- 見込みどおり、main の編集 + verifier の確認だけで足りた。レビューの
  担当を外した判断（文書と定義ファイルだけの変更）も想定どおりだった
- 次に同じ規模（文書・定義ファイルの文言修正）の項目でも、この組み方
  （main が編集、verifier がコマンド例の再現）でよい
