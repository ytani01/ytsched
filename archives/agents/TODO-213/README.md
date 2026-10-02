# TODO-213 の分担

- implementer（Sonnet 5.5 / medium）: `main_handler.py`・`main-page.js`・`my.css`・テストにまたがるので分けた。報告は `implementer-report.md`
- reviewer（Opus 5.5 / high）: リダイレクトの分岐と、点滅の見え方（背景色・週の移動）が変わるので入れた。報告は `reviewer-report.md`（再確認の節を含む）
- verifier（Sonnet 5.5 / medium）: lint・テストと、追加・修正・削除・update を実機で 1 回ずつ。報告は `verifier-report.md`、スクリーンショットは `flash.png`
- `measure_flash.py` は、点滅の黄色の画素の割合を測るスクリプト（implementer が作り、verifier が使い回した）
