# TODO-111 reviewer 報告（再レビュー）

## 指摘

無し。

## 前回の指摘の確認

### 1. 検索表示での `onloadHdr()` の例外

解消済み。

`src/ytsched/webroot/static/js/main-page.js:119-121` は、通常表示では
`#header_date`、ヘッダーが無い検索表示では `#footer_date` を取得する。
テンプレート上ではフッターの日付入力欄が常に存在するため、後続の
`el_date.value` 参照は通常表示と検索表示のどちらでも有効である。

`tests/test_browser.py` の
`test_long_search_result_loads_without_javascript_error` は、20 日分の検索結果を
用意し、本文が画面以上の高さであることを明示的に確認している。これにより、
問題があった `body_h < win_h` の早期 return を通らない経路を確認できる。
さらに、ヘッダーが無いこと、フッターの日付、`pageerror` が無いことを確認して
おり、前回の問題に対するブラウザテストとして妥当である。

### 2. `src/README.md` の旧 ID

解消済み。

週移動の説明は `#header_date` と `#footer_date` に更新され、実装と一致している。

## 全体の確認結果

- `main.html` の日付入力欄は `header_date` / `footer_date` に分離され、ID の
  重複は解消されている。
- `setActiveWeek()` は存在する両入力欄と `#cur_day` を同じ月曜へ更新しており、
  URL、ゲージ、スクロール位置を更新する既存処理の順序も保っている。
- 通常表示の追加テストは、週切り替え後のヘッダー、フッター、`#cur_day` を
  直接確認している。
- 変更は日付入力欄の ID の分離、その参照と同期、対応する説明とブラウザテストに
  限られ、TODO-111 の範囲内である。
- `.agents/agents/`、`.codex/`、`AGENTS.md`、`package-lock.json` の変更は
  依頼どおりレビュー対象外とした。
- コードとテストは変更していない。
