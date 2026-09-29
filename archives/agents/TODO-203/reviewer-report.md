# TODO-203 reviewer の報告

対象: `git diff HEAD -- .claude/agents CLAUDE.md`（runner.md・writer.md は
`git show HEAD:` で読んだ）。Codex 側、archives、`docs/token-usage-analysis.md` は見ていない。

## 観点ごとの結果

- 観点 1（落ちた内容）: 指摘 2 件（下の B・D）。それ以外は移っているか、落としてよいもの
- 観点 2（移した先との矛盾）: 指摘 2 件（下の A・B）
- 観点 3（`~/.claude/CLAUDE.md` との食い違い）: 指摘 1 件（下の A）。「規約を書き写さない」は守られている
- 観点 4（`CLAUDE.md` の 3 行）: 事実どおり。`.claude/agents/` は 4 ファイル。effort については下の C（確信度低）
- 消した定義への参照: `.claude/`・`CLAUDE.md`・`docs/`・`src/` に残っていない（`rg --hidden -w -e runner -e writer`、archives・Codex 側・`TODO.md` を除く。`tests/test_fix_id.py` の `runner` は `CliRunner` の変数名で無関係）

## 確信度の高い指摘

### A. verifier に `ruff` の書き換えを持たせたことが、グローバルの規則と字面で食い違う

- 場所: `.claude/agents/verifier.md` 16〜18 行（書き込みの例外）、44〜62 行（定型の実行）
- `~/.claude/CLAUDE.md` は「確認・レビューの担当には、コードを直させない」としている。
  runner は確認の担当ではない位置づけだったので目立たなかったが、verifier は確認の担当
  そのもので、その定義の中に「ソースを書き換えるコマンドを走らせる」手順が入った
- 同じ定義の 14 行「コードを直さない」には例外が書かれておらず、16〜18 行の
  「書き込んでよいのは報告ファイルだけ（例外は ruff）」とだけ対応している。
  runner にあった「`ruff` が自動で書き換えた分であって、あなたが直すのではない」の断りは
  移っていない
- 問題になる状態: 「reviewer を先、verifier を後」の順で回したとき、reviewer が見た差分の
  あとに verifier の `ruff check --fix` が import の並べ替えや自動修正を入れる。
  reviewer はその書き換えを見ていない。`--fix` は整形だけでなく、未使用 import の削除
  のような修正も入れうる（実害は未確認。どの規則の fix が効くかは確かめていない）
- 許容するか（定型の実行だけは例外とする、`--fix` を外して検査だけにする、など）は
  境界線上の判断なので main に委ねる

### B. 定型の実行の「落ちた分は全文」が、同じ定義の報告の決まりと食い違う

- 場所: `.claude/agents/verifier.md` 63〜65 行 と 70 行・76 行
- 定型の実行は「落ちた分は全文」、報告の節は「目安は 60 行以内」「例外が出たら、その部分だけ貼る」。
  runner には 60 行の目安が無かったので、移したことで生じた食い違い
- 問題になる状態: mypy と pytest が両方落ちたとき（エラー数十件＋トレースバック）。
  全文を写すと 60 行を大きく超え、どちらに従うかは担当の読み方次第になる。
  「全文は報告ファイルへ、60 行の目安は返事ではなく…」のように、どちらを優先するかを
  書くかどうかは main の判断

## 確信度の低いもの

### C. haiku に上書きしたとき、frontmatter の `effort: medium` が残る

- 場所: `.claude/agents/verifier.md` 6 行、`CLAUDE.md` の足した 3 行
- 3 行そのものは effort に触れておらず、誤りは無い。ただ、haiku への上書きでは
  `effort: medium` が付いたまま起動する。Haiku は effort に対応しないので効かないはずだが、
  エラーになるか黙って捨てられるかは **未確認**
- 記録の面では、決着時の表で verifier（Haiku 4.5）の effort をどう書くか
  （skill の例は「記載なし」で、理由を「定義に effort の行が無い」としている）が
  今の定義と合わなくなる。表の下の注記の書き方を決めておくかは main の判断

### D. 細かい脱落（落としてよいと思われるもの）

- runner の「終了ステータス（`echo $?`）」の `echo $?` → 手段の例示だけなので落としてよい
- runner の「たぶん〜が原因」「〜を直せば通る」は書かない → verifier 19〜20 行
  「推測しない。直し方を提案しない」で覆われている
- writer の「たぶんこうなっているはず、で書いた文書は迷わせる」（理由の一文）→ 落としてよい
- writer の日本語の 3 規則 → `~/.claude/CLAUDE.md` の「日本語の書き方」（31 行〜）と
  「造語を使わない」（21 行、「進め方」の中の 1 項目）を指す形になった。指す先は実在する。
  mermaid の規則も「日本語の書き方」の節に入っているので拾える
- writer の description にあった「CLAUDE.md」が implementer の description
  （「README・docs・archives」）から外れている。名指しで呼ぶので実害は無いと思われる
- verifier の追加は「原因の切り分けをしない」「実害は未確認と添える」を入れたが、
  グローバルにある「境界線上の判断もさせない」は入っていない。依頼側に書く規則なので
  定義に無くても足りる、とも読める

指摘に挙げた以外は、runner・writer の手順は移っている。

## 再レビュー

対象は `git diff HEAD -- .claude/agents/verifier.md`。A・B が解消したかと、直したことで新しい食い違いが出ていないかだけを見た。C・D は main の判断どおり対象外。

- A: 解消。定型の実行は `ruff format --check` と、`--fix` を付けない `ruff check` になり、ファイルを書き換えない。「書き込んでよいのは報告ファイルだけ」の例外と `git diff --stat` の行も消えていて、14〜17 行の「コードを直さない」「報告ファイルだけ」と矛盾しない
- B: 解消。「落ちた分はエラーの出た部分だけ」になり、報告の節の「例外が出たら、その部分だけ貼る」と揃った
- 新しい食い違い: 無し。`--line-length 78` と `--extend-select I` は `pyproject.toml` の `[tool.ruff]`（`line-length = 78`、`extend-select` に `I`）と同じ値で、指定が重なっているだけ。implementer が走らせる `mise run fmt`（`ruff format` / `ruff check --fix`）も同じ設定を読むので、整形済みのコードが定型の実行の検査で落ちることは無いと読める（実行はしていない）
