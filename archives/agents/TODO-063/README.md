# TODO-063 の分担

コードを 1 箇所直すだけの項目だが、**挙動が変わる**ので reviewer も入れた
（`~/.claude/CLAUDE.md` の基準）。

| 担当 | 任せたこと | 報告 |
|------|-----------|------|
| main | 実装（`moveToMonday()` の `days` の計算） | — |
| verifier | lint・test と、playwright での動作確認 | [verifier-report.md](verifier-report.md) |
| reviewer | 直し方と境界、呼び出し元への影響 | [reviewer-report.md](reviewer-report.md) |
| wording | 前例の無い語を挙げる | [wording-report.md](wording-report.md) |

依頼書は [request.md](request.md)。

- verifier は、**変更前のコードで症状が再現すること**まで確かめた
  （playwright の `page.route()` で `my.js` の本文だけ差し替えた）
- reviewer の指摘は無し。「滑らせて見せる週とのずれも消えている」ことは
  reviewer が気づいたもので、archives の本文に取り込んだ
- wording が挙げた「滑らせる先」は、既出の言い回しに合わせて
  「滑らせて見せる週」へ直した
