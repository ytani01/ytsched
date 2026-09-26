# TODO-199. ホームボタンで今日が画面の下にはみ出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Sonnet 5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ reviewer（Sonnet 5 / high）+ verifier（Sonnet 5 / medium、2 回） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | 不明 | 29,868 | 62,812 | 58% |
| verifier | Sonnet 5 | medium | 11,974 | 203,851 | 32% |
| reviewer | Sonnet 5 | high | 2,874 | 89,588 | 10% |
| 合計 |  |  | 44,716 | 356,251 | 概算 $5.9 |

- main の effort は記録に残らず、セッションの設定も確かめていない
- reviewer・verifier はモデルを上書きしていない（定義の sonnet と effort のまま）
- verifier は同じ担当に 2 回頼んだ（ゲージを見落とした分の測り直し）

分担と各担当の報告は [archives/agents/TODO-199/](../agents/TODO-199/README.md)。

## きっかけ

ホームボタンは今週の月曜日を画面の上端に合わせる（TODO-105）。
1 週間の表示が画面より長いと、週末の今日が画面の下にはみ出した。
利用者の希望は「今日がはみ出すときは今日を下端に合わせる。URL は月曜日を指す」。

## やったこと

- `nav.js` の `scrollToId()` に `sde_align == "home"` を足した。
  月曜日は `"top"` と同じ位置に合わせる。今日の欄の下端が、画面の下に
  固定した帯（フッターのゲージ `#footer_gauge_bar`、検索画面では無いので
  `#menu_bar`）の 30px 上より下になるなら、そこまでスクロールする。
  2 つの `scrollY` の大きいほうを取る
- 今日の欄は `getBoundingClientRect().bottom + scrollY` で文書上の位置を
  測る。`offsetTop` は `#week_wrap` からの位置で、文書の上端から 68px ずれる
- `main-page.js` の `homeButtonHdr()`（シングルタップ）と `reloadHome()`
  （ダブルタップの読み直し）が `"home"` を渡す。サーバは `sde_align` を
  そのまま引き継ぐので、読み込み後の位置合わせも同じ式を通る。
  `scrollToDate()` は `date`（月曜日）を URL に積むので、URL は月曜日のまま
- `nav.js`・`main-page.js` の先頭コメントに `today_str` の依存を書いた（TODO-097）
- `tests/test_browser.py`
  - `test_home_button_keeps_today_in_view`: 画面を 412×300 にし、
    `today_str` を日曜に書き換えてホームボタン → 日曜の欄がゲージの上に
    収まり、URL は月曜。`today_str` を月曜にすると `"top"` と同じ位置
  - `test_home_reload_keeps_today_in_view`: `sde_align=home` で開くと
    今日の欄がゲージの上に収まる
  - ダブルタップのテストの `_wait_for_top_screen()` を `sde_align=home` に、
    検索画面のシングルタップの確認を `"sde_align=" not in page.url` に変えた
- 検索画面の 1 回目のタップ（検索語つきの読み直し）と Home キーは変えていない。
  既存の `"top"` / `"bottom"` の `offsetTop` のずれも変えていない

## 確かめたこと

- `mise run lint`（ruff）・`mise run typecheck`・`uv run pytest -q`
  （ブラウザのテストを含む 698 件）が通った。JS の prettier・eslint は
  `node_modules` が無く走らなかった
- 新しい 2 件は、修正を外すと落ちる。ゲージを見ずに `#menu_bar` だけに
  合わせる版に戻しても落ちる
- verifier が PC 1920×1080・1366×768、スマホ 390×844（タッチ）で実測。
  今日＝日曜のシングルタップ・ダブルタップ、今日＝水曜、画面の高さ
  1080→600 のどれでも、今日の欄の下端はゲージの上端から約 30px 上で、
  URL の `date` は月曜日。今日が収まる週では月曜日の位置が `"top"` と同じ。
  スクリーンショットで、今日の最後の予定が隠れていないことを見た

## 残ること

- この環境には `/usr/bin/chromium` が無く、`tests/test_browser.py` は
  そのままでは全部 skip する。今回は `CHROMIUM` を一時的に
  `~/.cache/ms-playwright/chromium-1243/` のものへ差し替えて走らせた

## 分担の振り返り

- **reviewer**: `today_str` の依存が `main-page.js` の先頭コメントに無い点を
  見つけ、直した。もう 1 点（月曜の位置と今日の位置の座標系の食い違い）は、
  比べているのがどちらも `scrollY` なので該当しないと main が判断した
- **verifier**: 1 回目は `#menu_bar` とだけ比べ、今日の欄がフッターのゲージに
  隠れているのを見逃した。main がスクリーンショットを見て気づき、測り直させた。
  数値が揃っていても、画像を main が見るまで気づかなかった
- **見込みとの食い違い**: 担当は見込みどおり。verifier が 2 回になったのは、
  main が「画面の下の帯＝メニューバー」と思い込んで実装と依頼を書いたため
- **次に同じ規模なら**: 画面の端に合わせる実装では、着手前に
  `position: fixed` の要素をすべて測ってから式を書く。verifier への依頼には
  「比べる相手」を要素名で固定せず、「画面の下に固定されたもの全部」と書く
