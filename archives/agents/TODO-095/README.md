# TODO-095 の分担

見込みでは「決めるだけの項目」として `main のみ` にしていた。実際には
`pyproject.toml` と `src/ytsched/ytsched.py` を変えたので、CLAUDE.md の
決まりに従って確認を別の担当に分けた。

| 担当 | 見たところ | 報告 |
|------|-----------|------|
| main | 候補の規則を走らせて指摘の数を数え、どこまで足すかを決めた。`B007` の 1 件を直した | — |
| verifier | `lint` / `typecheck` / `test` の結果、`_i` への改名で挙動が変わっていないこと | [verifier-report.md](verifier-report.md) |
| wording | コミットに入る `.md` の、前例の無い語 | [wording-report.md](wording-report.md) |

`reviewer` は入れていない。変更が `extend-select` の 1 行と、ループ変数の
改名 1 か所だけで、挙動も分岐も変わらないため。

wording を走らせる順番を間違えた件は
[TODO-095 の archives](../../todo/TODO-095.%20ruff%20の規則を増やすか決める.md)
に書いた。
