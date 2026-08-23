# TODO-035 verifier への依頼

implementer が作った `tools/token-usage.py` と `mise.toml` の変更を確かめる。

## 読むもの

- `TODO.md` の TODO-035 の節（何のためのツールか）
- `archives/agents/TODO-035/implementer-request.md`（依頼した内容）
- `archives/agents/TODO-035/implementer-report.md`（実装者の報告と、
  単独で決めた判断 8 件）

## 確かめること

### 1. 集計そのものが正しいか（ここが本題）

このツールは「数字を出す」のが仕事なので、**出た数字が正しいかを
自分で検算すること**。実装者の報告を鵜呑みにしない。

- **重複除去。** `(requestId, message.id)` で除去している。除去の前後で
  どれだけ変わるか、除去が正しいか（本当に同じ usage の重複であって、
  別の課金対象を潰していないか）を、transcript の生の行を見て確かめる
- **範囲の判定。** transcript の `timestamp` は UTC、`git log` の
  author date はローカル（JST）。9 時間ずれていないか。境界の行が
  入る・入らないの判定が意図どおりか
- **親と subagents の両方を数えているか。** TODO-035 の背景に
  「親だけ集計すると 3 分の 1 になる」とある。片方が抜けていないか
- **担当名（`agentType`）の対応付け。** `subagents/agent-*.meta.json` から
  取っている。取れなかったときの `unknown` が実際には出ていないか
- 担当別・モデル別の各合計が、全体の合計と一致するか

検算には、`tools/token-usage.py` とは**別に自分で書いた短いスクリプト**を
使うこと（同じコードで確かめても意味が無い）。スクリプトは
`archives/agents/TODO-035/` に置かず、一時ディレクトリで済ませてよい。

### 2. 実際に走るか

- `uv run python tools/token-usage.py TODO-034`
- `uv run python tools/token-usage.py TODO-029`
- `uv run python tools/token-usage.py TODO-029 --since '2026-08-23 14:30:00'`
- `mise run tokens -- TODO-034`（mise 経由で引数が渡るか）
- `--list`
- 異常系: 引数なし、`abc`、`TODO-999`、`--since` に壊れた文字列、
  プロジェクトの外での実行。**落ち方**（終了コードとメッセージ）が
  まともかを見る

### 3. 実装者が単独で決めた判断

報告の「単独で決めた判断」8 件を読み、**それぞれ妥当かを見る**。特に:

- 判断 1（コミットメッセージの 1 行目だけを見る）— これで取りこぼす
  ケースが無いか。過去のコミットログを実際に当たって確かめる
- 判断 2（始点より古い終点は使わない）— TODO-022 / TODO-013 で実際に
  どうなるか
- 判断 8（`<synthetic>` モデルを落とさない）

### 4. lint・テスト

- `mise run fmt` / `mise run typecheck` が `tools` を含めて通るか
- `uv run pytest tests` が通るか（既存への影響が無いか）

## やらないこと

- **コードを直さない。** 見つけたことは報告するだけ。直すかどうかは
  管理者が決める
- `TODO.md` / `CLAUDE.md` の更新
- git のコミット
- `mise run upgradeproject` の実行

## 報告

`archives/agents/TODO-035/verifier-report.md` に書く。
検算に使ったスクリプトの中身と、その結果を必ず載せること。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
