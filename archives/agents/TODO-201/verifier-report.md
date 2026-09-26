# TODO-201 verifier 報告

## 確認した4か所

1. `.agents/skills/ytsched-workflow/SKILL.md` 35-36行目
   ○ 「`TODO.md` から完了項目の節を削除する（一覧は `archives/index.md` を見る）」に直っていた。
2. `.claude/agents/writer.md` 15行目
   ○ 「実際に `git ls-files` か `find` する」に直っていた。
   - 実行: `git ls-files | wc -l` → 1182件、`find . -maxdepth 2 -type f | wc -l` → 88件。
     どちらもエラー無くファイル一覧が出た。
3. `.claude/agents/implementer.md` 18行目付近 / `.claude/agents/verifier.md` 57行目付近
   ○ どちらも「`rg -n` で当たりを付けてから」に直っていた。
   - 実行: `rg -n "SchedData" src/README.md` → 該当行が出力された（`SchedDataEnt` /
     `SchedDataFile` / `SchedData` を含む行）。期待どおり動作。
4. `CLAUDE.md`（CodeGraph 節）
   ○ `ytsched.py:781` / `同 1051` / `738 と 1107` の行番号表記が消え、
     「`SchedDataFile` と `SchedData` の 2 つ、`save` も同じ 2 つのクラスにある」と
     クラス名だけの記述に直っていた。

## `~/.claude/bin/todo-index.py` の動作確認

- ○ 実在し、実行できた。`~/.claude/bin/todo-index.py --help` を叩いたところ、
  `--help` はオプションとして解釈されず、通常どおり実行されて
  `archives/index.md: 200 件` と出力した（このスクリプトは引数を取らない模様）。
- 実行後 `git diff --stat archives/index.md` を確認したところ差分は無し
  （既存の `archives/index.md` と同じ内容が再生成された、冪等）。
  `git status --short` でも編集対象4ファイル以外に変更は無いことを確認した。

## 判断が要る点

- `todo-index.py` は `--help` 引数を無視してそのまま実行してしまう
  （引数解析をしていない可能性）。依頼の「`--help` などで動作確認」は
  「実行できるか」の確認としては通ったが、ヘルプ表示機能自体は無いようだ。
  TODO-201 の対象外なので直していない。実害は未確認。

## 結論

依頼された4か所の編集はすべて正しく反映されており、書き換えたコマンド例
（`git ls-files`、`find`、`rg -n`）は実際に書いたとおり動作した。
`todo-index.py` も実行できることを確認した。
