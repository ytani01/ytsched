# TODO-077. `fix` で `.bak` が中間状態に上書きされるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 81,695 / cache_creation 429,208 / 概算 $43.8 |
|      | main 96% + verifier 3% + implementer 1% + reviewer 1%（料金の割合） |

## きっかけ

基本設計のレビュー（`docs/design-review.md` の B）で見つかった。

`exec_update()` は `fix` を `cmd_del()` → `cmd_add()` で実装していて、
`SchedData` の `del_sde()` / `add_sde()` がそれぞれ `sdf.save()` を
呼んでいた。同じ日のファイルが 1 回の修正で 2 回保存され、**2 回目の
`.bak` が 1 回目の結果（1 件消えた状態）を写す**。

| | 中身 |
|---|---|
| 修正前のファイル | 予定A, 予定B |
| 修正後の `.bak` | **予定A のみ** |

修正前の内容がどこにも残らず、バックアップとして働いていなかった。

## 決めたこと

**`exec_update()` 一式（約 400 行）は `main_handler.py` に置いたまま
にした。** 前半の `get_date_arg()` / `get_time_arg()` /
`get_deadline_str()` が tornado の `get_argument()` に依存していて、
`SchedData` を受け取るクラスへ出すには、フォームの値の取り出しと変換を
先に分けなければならない。それは TODO-081 の「引数と設定値の変換・検証を
`HandlerBase` から出す」そのものなので、順序を逆にすると同じ場所を
二度触ることになる。**置き場所は TODO-081 のあとで考え直す。**

## やったこと

**保存を「変更」から切り離し、1 回の更新で 1 ファイルにつき 1 回だけ
書くようにした。**

- `SchedData.add_sde()` / `del_sde()` が `sdf.save()` を呼ぶのをやめ、
  変更のあった `SchedDataFile` を `_dirty_sdf` に覚えるだけにした
- `SchedData.save()` を新しく作り、覚えている `SchedDataFile` を
  1 つにつき 1 回 `save()` して、覚えた分を空にする
- `exec_update()` が `cmd_del()` / `cmd_add()` を `try` で囲み、
  `finally` で `self._sd.save()` を 1 回呼ぶ

日付ではなく `SchedDataFile` そのものを覚えるのは、`save()` までの間に
LRU キャッシュから捨てられると、日付から引き直したときに**変更の乗って
いない別のインスタンス**になり、変更が黙って消えるため（reviewer の指摘）。

`finally` にしたのは、`SchedData` がアプリ全体で 1 つだからで、途中で
例外が出たときに変更の印を残したまま抜けると、**次の関係の無い
リクエストの保存に紛れ込む**（reviewer の指摘）。この経路は、保存を
切り離したことで新しく開いたもの。途中まで保存されること自体は、
切り離す前と同じ挙動。

`SchedDataFile.save()` は変えていない。空のファイルをバックアップ
しない決まり（TODO-005）もそのまま。

## テスト

- `tests/test_web.py::TestUpdate::test_fix_keeps_backup_of_both_entries`
  — **本題。** 同じ日に 2 件あるファイルで片方を `fix` し、`.bak` に
  両方残ることを HTTP 経由で見る
- 同 `::test_exec_update_saves_even_on_error` — 途中で例外が出ても、
  そのリクエストの中で保存され、印が残らないこと
- `tests/test_ytsched.py::test_sched_data_save_after_cache_discard`
  — キャッシュから捨てられた日の変更も保存されること
- 同 `::test_sched_data_save_writes_once_per_date` — 同じ日に 2 回
  `add_sde()` しても `SchedDataFile.save()` は 1 回
- 既存の `SchedData` のテスト 3 つを、`save()` を呼ぶ形に直した
- `mise run lint` 通過。`uv run pytest tests` 461 passed

verifier は、`git worktree` で修正前のコードを用意して**直す前は本当に
壊れていたこと**を確かめ、追加した 2 本のテストが**修正を戻すと落ちる**
ことも確かめた（`git stash` は auto mode に拒否されるので使えない）。
日付を変える `fix`、`add` / `del` / `update`、ToDo の追加・削除・完了も
HTTP 経由で確認している。

分担と報告は [`archives/agents/TODO-077/`](../agents/TODO-077/README.md)。
