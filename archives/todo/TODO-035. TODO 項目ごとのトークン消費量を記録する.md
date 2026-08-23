# TODO-035. TODO 項目ごとのトークン消費量を記録する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + wording |
| 実施 | Opus 5 / effort medium | implementer + verifier + runner + writer + wording |
| 消費 | output 24,816 / cache_creation 331,968（全体） | main 26% + implementer 20% + verifier 16% + writer 15% + wording 15% + runner 9% |

分担の理由と各担当の報告は `archives/agents/TODO-035/` にある。

## きっかけ

「この規模ならどの担当で足りたか」を振り返る材料が、今までは見込みと
実施の分担しか無かった。実際にどれだけトークンを使ったかが分かれば、
次の項目の見立てに使える。

当初は「着手時と完了時の残りトークンを手で書く」案だったが、採らな
かった。残りはリセットを跨ぐと差が壊れるうえ、モデル別の内訳も取れない。
**Claude Code の transcript から集計する**ことにした。

## やったこと

`tools/token-usage.py` を新規に書き、`mise.toml` に `tokens` タスクを
足した（`fmt` / `typecheck` の対象にも `tools` を加えた）。

```
mise run tokens -- TODO-034
mise run tokens -- TODO-034 --since '2026-08-23 14:00:00'
mise run tokens -- --list
```

**集計の要点**

- `~/.claude/projects/-home-ytani-work-ytsched/` の下、親セッションの
  `<uuid>.jsonl` と、サブエージェントの
  `<uuid>/subagents/agent-*.jsonl` の**両方**を数える。片方だけだと
  実測で 3 分の 1 になる
- 同じ `usage` が複数行に現れる（同じ assistant メッセージ内の複数の
  tool_use ブロックごとに繰り返される）ため、`(requestId, message.id)`
  の組で一度だけ数える。除去しないと約 1.9 倍になる
- 担当名は `subagents/agent-*.meta.json` の `agentType` から取る
- 範囲は git のコミット時刻で切る。始点は
  `docs(todo): … を TODO-NNN として立てる`、終点は
  `feat/fix(...): …（TODO-NNN）`。どちらもコミットメッセージの
  **1 行目だけ**を見る（本文まで見ると、たまたま別の項目に触れている
  コミットを始点に拾ってしまう）

**verifier が見つけた不具合と、その修正。** 今の「決着は `docs(todo):`
以外のコミットで書く」という規約が定まる前（TODO-013・TODO-022）は、
決着も `docs(todo):` プレフィックスで書いていた。始点探索が「新しい順に
見て最初に当たったもの」を返していたため、これらの項目では決着の
コミットを始点として誤って選び、さらに本来の終点が「始点より古い」と
判定されて捨てられ、「まだ完了していない」扱いで現在時刻までを集計して
しまっていた。**当てはまるものが複数あれば、いちばん古いものを返す**
よう `find_start()` を直した。**同じ間違いが `show_list()`（`--list`）
にもあり、そちらは runner が見つけた**（main は `find_start()` だけ直して
確認を済ませていた）。

**決めたこと。** archives の TODO ファイルに貼る `消費:` 行は、
`output` と `cache_creation` の数値、それに担当ごとの割合を 1 行だけ
書く形にした。`cache_read` は書かない。会話の長さでほぼ決まり、項目の
重さを表さないうえ、桁が 1 つ違うので貼ると他の数字が霞む。

```
消費: output 21,282 / cache_creation 163,913（main 64% + verifier 18% + wording 18%）
```

運用は `~/.claude/CLAUDE.md`（`消費:` 行の形式そのもの）と、
ytsched の `CLAUDE.md`（ツールの呼び方、`--since` の使いどころ）に
分けて書いた。

## 残っている制約

- transcript が 2026-08-22 以降しか残っていないため、それより前の項目は
  遡れない
- **立ててから着手まで空いた項目は `--since` が要る。** 間に別の項目の
  作業が挟まると、その分も数に入ってしまう。TODO-029 は `--since` の
  有無で cache_creation が 1,042,774 と 301,888 に分かれた

## やらなかったこと

`tools/token-usage.py` のテストは書いていない。`tests/` は `ytsched` の
振る舞いを見るためのもので、`mise run test` の対象もそちら。テストを
足すなら別項目が要る。

## テスト

verifier が、`tools/token-usage.py` とは別に自分で書いた検算スクリプトで
TODO-034・TODO-029 の担当別・モデル別・合計を突き合わせ、すべて一致を
確認した（`(requestId, message.id)` の重複除去が正しいことも、生の行を
見て確かめている）。修正後、runner が `mise run lint`
（ruff / basedpyright / mypy）と `uv run pytest tests`（404 passed）を
走らせ、いずれも通ることを確認した。
