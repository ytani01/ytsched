# TODO-194 verifier 報告

## 1. SKILL.md の手順の再現

- 手順5 `~/.claude/bin/token-usage.py TODO-191` → ○ 実行できた（main 73% + general-purpose 24% + verifier 3%、概算 $3.5）
- 同 `--since '2026-09-07 00:00:00'` 付き → ○ 実行できた（概算 $11.4）。ただし `WARNING: <synthetic>: 単価表に無いモデル .. claude-opus-5 の単価で概算` という警告が出る。SKILL.md の説明とは無関係の既存のスクリプト側の挙動なので、SKILL.md の不備ではない
- 手順6 `grep -c '^- \[\*\*TODO-' TODO.md` → ○ `194` を返し、「これまでに 194 件を決着させた」と一致
- 手順8 の「終点は `docs(todo):` 以外のコミット」→ ○ `token-usage.py` の `find_end` は `docs(todo):` で始まらず `（TODO-NNN）`（全角カッコ）を含むコミットを終点にしている（`START_PREFIX = "docs(todo):"` と docstring 17行目に明記）。SKILL.md の記述と一致
- frontmatter の `disable-model-invocation` / `argument-hint` → ○ 両方とも Claude Code の実在するキー。`~/.claude/plugins/marketplaces/claude-plugins-official/` 配下の複数の公式プラグイン（`claude-security`, `cwc-makers`, `example-plugin`, `plugin-dev/skills/command-development/SKILL.md` の解説など）で同じキーが使われている

## 2. 書式が todo-workflow に合っているか

- 見出しの構成（きっかけ / やったこと / 確かめたこと）は todo-close の手順3のテンプレートどおり。TODO-194 自身の決着ファイルもこの構成
- 2 つの表の列は todo-workflow のテンプレートと一致（見込み/実施の表、担当ごとの output/cache_creation/料金の割合の表）
- ファイル名 `archives/todo/TODO-194. 項目の決着処理を todo-close スキルにまとめる.md` は「節見出しそのまま」の規則どおり（`` `/todo-close` `` のバッククォートは外れて `todo-close` の文字だけになっている点は妥当な解釈）

## 3. TODO.md の4か所

- ○ 節が削除されている（TODO-194 の節は消えている）
- ○ 目次の先頭（194 が 195・196 より上、195は196より上）に追加されている。194→195→196 の順は「決着した順（新しい順）」と一致（195 のコミットが最新、196 はその前、194 は今回作業中で未コミット）
- ○ 残っている番号「TODO-192・193」に更新されている
- ○ 決着件数「194 件」に更新され、`grep -c` の実測値と一致

## 4. 目次のリンクの実在照合

- 全 194 件のリンクを機械的に urldecode してファイル存在を確認。**1 件だけ既存の不具合を発見（TODO-194 の変更とは無関係）**
  - `archives/todo/TODO-073.%20クレジット表示を「(c)%202026%20ytani01」に統一する.md` にリンクされているが、実ファイル名は括弧の直後で切れた形になっており存在しない（`ls` で確認すると実ファイル名が違う）。これは TODO-073 のときからの既存の問題で、今回の diff（`git diff HEAD -- TODO.md`）には含まれていない
- TODO-194・195・196 自身のリンクは 3 件とも実在するファイルを指しており問題なし

## 5. SKILL.md 同士の二重記述

- 表の列・`cache_read` を入れない理由などの書式は todo-close 側に無く、「手順2で todo-workflow を読む」という案内のみ。二重記述は見当たらなかった
- 手順5 の「出力の2行目は貼らない」は todo-workflow には無い記述だが、これは `~/.claude/CLAUDE.md` 本体に既にある注意（「出力の 2 行目...は貼らない」）と重複している。実害は無いが、todo-close 側にも `~/.claude/CLAUDE.md` にもほぼ同文があり、三重にはなっていないが二重ではある（判断不要、参考情報）

## 結論

見つけた不具合は「TODO-073 のリンク切れ」1件のみだが、これは TODO-194 の変更とは無関係の既存の問題。TODO-194 自身の変更・新設スキルには不備は見つからなかった。
