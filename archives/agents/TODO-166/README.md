# TODO-166 の分担

| 担当 | 何を任せたか |
|------|--------------|
| main（Opus 5 / effort medium） | 現状の把握、依頼の作成、文書の仕上げ |
| implementer | `LoadMonthPages` の追加、`_mk_month_blocks()` の変更、テストと文書の書き換え |
| verifier | lint・型チェック・全件テスト、起動して設定ごとのブロック数を実測 |

## この分担にした理由

`LoadMonths` という前例がそのまま手本になる項目で、設計の判断はほぼ無い。
一方で、触るファイルはソース 2 つ・テスト 2 つ・文書 3 つに散らばるので、
実装は implementer に任せた。

確かめる中身は「設定の値ごとにブロック数が変わるか」で、実際に起動して
数えられる。書式の確認だけではないので verifier を分けた
（`CLAUDE.md` の「試せる手順があるなら分ける」）。分岐の増減や既存の
挙動の変更が無いので、reviewer は入れていない。

- [implementer への依頼](implementer-brief.md) / [報告](implementer-report.md)
- [verifier への依頼](verifier-brief.md) / [報告](verifier-report.md)
