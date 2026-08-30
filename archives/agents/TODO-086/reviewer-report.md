# TODO-086 reviewer 報告

## 再確認

先の指摘は解消済み。`src/ytsched/trash.py` は `trashed_at` をマイクロ秒
まで記録し、`docs/data-format.md` の形式も同じ精度へ更新された。
`tests/test_trash.py` も、同じ `sde_id` を続けて削除した 2 行の
`trashed_at` が異なることを確認している。秒精度の衝突で別の行を復活する
問題は残っていない。
