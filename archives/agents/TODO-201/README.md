# TODO-201 の分担

文書と定義ファイルだけの変更で、確かめる中身が「書式が揃っているか」に
とどまらないため（コマンド例が書いたとおりに動くかの再現が要る）、
main が編集し、verifier に確認を分けた。レビューの担当は入れていない
（挙動が変わる変更ではないため）。

- **main**: `.agents/skills/ytsched-workflow/SKILL.md`、
  `.claude/agents/writer.md`、`.claude/agents/implementer.md`、
  `.claude/agents/verifier.md`、`CLAUDE.md` の 4 か所を編集
- **verifier**: 編集内容の反映確認と、書き換えたコマンド例
  （`git ls-files`、`find`、`rg -n`、`todo-index.py`）の再現。
  報告は [verifier-report.md](verifier-report.md)
