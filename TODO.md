# TODO

**残っている項目: TODO-198。** これまでに 197 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-199` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-198. runner・verifier の定義の古い記述を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main（実装）+ verifier（Sonnet 5 / medium） |

`/claude-api prompt-audit`（2026-09-27）で見つかった 3 件。

- [ ] 着手前に verifier に測らせる: `lint` の依存のどれかを落とした状態で
      `mise run test` を叩き、残りのタスクが走るか止まるか
- [ ] runner の「`mise run lint` / `test` は使わない」の理由を直す
      （`.claude/agents/runner.md:37-40`）
- [ ] runner のコマンドの対象に `tools` を足す
      （`.claude/agents/runner.md:30-33`、`.agents/agents/runner.md:19-22`）
- [ ] verifier の「（TODO-003 以降）」「（TODO-004 以降）」を消す
      （`.claude/agents/verifier.md:29-30`）
- [ ] verifier に、直した runner の 5 つのコマンドを走らせて通るか確かめさせる

**背景**

- runner は「`mise run lint` / `test` は `upgradeproject` に依存して
  依存を上げ直すから使わない」と書いているが、TODO-023 で依存は切った。
  今の `mise.toml` の `lint` は `fmt, fmtjs, typecheck, lintjs` だけに
  依存する。`CLAUDE.md` も「叩かせてよい」と書いていて食い違う
- `mise.toml` の `fmt` / `typecheck` は `src tests tools` を見るが、
  runner は `src tests` だけで、`tools/*.py` が検査から漏れる
- Codex 側（`.agents/agents/runner.md`）も揃える（TODO-197 の方針。
  2026-09-27 に利用者が決めた）。`.codex/agents/runner.toml` は
  コマンドを持たないので直さない

**決めること**

- 1 つ目の測定で決まる。止まるなら「途中で止まり残りの結果が取れない」と
  理由を書き直して個別のコマンドを残す。止まらないなら、runner の
  コマンドを `mise run test` に置き換えるかを利用者に聞く
- JavaScript（`fmtjs` / `lintjs`）を runner に足すかは、この項目では扱わない
- reviewer は入れない。変わるのは定義の文言とコマンドの対象で、
  分岐の意味が変わるコードは無い

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
