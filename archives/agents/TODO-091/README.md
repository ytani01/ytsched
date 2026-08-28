# TODO-091 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |

## なぜこの分担か

`sched_load.py`・`main_handler.py`・`main.html`・`tests/test_main_handler.py`
の 4 ファイルにまたがるが、変換は機械的（dict のキー参照を属性参照に置き
換える）。実装は `implementer` 1 人で足りる。挙動は変えないので `reviewer`
は入れない（TODO-017 の基準: 挙動や分岐が変わる項目に入れる）。確認は
`~/.claude/CLAUDE.md` の決まりどおり `verifier` を別に立てる。

## main が決めたこと（着手前）

- **画面のキャッシュ件数表示は残す。** `main.html` の版数の隣に出している
  `({{ sd.get_cache_size() }})` は、`sd` を渡す唯一の理由。表示自体は残し、
  `sd` そのものでなく `cache_size`（int）を render に渡す形にする。
  消すかどうかは別途決める。
- **dataclass は `sched_load.py` に置く。** `SchedLoadCond` /
  `SchedSearchCond` と同じ場所。名前は `SchedDay`（`date` /
  `is_holiday` / `sde`）と `SchedWeek`（`offset` / `monday` / `sched`）。

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
