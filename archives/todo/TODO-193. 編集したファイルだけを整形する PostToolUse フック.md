# TODO-193. 編集したファイルだけを整形する PostToolUse フック

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | medium | 11,557 | 52,214 | 87% |
| verifier | Sonnet 5 | medium | 4,626 | 36,703 | 13% |
| 合計 |  |  | 16,183 | 88,917 | 概算 $1.9 |

- 見込みでは main を Sonnet 5 としていたが、着手時のモデルは Opus 5 だった
  （main のモデルを切り替えるのは利用者）。effort は見込みどおり medium
- verifier は定義（`.claude/agents/verifier.md`）の `model: sonnet` /
  `effort: medium` のまま。上書きしていない

## きっかけ

`mise run fmt` は src / tests / tools 全体を舐めるので、編集のたびに叩くには
重い。触った 1 ファイルだけなら即座に終わり、`mise run lint` まで指摘を
溜めずに済む。

## やったこと

- `.claude/hooks/fmt-one.sh` を書いた
  - stdin の JSON から `tool_input.file_path` を取り、`.py` は
    `uv run ruff format` → `uv run ruff check --fix`、`.js` は
    `npx prettier --write` → `npx eslint --fix` を走らせる
  - 自動修正できない指摘が残ったときだけ stderr へ書き `exit 2` で返す
    （PostToolUse では `exit 2` の stderr だけが Claude に渡る）。
    整形しかしていないときは何も言わない
  - `archives/` は `ruff` の対象から外してある（TODO-168）が、ファイルを
    名指しで渡すと `ruff` は exclude を見ない（`--force-exclude` が要る）ので、
    フック側でも外す。`.venv` / `node_modules` / `dist` / `.git` と、
    プロジェクトの外のファイルも同じく外す
- `.claude/settings.json` の `hooks.PostToolUse` に `Edit|Write` で登録した
  （timeout 30 秒）。書き方は既存の `PreToolUse` の項に揃えた

## 確かめたこと

verifier が担当した（`../agents/TODO-193/verifier-report.md`）。不具合なし。

- `.py` / `.js` とも整形と自動修正が効く。直せない指摘が残るときは stderr へ
  出て `exit 2`、残らないときは無言で `exit 0`
- `.md`、`archives/` の下、`.venv` / `node_modules` / `dist` の下、
  プロジェクトの外、存在しないファイルでは何もしない
- 空入力、`file_path` の無い JSON、JSON として不正な入力、空白や日本語を
  含むパス、シンボリックリンクでも落ちない
- フックが有効な状態での連続編集も壊れない。verifier のセッションでは
  `Write` の直後に Claude Code 自身から「PostToolUse hook がファイルを
  書き換えた（おそらく整形）。次の `Edit` は stale-file エラーにならない」
  という通知が届き、同じファイルへの続きの書き込みも成功した

## 分担の振り返り

- **verifier は不具合を見つけなかった。** ただし、想定外の入力（不正な
  JSON、空白や日本語を含むパス、シンボリックリンク）と、フックが有効な
  状態での連続編集は main が試していない範囲で、そこを埋めたのは効いた。
  「`CLAUDE_PROJECT_DIR` だけ一時ディレクトリに向けて cwd を揃えないと
  prettier が無言で終わる」という指摘も、実運用では起きないが、あとで
  同じ試し方をしたときに迷わずに済む
- **見込みと食い違ったのは main のモデルだけ**で、担当の編成は見込みどおり。
  シェルスクリプト 1 本と設定 1 箇所なので、implementer を分ける規模では
  なかった
- **次に同じ規模（フック 1 本＋設定）をやるなら、同じく main + verifier で
  よい。** ただし main の側で最低限の動作確認まで済ませてから渡すと、
  verifier の担当が「想定外の入力」と「実際にフックが動く状態での確認」に
  寄って、重複が減る。今回はそうなっていた
