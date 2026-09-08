# verifier 確認報告

確認日: 2026-09-09

## 構文と設定

- ○ `python3` で `~/.codex/hooks.json` と `.codex/hooks.json` を `json.loads`。
  いずれも終了コード 0。
- ○ `python3` の `tomllib.loads` で `~/.codex/config.toml` を読み込み。終了コード 0。
- ○ `~/.codex/config.toml` は `model_reasoning_effort = "medium"`。
  `.claude/agents/verifier.md` も `effort: medium`。
- ○ `.codex/agents/*.toml` 6 個を `tomllib` で読み込み、`name` は
  `implementer, reviewer, runner, verifier, wording, writer`。各 `name` に対応する
  `.claude/agents/<name>.md` が存在する。

## PreToolUse

入力はすべて `{"tool_input":{"command":...}}` を stdin へ渡した直接実行。

- ○ 共通 `~/.claude/hooks/guard-bash.sh`: `git status --short` rc=0、
  `command cp a b` rc=0。
- ○ 共通フック: 裸の `cp a b` rc=2、`git push origin main` rc=2。
  stderr はそれぞれ `cp はエイリアスで -i が付き、確認プロンプトでセッションが固まる。`、
  `git push は利用者が行う（2026-09-03 に決めた）。`。
- ○ repo `.claude/hooks/guard-bash-ytsched.sh`: `git status --short` と
  `command cp a b` rc=0、`uv run ytsched webapp --datadir /tmp/ytsched-check` rc=0。
- ○ repo フック: `uv run ytsched webapp` rc=2、`mise run upgradeproject` rc=2。
  stderr の要点は `--datadir の無い ytsched の起動は、既定の /home/ytani/ytsched/data（実データ）を使う。`、
  `mise run upgradeproject は依存を上げ直す（rm -f uv.lock → uv sync → uv pip install -U）。`。
- ○ 共通と repo の両方を実行する構成では、裸の `cp` と `git push` は共通フックで拒否される。
  repo フック単体は ytsched 固有の保護だけを担当し、同2コマンドを rc=0 とした。

## fmt-patch.py

- ○ repo 内の `mktemp -d` で専用一時ディレクトリを作り、`apply_patch` で未整形の
  `sample.py` / `sample.js` と JSON event を作成して実行。`python3 .codex/hooks/fmt-patch.py`
  の rc=0。実測結果は Python が `def add(a, b):` と4スペースの本体、JavaScript が
  Prettier の改行・セミコロン付きの関数へ整形され、`py_compile` と `node --check` も rc=0。
  検証後、作成ファイルを `apply_patch` で削除し、生成された pycache も削除して一時ディレクトリを除去した。
- ○ `patch_paths()` と `subprocess.run` の mock で、複数パス、`*** Move to:` の移動先、
  Delete、`archives/`、`.claude/`、プロジェクト外パスを確認。整形呼び出しは Python と
  JavaScript の2件だけで、除外対象は呼ばれなかった。

## 変更範囲と制限

- `git status --short`: `.codex/hooks.json`、`.codex/README.md`、`.codex/agents/`、
  `.codex/hooks/`、`archives/agents/TODO-197/` のみ。
- `git diff --check` は終了コード 0。`git diff --name-only -- .claude` は空。
  既存 Claude ファイルは変更されていない。
- Codex 本体が設定を再読み込みし、実際のセッションでフックを実行することは未確認。
  追加・変更した定義を未信頼の状態から実行するには `/hooks` による信頼登録が必要。
  起動中担当への agent 定義反映も未確認。
