# TODO-167 の分担

| 担当 | 依頼 | 報告 |
|------|------|------|
| implementer | [implementer-brief.md](implementer-brief.md) | [implementer-report.md](implementer-report.md) |
| verifier | [verifier-brief.md](verifier-brief.md) | [verifier-report.md](verifier-report.md) |

## この分担にした理由

TODO-166（月間表示の `LoadMonthPages`）と対になる項目で、設定キーを 1 つ
置き換えるだけの部分は手本がそのまま使える。ただし今回は

- `months2weeks()` の削除で、`main_view.py` / `main_handler.py` /
  `ytsched.py` のコメント / テストの期待値が連動して変わる
- `conf.json` を既定値で作る処理が `ConfFile` に新しく増える

の 2 つがあり、複数ファイルにまたがるので implementer を分けた。
`conf.json` を作る側は「既存データのある datadir で余計なことをしないか」
「既定値を書き出しても挙動が変わらないか」を実際に起動して見る必要があるので、
verifier も立てた（`~/.claude/CLAUDE.md` の「試せる手順があるなら分ける」）。

reviewer は入れていない。挙動が変わるのは設定キーの名前と既定値の範囲で、
分岐そのものは増えないため。
