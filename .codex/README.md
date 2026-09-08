# Codex の設定

指示は `AGENTS.md` から Claude の `CLAUDE.md` と担当定義を参照する。
Claude のファイルは変更しない。

`.codex/agents/` に Claude と同じ6担当を登録する。担当の手順は
`.claude/agents/` を参照し、`wording` は文章作成ではなく初出語の確認を行う。
モデルは既存の Codex 側の選択を基に、実装は Terra、レビュー・検証・文書は
Sol、定型実行は Luna とする。effort は対応する Claude の定義に合わせる。
担当設定を読み直すには、新しい Codex セッションを開始する。

`hooks.json` のコマンド保護は `.claude/hooks/guard-bash-ytsched.sh` を
そのまま呼ぶ。編集後の整形は `hooks/fmt-patch.py` が Codex の
`tool_input.command` から追加・更新・移動先のパスを取り出し、
`.claude/hooks/fmt-one.sh` に渡す。削除、プロジェクト外、生成物、
`archives/`、`.claude/` は整形しない。

ユーザー全体の `~/.codex/hooks.json` には共通のコマンド保護と
CodeGraph の prompt hook を設定する。既存のセッション開始フックは残す。
`~/.codex/config.toml` の思考量は Claude と同じ `medium` にする。
Claude 固有のモデル名、プラグイン、音声・表示機能はコピーしない。

フックを追加・変更したあとは、Codex の `/hooks` で内容を確認して
信頼する。未確認のフックは実行されない。定義の読み込み・信頼登録を含む
Codex 本体からの実行は、スクリプト単体の検証とは別に確認する。

仕様: [OpenAI の hooks ドキュメント](https://learn.chatgpt.com/docs/hooks)
