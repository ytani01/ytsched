# TODO-197 reviewer 報告

## 指摘

無し。

## 確認した内容

- `.codex/hooks/fmt-patch.py:10-17` は `Add File` と `Update File` の
  パスを集め、`Move to` では直前の更新元を移動先へ置き換える。`Delete File`
  は集めず、最終的に存在しないファイルも `:28` で外すため、追加・更新・
  移動先だけが整形対象になる。
- 同ファイル `:27-40` はパスを `resolve()` してからプロジェクト配下かを
  判定する。プロジェクト外への `..` とシンボリックリンク、`.claude/`、
  `archives/`、生成物、Python・JavaScript 以外は整形対象から外れる。
- `.codex/hooks.json:4-23` の `Bash` と `Edit|Write` は Codex の
  `exec_command` と `apply_patch` に一致し、どちらも `tool_input.command`
  を既存の Claude 用スクリプトまたは変換スクリプトへ渡す。リポジトリ側の
  hook は Git ルートから解決しており、サブディレクトリから開始した
  セッションでも対象を見失わない。
- `~/.codex/hooks.json:3-23` は共通ガードと CodeGraph の prompt hook を
  Claude の設定に合わせ、既存の `SessionStart` 2 件を残している。
  `~/.codex/config.toml:2` の effort は Claude の `medium` と一致する。
- `.codex/agents/*.toml` 6 件は必須の `name`、`description`、
  `developer_instructions` を持ち、TOML として読み込めた。各担当は対応する
  `.agents/agents/*.md` と `.claude/agents/*.md` を読む指定で、モデル系列と
  effort も今回の方針および Claude 側の定義に対応している。
- リポジトリの `git diff` に `.claude/` の変更は無い。`~/.claude` には
  `settings.json` の末尾改行だけの既存差分があるが、更新時刻は今回の Codex
  設定変更より前だった。レビュー開始前の状態は別途保存していないため、
  ユーザー全体の Claude 設定が今回まったく変更されていないことの厳密な確認は
  未実施。

## 未確認

- `/hooks` での信頼登録後に Codex 本体が各 hook を起動すること。
- 新しい Codex セッションで 6 担当が一覧・起動に反映されること。

上記 2 点は既知の未確認事項で、コード上の指摘には数えていない。

## 参照した仕様

- <https://learn.chatgpt.com/docs/hooks>
- <https://learn.chatgpt.com/docs/agent-configuration/subagents>
