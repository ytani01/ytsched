# TODO-035 writer 報告

## 作った・直したファイル

- `archives/todo/TODO-035. TODO 項目ごとのトークン消費量を記録する.md`
  （新規）── 骨格は「きっかけ / やったこと / テスト」。見出し直後に
  `見込み:` / `実施:` / `消費: TBD` の 3 行。`見込み:` は `TODO.md` に
  あったものをそのまま写した。`実施:` の担当には runner を足した。
  依頼書で指定された内容（採らなかった案の理由、集計の要点、
  verifier が見つけた不具合とその修正、`消費:` 行の形の決定、残っている
  制約、やらなかったこと）をすべて入れた
- `archives/agents/TODO-035/README.md`（新規）── 誰にどこを担当させたか、
  分担の理由（implementer / verifier / runner / wording それぞれ）を
  `archives/todo/TODO-034` 隣の README を見本に書いた
- `TODO.md`（変更）── TODO-035 の節を削除、冒頭の「残っている項目」を
  `TODO-031, TODO-032` に、決着件数を 32 → 33 に直し、「完了済み」目次の
  先頭に TODO-035 を追加（リンクは既存行と同じ形で `%20` のみエンコード）

`消費:` の数字は埋めていない（`TBD` のまま）。

## 実物を確かめた方法

- `archives/agents/TODO-035/` の 6 ファイル（implementer-request/report、
  verifier-request/report、runner-report、wording-report）と
  `writer-request.md` を読んだ
- `TODO.md` の TODO-035 節、`~/.claude/CLAUDE.md` の「TODO.md でのタスク
  管理」節を読んだ
- `git status` / `git diff --stat HEAD` / `git log --oneline -5` で
  現在の作業ツリーの状態（`CLAUDE.md`・`mise.toml` の変更、`tools/` が
  未追跡）を確認
- `git diff HEAD -- mise.toml` で実際の変更内容を確認
- `grep -n` で `CLAUDE.md`（プロジェクト）の「トークン消費量の記録」節と
  `~/.claude/CLAUDE.md` の `消費:` 行の説明（main が既に更新済み）を確認
  し、`消費:` の書式（`output` / `cache_creation` / 担当ごとの割合、
  `cache_read` は書かない）が依頼書の内容と一致することを確かめた
- `tools/token-usage.py` の `find_start()` の docstring とコードを読み、
  「いちばん古いものを返す」よう直っていること（verifier が見つけた
  不具合の修正）を確認
- `archives/todo/TODO-034. ….md` と隣の `README.md` を書き方の見本にした
- リンクの URL エンコードは `python3 -c "urllib.parse.quote(...)"` で
  試したうえで、既存行（TODO-034 など）が空白だけ `%20` にして日本語は
  そのままにしていることを確認し、それに合わせた

## 判断が要る点

特になし。`消費:` の数字は依頼どおり `TBD` のままにしてある。main が
`tools/token-usage.py TODO-035`（`--since` の要否も含めて）で数字を
出し、割合とともに埋めることになる。
