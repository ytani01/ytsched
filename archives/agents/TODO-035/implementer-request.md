# TODO-035 implementer への依頼

`tools/token-usage.py` を書き、`mise.toml` に `tokens` タスクを足す。
背景は `TODO.md` の TODO-035 を読むこと。

## 作るもの

### 1. `tools/token-usage.py`

TODO 項目ごとに、Claude Code の transcript からトークン消費量を集計して
表示するコマンドラインツール。

**呼び出し方**

```
uv run python tools/token-usage.py TODO-034
uv run python tools/token-usage.py TODO-034 --since '2026-08-23 14:00:00'
uv run python tools/token-usage.py --list
```

- 引数は TODO 番号（`TODO-034` / `034` / `34` のどれでも受ける）
- `--since` で始点の時刻を手で指定できる（立ててから着手まで空いた項目用）
- `--list` は集計できる項目を一覧する（任意。作らなくてもよい）

**範囲の決め方**

git のコミット時刻で切る。

- 始点: コミットメッセージが `docs(todo):` で始まり、本文に
  `TODO-NNN` を含むもの。そのコミットの author date
- 終点: 本文に `（TODO-NNN）`（全角カッコ）を含む、`docs(todo):` 以外の
  コミット。そのコミットの author date
- 始点が見つからないときはエラーにして、`--since` を使うよう促す
- 終点が見つからないときは「まだ完了していない」とみなし、現在時刻までを
  集計する（その旨を出力に書く）
- `--since` が指定されたら始点の検索はせず、そちらを使う

`git log` は `subprocess` で呼んでよい。タイムゾーンに注意
（transcript の `timestamp` は UTC の ISO 8601、`git log` の author date は
ローカル時刻）。どちらも aware な `datetime` に揃えてから比較すること。

**集計するもの**

対象ディレクトリ: `~/.claude/projects/-home-ytani-work-ytsched/`

- 親セッション: 直下の `<uuid>.jsonl`
- サブエージェント: `<uuid>/subagents/agent-*.jsonl`
  - 同じディレクトリの `agent-*.meta.json` に `agentType`
    （`implementer` / `verifier` / `wording` など）が入っている。
    担当名として使う。meta.json が無いときは `unknown`

各行は JSON。`message.usage` を持つ行だけを見る。範囲の判定は行の
`timestamp`。

**重複行の除去（重要）**

同じ usage が複数行に現れる。実測で 117 行のうちユニークは 61 件だった。
`(requestId, message.id)` の組で一度だけ数えること。この除去を入れないと
値が倍近くになる。

**出力**

主に見るのは `output_tokens` と `cache_creation_input_tokens`。
`cache_read_input_tokens` は会話の長さでほぼ決まり、項目の重さを表さない
ので、参考として別に出す（合計欄には入れるが、主指標と区別が付くように）。

次の 3 つを出す。数値は桁区切りを入れて読みやすく。

1. 範囲（始点・終点の時刻と、それをどのコミットから取ったか）
2. 担当別の内訳（`main` と各 `agentType`）
3. モデル別の内訳（`claude-opus-5` / `claude-sonnet-5` など）

最後に、archives の TODO ファイルへ貼れる形の 1〜2 行を出す。形式は
下の「3. 書く形」に合わせること。

**書き方**

- `src/` のコードと同じ書き方に揃える。型ヒントを付け、`ruff format
  --line-length 78` と `basedpyright` / `mypy` が通ること
- ログは `mylog.py` のラッパを使う（`CLAUDE.md` 参照）。
  ただしこのツールは `src/ytsched` のパッケージ外なので、import 経路を
  確かめること。うまく通らないなら、ログ無しにして `print` で済ませて
  よい（その判断を報告に書く）
- 標準ライブラリだけで書く。依存を足さない
- `~/.claude/projects/...` のパスは定数にし、プロジェクト名の部分は
  カレントディレクトリから導く（`/` を `-` に置換した形）。
  ハードコードしない

### 2. `mise.toml`

- `[tasks.tokens]` を足す。
  `run = "uv run python tools/token-usage.py"`。
  `mise run tokens -- TODO-034` のように引数を渡せること
- `fmt` と `typecheck` の対象 `src tests` に `tools` を足す

### 3. 書く形（archives の TODO ファイル）

`archives/todo/TODO-NNN. ….md` の `見込み:` / `実施:` の行の下に、
`消費:` の行として 1 行で書く。案:

```
消費: output 12,345 / cache_creation 678,901（main 40% + implementer 35% + verifier 25%）
```

**この形が妥当かどうか、実際に集計した結果を見てから判断して報告すること。**
桁が大きすぎて読みにくい、担当の割合が要らない、といったことがあれば、
別案を出してよい。決めるのは管理者。

## 確かめること

- `TODO-034`（始点 `4b68048` 14:59、終点 `fe0aba3` 15:13）で実際に走らせ、
  それらしい数字が出ること。この項目は verifier + wording を使っている
- `TODO-029` でも走らせてみること（始点が離れている例）
- `mise run fmt` / `typecheck` が `tools` を含めて通ること

## やらないこと

- `CLAUDE.md` の更新（管理者が別に行う）
- `TODO.md` のチェックボックス更新
- git のコミット
- `mise run upgradeproject` の実行

## 報告

`archives/agents/TODO-035/implementer-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
