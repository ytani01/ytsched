# TODO-035 writer への依頼

TODO-035 が決着したので、文書を仕上げる。

## 読むもの

- `TODO.md` の TODO-035 の節
- `archives/agents/TODO-035/` の 4 ファイル
  （`implementer-request.md` / `implementer-report.md` /
  `verifier-request.md` / `verifier-report.md` / `runner-report.md`）
- `~/.claude/CLAUDE.md` の「TODO.md でのタスク管理」（骨格の決まり）
- 既にある `archives/todo/TODO-034. ….md` を、書き方の見本にする

## 作る・直すもの

### 1. `archives/todo/TODO-035. TODO 項目ごとのトークン消費量を記録する.md`

骨格は **「きっかけ / やったこと / テスト」**。見出しの直後に
`見込み:` / `実施:` / `消費:` の 3 行。

```
見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + wording
実施: main = Opus 5 / effort medium、担当 = implementer + verifier + runner + wording
消費: （ここは空のままにする。main が埋める）
```

- **`見込み:` は書き直さない。** `TODO.md` にあるものをそのまま写す
- `実施:` は実際の編成。**wording はこのあと立てるので、含めてよい**
- **`消費:` の行は `消費: TBD` と書いておく。** コミット直前に main が
  実際の数字へ差し替える（終点のコミットが未定のため、今は出せない）

内容に必ず入れること:

- 何を作ったか（`tools/token-usage.py`、`mise.toml` の `tokens` タスク、
  `fmt` / `typecheck` への `tools` 追加）
- **当初案（着手時と完了時の残りトークンを手で書く）を採らなかった理由**
  ── 残りはリセットを跨ぐと差が壊れ、モデル別の内訳も取れない
- 集計の要点 ── 親セッションと `subagents/agent-*.jsonl` の両方を数える、
  `(requestId, message.id)` で重複を除く（除かないと約 1.9 倍になる）、
  担当名は `agent-*.meta.json` の `agentType` から取る
- **`verifier` が見つけた不具合と、その修正**（下の「テスト」にも関わる）。
  今の規約の前は決着も `docs(todo):` で書いていたため（TODO-013・
  TODO-022）、新しい順に最初に当たったコミットを始点にすると決着の
  コミットを拾ってしまう。いちばん古いものを返すよう直した。
  **同じ間違いが `show_list()`（`--list`）にもあり、そちらは runner が
  見つけた**（main は `find_start()` だけ直して確認を済ませていた）
- 決めたこと ── `消費:` 行は `output` と `cache_creation` と担当ごとの
  割合の 1 行だけ。`cache_read` は書かない（会話の長さでほぼ決まり、
  項目の重さを表さない）。運用は `~/.claude/CLAUDE.md`（形式）と
  ytsched の `CLAUDE.md`（ツールの呼び方と `--since`）に分けて書いた
- **残っている制約** ── transcript が 2026-08-22 以降しか無いので過去の
  項目は遡れない。立ててから着手まで空いた項目は `--since` が要る
  （TODO-029 は有無で cache_creation が 1,042,774 と 301,888 に分かれた）
- **やらなかったこと** ── `tools/token-usage.py` のテストは書いていない。
  `tests/` は `ytsched` の振る舞いを見るもので、足すなら別項目が要る

「テスト」の節には、verifier の独自スクリプトによる検算（TODO-034・
TODO-029 で担当別・モデル別・合計とも一致）と、runner の
`mise run lint` / `uv run pytest tests`（404 passed）を書く。

### 2. `archives/agents/TODO-035/README.md`

誰にどこを担当させたか、**その分担にした理由**、各報告ファイルへの
リンクを書く。`archives/todo/TODO-034` の隣にある README を見本にする。

**分担の理由として書くこと:**

- implementer を立てたのは、ツール 1 本と `mise.toml` にまたがるため
- verifier を立てたのは、**このツールの仕事が「数字を出す」ことなので、
  出た数字が正しいかを独立に検算する必要があった**から。実際、独自
  スクリプトでの検算に加えて実バグを 1 件見つけた
- runner を追加で立てたのは、修正後の lint とテストを走らせるため。
  **判断の要らない実行なので runner で足り、実際に main の見落とし
  （`--list` 側の直し忘れ）を拾った**
- wording を立てたのは、`.md` が複数入るコミットだから

### 3. `TODO.md`

- TODO-035 の節を削る
- 冒頭の「残っている項目」を `TODO-031, TODO-032` に直し、決着した件数を
  32 → 33 に直す
- 「完了済み」の目次のいちばん上に TODO-035 を足す
  （リンクは URL エンコード。既存の行に合わせる）

## やらないこと

- `CLAUDE.md`（両方）の更新 ── main が済ませた
- `tools/token-usage.py` / `mise.toml` の変更
- git のコミット
- `消費:` の数字を自分で埋めること（`TBD` のままにする）

## 報告

`archives/agents/TODO-035/writer-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
