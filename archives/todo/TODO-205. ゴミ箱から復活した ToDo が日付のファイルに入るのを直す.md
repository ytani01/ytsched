# TODO-205. ゴミ箱から復活した ToDo が日付のファイルに入るのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Sonnet 5.5 / 記載なし | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | 記載なし | 64 | 9,914 | 83,859 | 1,784,472 | 70% |
| reviewer | Opus 5.5 | high | 36 | 1,449 | 69,483 | 485,840 | 21% |
| verifier | Sonnet 5.5 | medium | 20 | 193 | 29,126 | 228,265 | 10% |
| 合計 |  |  | 120 | 11,556 | 182,468 | 2,498,577 | 計 2,692,721 |

- main は Sonnet 5.5 で動いた（見込みは Opus 5.5）。effort は記録に残らないので「記載なし」
- 集計は `--since '2026-09-30 05:10:41'`（TODO-206 の決着コミットの時刻）。決着の作業
  （このファイルの作成など）の分は含まない。サブエージェントの分は少なめに出る
- reviewer は 1 回目がセッションの使用上限（429）で止まり、報告が出なかったので
  同じ依頼で起動し直した。上の reviewer の分には 1 回目も入っている

## きっかけ

`TrashHandler._restore()` は `add_sde(restored.date, …)` で復活させるので、ToDo も
締切日のファイルへ入った。一覧のリンクは `is_todo()` で `todo_flag=true` を付け、
`EditHandler` は `ToDo.jsonl` を探すため、復活した ToDo は編集画面が 404 になった。

## やったこと

- `src/ytsched/trash_handler.py` の `_restore()`: `restored.is_todo()` なら
  `add_sde(None, …)`（`ToDo.jsonl`）へ入れる。`SchedUpdater.cmd_add()` と同じ分け方
- `tests/test_web.py` に `test_restore_todo_goes_to_todo_file_and_edit_opens` を追加
- 既に日付のファイルへ入ってしまった ToDo には何もしない（利用者が決めた。2026-09-30）

## 確かめたこと

- 修正を戻すと新テストが落ちる（main と verifier が実測）
- 全体テスト 707 件、lint、型チェック（basedpyright / mypy）が通る
- 実アプリ（一時 `--datadir`）で、復活 POST が 302 で `ToDo.jsonl` へ入り、
  `/edit?...&todo_flag=true` が 200（verifier）
- reviewer は 6 点（`cmd_add()` との一致、`is_todo()` の判定、redirect、保存経路、
  テストの強さ、`_restore_id()` の走査）に問題なし。同じ不具合を持つ呼び出し元も無い

## 分担の振り返り

- reviewer は指摘なし。確信度の低い点として「ToDo なら `None`」の分け方が
  `cmd_add()` と `_restore()` の 2 か所になったことを挙げた（実害は未確認）。
  3 か所目ができるなら `SchedData` 側にまとめる余地がある
- verifier は実測で全項目一致。食い違いは無かった
- 見込みと食い違ったのは main のモデル（Opus 5.5 → Sonnet 5.5）だけ。実装は 1 行の
  分岐で、Sonnet で足りた
- 次に同じ規模（分岐 1 つ + テスト 1 つ）をやるなら、main は Sonnet 5.5 のまま、
  reviewer は 1 回で済む依頼にする。verifier の実アプリ確認（xsrf の cookie を付けた
  curl）は、自動テストが同じ経路を通るので、頼まなくてもよかった
