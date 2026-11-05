# TODO-232. 詳細欄のブラウザテストがまれに落ちるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 不明 | 5 | 521 | 3,447 | 315,029 | 64% |
| ver-229（verifier） | Sonnet 5.5 | medium | 10 | 1,356 | 3,008 | 173,071 | 36% |
| 合計 |  |  | 15 | 1,877 | 6,455 | 488,100 | 計 496,447 |

- 原因を調べた分は TODO-229・TODO-231 の範囲に入っていて、ここには入らない

## きっかけ

TODO-231 の確認で、TODO-227 で足した `test_detail_fills_between_bars_and_blur_shrinks_it` が 4 回に 1 回落ちた。

## やったこと

- `tests/test_browser.py`: 待つ条件の `h > 300` は縮む前の高さ 368px でも通るので、処理の前に判定へ進むことがあった。`h > 300 && h < 360` にした

## 確かめたこと

verifier の報告は `archives/agents/TODO-232/verifier-report.md`。

- このテストを 8 回続けて実行し、8 回とも通った
- `resize` のリスナーを外すと、`wait_for_function` のタイムアウトで落ちる

## 分担の振り返り

- **各担当が見つけたもの:** verifier がこの不具合を見つけ、修正後も失敗しないことと、壊すと落ちることを確かめた
- **見込みと食い違った点:** 無し
- **次の編成への指示:** 値を待つテストでは、変化の前の値で条件が通らないかを、書くときと reviewer の観点に入れる。TODO-227 の reviewer にはテストの強さを頼んだが、この待ち方は見つからなかった
