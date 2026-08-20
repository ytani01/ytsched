# TODO-007. loguru への移行 — 分担

## 分担

| 担当 | 範囲 | 報告 |
|---|---|---|
| main（Opus 5 / high） | 下調べ、方針の決定、依頼と取りまとめ | — |
| `implementer` | `mylog.py` の持ち込み、6 ファイルの書き換え、テストの追随 | [implementer-report.md](implementer-report.md) |
| `verifier` | pytest / mypy / ruff の実行、webapp の起動確認 | [verifier-report.md](verifier-report.md) |

## この分担にした理由

書き換えが 6 ファイル・ログ呼び出し約 123 箇所に及び、あわせて公開引数
（各クラスの `debug`）も変わるので、実装の担当を分けた。
確認は、実装した本人が「動くはず」で済ませないように `verifier` へ回す。

`reviewer` は付けていない。tmr に既にある `mylog.py` をそのまま持ち込み、
呼び出し側は機械的な書き換えが大半で、設計を決める余地が小さいため。

## 決めたこと（依頼前に利用者と確認済み）

- 各クラスの `debug` 引数は**廃止**する（`SchedDataEnt` / `SchedDataFile` /
  `SchedData` / `HandlerBase`）。ログの水準は `loggerInit()` と
  `getLogger()` だけで決める。`WebServer` の `debug` は tornado の
  `autoreload` / `debug` 設定に要るので残す
- ログ呼び出しの書式は **f-string**（tmr に揃える）

## 決着

項目そのものの記録は
[archives/todo/TODO-007. loguru への移行.md](../../todo/TODO-007.%20loguru%20への移行.md)。

担当から上がった判断点への回答:

1. **`tests/helpers.py:53` の `debug=False`** — 実物は
   `tornado.web.Application(...)` に渡す tornado 自身の設定で、今回廃止した
   クラスの `debug` 引数ではなかった。**残すのが正しい**（main の依頼文が
   誤って「直す対象」に挙げていた）
2. **`loggerInit()` を呼ばないときに loguru 既定の stderr / DEBUG が効く件**
   — **そのままにする**。tmr と同じ作りで、揃えるのがこの項目の趣旨。
   テストが失敗したときに DEBUG が見えるのは手がかりにもなる
