# TODO-198. runner・verifier の定義の古い記述を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main（実装）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | 不明 | 7,918 | 46,939 | 88% |
| verifier | Sonnet 5 | medium | 2,660 | 36,045 | 12% |
| 合計 |  |  | 10,578 | 82,984 | 概算 $2.0 |

- main は見込みの Sonnet 5 に切り替えずに着手した。effort は記録に残らず分からない
- main の分には、項目を立てたとき（06:14〜）のやり取りも含まれる

## きっかけ

`/claude-api prompt-audit`（2026-09-27）で、runner・verifier の定義に古い記述が 4 件見つかった。

- runner は「`mise run lint` / `test` は `upgradeproject` に依存して依存を上げ直すから使わない」と書いていたが、TODO-023 で依存は切ってあり、`CLAUDE.md` の「叩かせてよい」と食い違っていた
- `mise.toml` の `fmt` / `typecheck` は `src tests tools` を見るが、runner は `src tests` だけで `tools/*.py` が漏れていた
- verifier の確認の型に「（TODO-003 以降）」「（TODO-004 以降）」が残っていた
- runner は `model: haiku` なのに `effort: low` があった。Haiku 4.5 は `effort` に対応しない

## やったこと

- 着手前に verifier に測らせた。worktree で `mise run test` を叩くと、依存の `fmtjs` が落ちた時点で mise が `ERROR task failed` で止まり、`typecheck`・`lintjs`・pytest は走らなかった。止まるので、個別のコマンドを残す方にした
- `.claude/agents/runner.md`: `mise run lint` / `test` を使わない理由を「依存のタスクが 1 つ落ちると残りが走らず、残りの結果が取れない」に書き直した。`effort: low` を消した
- `.claude/agents/runner.md`・`.agents/agents/runner.md`: pytest 以外の 4 つのコマンドの対象に `tools` を足した
- `.claude/agents/verifier.md`: 「（TODO-003 以降）」「（TODO-004 以降）」を消した

## 確かめたこと

- verifier が、直した 5 つのコマンドを本体で順に走らせ、すべて終了ステータス 0（pytest は 611 passed, 85 skipped）。ruff の書き換えは無し
- `.agents/agents/runner.md` と `.claude/agents/runner.md` のコマンド 5 行が一字一句同じ

## 残ること

- 定義を読み直すには Claude Code の再起動が要る（再起動は利用者）

## 分担の振り返り

- verifier: 測定では、worktree に `node_modules` が無く、用意した型エラーより先に `fmtjs` で止まった。狙った `typecheck` の失敗ではないが、「依存が 1 つ落ちると下流を走らせない」ことは確かめられた。実行確認ではコマンドがすべて通ることと、Codex 側との一致を確かめた
- 見込みとの食い違いは main のモデルだけ（Opus 5.5 のまま着手した）。料金の 88% が main なので、次は見込みどおり Sonnet 5 に切り替えてから着手する
- 次に同じ規模なら同じ組み方でよいが、worktree で mise を測らせるときは `npm ci` を先に済ませるよう依頼に書き、狙った依存で落ちるようにする
