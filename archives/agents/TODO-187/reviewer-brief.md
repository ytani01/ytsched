# TODO-187 reviewer への依頼

## 目的

TODO-187（ゲージをフッターの直上にも出す）の変更が **良いか**を見る。
コードは直さない。見つけたことは報告するだけ。

## 前提

- 依頼の全文は `archives/agents/TODO-187/implementer-brief.md`
- implementer の報告は `archives/agents/TODO-187/implementer-report.md`
- 変更は未コミット。`git diff` で見る

## 見てほしいところ

- **針・ラベル・`my-gauge-r-no-transition` の反映漏れ**が無いか。
  複数のゲージへ一斉に反映する形になっているが、抜けている経路
  （ドラッグ中・cancel・読み直し直後の `placeGaugeWithoutTransition()`）は無いか
- **`elGaugeR0` → `elGaugeRs` の置き換え**で、意味が変わってしまった
  判定が無いか（特に「検索モードでゲージが無い」の判定）
- **`mondayFromClientX()` の帯の持ち回り**が、down / move / up で
  一貫しているか。`gaugeBarDragStart` が null になる経路で
  帯の参照が残らないか
- **`body` の `paddingBottom` / `paddingTop` の計算順**が、
  `fillMainHeight()` や `body_h` / `win_h` の測定と噛み合っているか
- CSS の `z-index` の関係（下のゲージ 50 / `.my-bar-content` 100 /
  `.my-menu-bar` 200）が意図どおりか
- テストが**本当に意味のあることを見ている**か。
  上下が同じであることを、たまたま通るだけの形で見ていないか
- 既存のコメント・命名・`(TODO-NNN)` の付け方の決まりからの逸脱

## 報告

`archives/agents/TODO-187/reviewer-report.md` に、
**指摘・根拠・直すべきかの判断材料**を書く。
返事は 5 行以内。
