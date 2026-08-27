# TODO-077 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 81,695 / cache_creation 429,208 / 概算 $43.8 |
|      | main 96% + verifier 3% + implementer 1% + reviewer 1%（料金の割合） |

## なぜこの分担にしたか

データの保存の順番を変える項目で、**壊れると予定が消える**。
`ytsched.py` と `main_handler.py` とテスト 2 ファイルにまたがるので、
実装も分けた（implementer）。

挙動が変わる項目なので reviewer も立てた（`CLAUDE.md` の基準どおり）。
実際、reviewer は「テストが通ること」を見ても出てこない指摘を 2 件出した。

## 報告

- [implementer-report.md](implementer-report.md) — 実装
- [verifier-report.md](verifier-report.md) — 不具合なし。
  `git stash` が auto mode に拒否されたため `git worktree` で修正前を
  用意し、直す前は本当に壊れていたことも確かめた
- [reviewer-report.md](reviewer-report.md) — 2 件の指摘。**どちらも直した**
  1. `_dirty_dates` が例外で残ると、次の関係の無いリクエストの保存に
     紛れ込む（この変更で新しく開いた経路）→ `exec_update()` を
     `try`/`finally` にした
  2. `save()` が日付から `get_sdf()` で引き直すので、LRU で捨てられると
     変更が消える → `SchedDataFile` そのものを覚えるようにした

## 消費について

**main の 96% は、担当の完了を待つ間のポーリングで積み上がったもの**で、
この項目の重さを表していない。サブエージェントを起動したあと、
`git status` を短い間隔で繰り返し叩いて完了を待ったため、main の
メッセージが 533 件になった（cache_read 7,700 万）。
**担当の完了は通知で届くので、待つ間は何も叩かないこと。**
