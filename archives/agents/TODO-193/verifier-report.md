# TODO-193 verifier 報告

対象: `.claude/hooks/fmt-one.sh`（新規）、`.claude/settings.json` の `hooks.PostToolUse`

## 1. フックを直接叩いての確認（○）

すべて一時ディレクトリ（scratchpad 配下、実運用では `CLAUDE_PROJECT_DIR` を
プロジェクトルートに揃えた状態）で確認した。

- `.py`: `ruff format` + `ruff check --fix` が実行され、未使用 import の削除・
  空白の整形が反映された（`import os` が削除され `x=1` → `x = 1` に）。exit=0
- `.js`: `prettier --write` + `eslint --fix` が実行され、`const x=1` →
  `const x = 1;` のように整形された
- 自動修正できない指摘が残るケース:
  - `.py` に `F821 Undefined name` を仕込むと、stderr に指摘を出して exit=2
  - `.js` に `no-undef 'console' is not defined` を仕込むと、stderr に
    ESLint の指摘を出して exit=2
- 指摘が残らないときは exit=0 で無言（stdout/stderr とも空）を確認
- `.md`、`archives/*.py`、`.venv/*.py`、`node_modules/*.js`、`dist/*.js`、
  プロジェクト外のファイル（`/tmp/outside.py`）、存在しないファイルは
  すべて exit=0 で何もしない（stdout/stderr 空）ことを確認

## 2. 想定外の入力（○）

- 空入力（`printf ''`）: exit=0
- `tool_input.file_path` が無い JSON: exit=0
- JSON として不正な入力（`not json`）: exit=0（`jq` が失敗し `|| exit 0` で拾う）
- パスに空白・日本語（`日本語 dir/変な名前 test.py`）: 正しく整形され exit=0
- シンボリックリンク（`link.py` → `real.py`）: 実体側 `real.py` が整形され exit=0

いずれも落ちない。

## 3. `.claude/settings.json` の書式（○）

正しい JSON（`cat` で確認、パースエラー無し）。`PostToolUse` の
`matcher: "Edit|Write"` / `hooks: [{type: "command", command: ..., timeout: ...}]`
の形は、同じファイルの `PreToolUse`（`guard-bash-ytsched.sh`）の項と揃っている。
`command` はどちらも `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/<script>.sh"` の形。

## 4. フック有効時の Edit/Write の連続実行（○、ただし別プロセス起動は行っていない）

`claude -p` での別プロセス起動は行わず、代わりに**このセッション自体で
フックが実際に有効になっていた**ため、それを使って直接確認した。

- 汚いコード（未整形 `.py`）を一時ファイル `.tmp_verify_193_hook.py`
  （プロジェクト直下、作業後に削除済み）へ `Write` すると、直後に
  システムから
  `PostToolUse:Write hook additional context: PostToolUse hook modified
  ...tmp_verify_193_hook.py after your edit (likely a formatter). Your next
  Edit will not fail with a stale-file error, ...`
  という通知が実際に届いた。フックが動作し、ファイルが書き換わったことを
  Claude Code 自身が検知している
- 続けて同じファイルへもう一度 `Write` を行っても、エラーにならず
  `has been updated successfully` で成功した
- （`Edit` ツール自体は verifier の許可ツールに無いため試していないが、
  `Write` で同じファイルへの連続書き込みが壊れないことは確認できた。
  システム側の通知文面からも、直後の `Edit` が stale-file エラーに
  ならないことが保証されている）

## 見つかった不具合

なし。

## 補足（バグではないが、テスト方法上の注意点）

`fmt-one.sh` は `CLAUDE_PROJECT_DIR` の値でファイルの所属を判定するが、
`uv run` / `npx` はスクリプトを起動した**プロセスの cwd** の設定
（`pyproject.toml` / `eslint.config.js` など）を見て動く。検証中、
`CLAUDE_PROJECT_DIR` だけを一時ディレクトリに向けて cwd を ytsched の
ままにしたところ、prettier がファイルを一切書き換えずに無言で終了する
現象が出た（cwd 外の絶対パスを渡すと prettier が config 解決に失敗して
何もしないように見える）。cwd も `CLAUDE_PROJECT_DIR` に揃えて実行し
直すと正常に整形された。実運用では Claude Code がプロジェクトルートを
cwd としてフックを起動するはずなので、フック自体の不具合ではないと
判断した。念のため報告する。
