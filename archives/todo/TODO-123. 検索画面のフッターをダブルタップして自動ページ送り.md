# TODO-123. 検索画面のフッターをダブルタップして自動ページ送り

|      | main | 担当 |
|------|------|------|
| 見込み | GPT-5 / effort medium | implementer + verifier |
| 実施 | GPT-5 / effort medium | implementer + verifier |

分担と各担当の報告は
[archives/agents/TODO-123](../agents/TODO-123/README.md) にある。

## きっかけ

検索画面のフッターの ＜ ＞ をダブルタップしても、自動ページ送りが始まらない。
検索画面は 1 回動くごとに画面を読み直すため、週表示用のタイマーは続かなかった。

## やったこと

- 検索画面のダブルタップ時刻と自動送りの方向を `sessionStorage` に保存し、
  再読み込み後も `AutoTurnMsec` 間隔で検索基準日を 7 日ずつ移動するようにした
- 同じボタンまたはフッター外の操作で保存した状態を消して、自動送りを止める
- 検索画面の移動は従来どおり `moveActiveDate()` を使い、週枠の
  アニメーションを出さない
- 前後の自動送り、同じボタンとフッター外での停止、非アニメーションを
  ブラウザテストで確認した

## テスト

- `uv run pytest tests/test_browser.py -k 'auto_page_turn_in_search_mode' -v` — 3 passed
- `uv run pytest tests/test_browser.py -k 'tap_outside_stops_auto_page_turn_without_week_slide_in_search_mode' -v` — 1 passed
- `npx eslint src/ytsched/webroot/static/js/main-page.js` — 成功
- `mise run test` — 整形・lint・型チェックは成功。pytest は実行開始後に
  実行環境の待機上限へ達したため、完了結果は取得できなかった

トークン集計は、Codex の会話記録に対応する Claude transcript が無いため実行できない。
