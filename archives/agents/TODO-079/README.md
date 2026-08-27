# TODO-079 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 8,750 / cache_creation 130,544 / 概算 $2.4 |
|      | main 61% + implementer 24% + verifier 13% + wording 2%（料金の割合） |

## なぜこの分担にしたか

**挙動を変えない**項目なので、reviewer は立てていない
（`CLAUDE.md` の基準は「挙動や分岐が変わる項目には入れる」）。
`main_handler.py` とテストにまたがり、引数の受け渡しを組み替えるので、
実装は分けた（implementer）。

verifier には、**条件を変えた 8 パターンで HTML を突き合わせる**ことを
任せた。実装者は 1 つの URL でしか確かめておらず、検索・絞り込み・
`todo_days` が負・`LoadMonths` を変えた場合は通る道が違う。

main のモデルは、着手時点で Opus 5 のままだった（見込みは Sonnet 5）。

## 報告

- [implementer-report.md](implementer-report.md) — 実装
- [verifier-report.md](verifier-report.md) — 不具合なし。8 パターンとも
  HTML に差は無かった（唯一の差はバージョン表示で、worktree と本体で
  `git describe` の値が違うため）
