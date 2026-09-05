# TODO-185 の分担

ゲージの追従までの待ち時間を定数にして `conf.json` で変えられるようにする項目。
Python・JavaScript・テンプレート・文書・テストにまたがるうえ、既定値が
1000 → 500 に変わって挙動も変わるので、実装・確認・レビューを分けた。

| 担当 | 役割 |
|------|------|
| implementer | `GaugeFollowMsec` の追加（`AutoTurnMsec` と同じ経路）、既定 500 への変更、文書・テストの追加 |
| verifier | `mise run lint` / `typecheck` / `test` の実行と、`data-gauge-follow-msec` が実際に HTML へ出ることの確認 |
| reviewer | 既定値が変わったことによる影響、`AutoTurnMsec` の経路との食い違い、gauge.js 側の値の読み方 |

報告は同じディレクトリの `*-report.md`。
