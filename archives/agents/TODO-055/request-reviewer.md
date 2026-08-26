# TODO-055 reviewer への依頼

## 何をした項目か

`archives/agents/TODO-055/request-verifier.md` の「何をした項目か」と同じ。
先にそれを読むこと。

## 見てほしいこと

`git diff`（develop からではなく、作業ツリーの未コミットの差分）を見る。

- **`calc_week_diff()` の正しさ。** 月曜へ丸めてから `// 7` している。
  負の週、年をまたぐ週、月曜・日曜の境目で誤らないか
- **`body` の `padding-top` を JavaScript で入れている件**（`onloadHdr()`）。
  `body_h` を測るより先に入れているか、検索モードで帯が無いときに壊れないか、
  ソフトキーボードの `followKeyboard()` と食い違わないか
- **`.fixed-top` の `z-index`。** ゲージ（`.my-osd-base` は 10）・
  メニューバー（`.my-menu-bar` は 200）・`.my-bar-content`（100）との
  重なりが意図どおりか
- **日付の欄の `onmousedown` を `{% set %}` で組み立てている件。**
  autoescape との兼ね合い（`main.html` の属性値は `&#x27;` になる）、
  検索モードとの出し分け
- テスト（`tests/test_web.py` の `TestWeekBar` / `TestDateColumn`、
  `tests/test_main_handler.py` の `test_calc_week_diff`）が、
  **わざと元へ戻したときに落ちるか**（素通りするテストになっていないか）
- プロジェクトの決まりからの逸脱（`src/README.md`・`CLAUDE.md`）

## 報告

`archives/agents/TODO-055/reviewer-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。**コードは直さない。**
