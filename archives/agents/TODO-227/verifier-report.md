# TODO-227 verifier 報告

条件: chromium(playwright)、viewport 412×780 → キーボード代用で 430、40 行の詳細を持つ予定を `--datadir` 一時ディレクトリで起動。
スクリプト: `archives/agents/TODO-227/verify_detail_fill.py`（`uv run python` で実行）、生の値: `verify_detail_fill.json`。
開始時の `git status`: 依頼外の変更なし（`model-check.md` のみ変更済み、これは報告置き場）。

読み込み時（780、フォーカスなし）: #detail top 234 / bottom 602 / h 368、バー下端 45、下バー上端 735、scrollY 0。
フォーカスなしで 430 に縮めた場合: top 234 / bottom 334 / h 100（上限の計算値）、scrollY 0。

| # | 項目 | 結果 | 測った値 |
|---|---|---|---|
| 1 | click → 430 | ○ | top 45 = 上バー下端 45、bottom 385 = 下バー上端 385、h 340、scrollY 189 |
| 2 | 780 に戻す（フォーカス保つ） | ○ | top 234 / bottom 602 / h 368（読み込み時と同じ）、scrollY 0、active=detail |
| 3 | 再び 430 → title へフォーカス | ○（※） | 430 に縮めた直後は 1 と同じ（h 340）。title フォーカス後: top 234 / bottom 334 / h 100、scrollY 0 |
| 4 | title click → 430 → detail click | ○ | top 45 / bottom 385 / h 340 / scrollY 189（1 と一致） |
| 5 | フォーカスなし 430 → detail click | ○ | top 234 / bottom 334 / h 100、scrollY 0（広がらない） |
| 6 | スクリーンショット | ○ | `item6_detail_filled_430.png`: 欄と上下のバーは重ならず、1〜12 行目の文字が読める |

※ 3 の「読み込み時の計算の高さ」: 戻った高さは 780 時の 368 ではなく、430 の画面で計算した 100。
依頼の文言が前者を意図していたなら食い違い。追加したテスト（`test_detail_fills_between_bars_and_blur_shrinks_it`）は 100 を期待しているので、後者の読みで一致。どちらが意図かは main の判断。

## pytest
`uv run pytest tests/test_browser.py -k "test_detail_fills or test_detail_focus_does_not_move or test_detail_click_does_not_fill or test_detail_manual_height"` → 5 passed, 91 deselected。
サーバログ: 例外・トレースバックなし。起動したサーバは終了済み（PID 残りなし）。

## 見つけた不具合
なし。実機キーボードは未確認（依頼範囲外）。
