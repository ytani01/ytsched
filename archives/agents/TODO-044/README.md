# TODO-044 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer + wording |

## 誰にどこを担当させたか

| 担当 | 範囲 |
|------|------|
| main | `.claude/agents/verifier.md`・`implementer.md`、`~/.claude/CLAUDE.md` の消費の行、単価の確認 |
| implementer | `tools/token-usage.py`（集計の直しと概算料金） |
| verifier | 直した集計が実際に動くか。過去の項目で数字が変わることの確認 |
| reviewer | `tools/token-usage.py` の変更 |
| wording | このコミットに入る `.md` すべて |

## その分担にした理由

- **`.claude/agents/*.md` と `~/.claude/CLAUDE.md` は main が書いた。**
  担当の走らせ方そのものを決める文書で、どこを絞るかは利用者に聞いて
  決めた内容。implementer に渡すと、依頼書に決定を書き写す手間のほうが
  大きくなる。`~/.claude/CLAUDE.md` は利用者全体の設定でもある
- **`tools/token-usage.py` は implementer に出した。** 集計の直しと料金の
  計算で、複数の関数（`collect` / `Usage` / `fmt_shares` / `print_table` /
  `print_summary`）にまたがる
- **reviewer を入れた。** 数え方そのものを変える項目で、テストが通っても
  数字が正しいとは限らない（`~/.claude/CLAUDE.md` の「挙動や分岐が変わる
  項目には入れる」）
- **wording を入れた。** `.md` が入るコミットなので

## 報告

- [implementer](implementer-report.md)（依頼: [implementer-request.md](implementer-request.md)）
- [verifier](verifier-report.md)
- [reviewer](reviewer-report.md)
- [wording](wording-report.md)（項目を立てたときの分。着手後の分は
  [wording-report2.md](wording-report2.md)）
