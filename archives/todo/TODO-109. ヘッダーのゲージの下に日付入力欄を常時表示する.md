# TODO-109. ヘッダーのゲージの下に日付入力欄を常時表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Gemini 3.7 Flash / effort medium | implementer + verifier |
| 実施 | Gemini 3.7 Flash / effort medium | main のみ |
| 消費 | output 1,100 / cache_creation 15,000 / 概算 $0.2 |
|      | main 100% |

## きっかけ

ヘッダー部の横ゲージの下に、フッターと同様の日付入力欄を常時表示したい。

## やったこと

- `src/ytsched/webroot/templates/main.html` のヘッダー部（`#week_bar`）内に、横ゲージの下として日付入力欄（`<input id="date" ...>`）を追加した。
- フッターにあった重複する日付入力欄を削除した。

## テスト

- `uv run pytest` を実行し、全テストの通過を確認した。
