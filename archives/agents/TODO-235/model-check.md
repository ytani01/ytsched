## 2026-11-11 03:01 impl-235（implementer、model: sonnet、effort: medium）

結論: 見合う
理由: 変更範囲はテストのみで、既存の `_mark` / `_wait_for_reload` / `_wait_for_top_screen` を使い回す小さな差分なので、sonnet と medium で足りる。`reloadHome()` を外して落ちるかを確かめる手順も 1 通りに決まっており、上位モデルや high 以上の effort は要らない。

