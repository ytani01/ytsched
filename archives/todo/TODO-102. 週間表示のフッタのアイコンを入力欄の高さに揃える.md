# TODO-102. 週間表示のフッタのアイコンを入力欄の高さに揃える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier + wording |
| 実施 | Opus 5 / effort medium | main のみ + verifier + wording |
| 消費 | output 12,328 / cache_creation 130,398 / 概算 $2.1 |
|      | main 73% + verifier 22% + wording 5%（料金の割合） |

分担は [archives/agents/TODO-102/](../agents/TODO-102/) にある。

## きっかけ

週間表示のフッタは、アイコンだけが一回り小さく、並んでいる入力欄より
下側が浮いて見えていた。幅 412px で測った高さは次のとおり。

| 要素 | 高さ |
|------|------|
| 検索欄・フィルタ欄の入力欄 | 25.5px |
| 日付の入力欄（`type=date`） | 28px |
| ToDo 日数の `select` | 21px |
| アイコン（`my-icon-lg` = 1.25em） | 20px |

揃える先は、利用者に確認して検索欄・フィルタ欄の 25.5px にした。
対象はフッタのアイコン全部。編集画面（`edit.html`）のフッタは
対象外。

## やったこと

- `my.css`: `.my-icon-xl`（1.6em = 25.6px）を足した。`.my-icon-lg`
  （1.25em）と `.my-icon-2x`（2em）の間に置いてある。
- `main.html`: `<footer>` の中の `my-icon-lg` を `my-icon-xl` に
  差し替えた（8 か所。bars・chevron-left・chevron-right・home・
  list・filter・search・backspace）。`<footer>` の外にある 2 か所は
  そのまま。
- ホームボタンだけは、隣に日付表示（`.my-home-date`。xx-small を
  `line-height: 10px` で 3 行、30px）が並んでいて、そちらのほうが
  背が高い。着手後に利用者から指摘があり、`.my-icon-home`
  （1.875em = 30px）を足して日付表示と同じ高さにした。

## テスト

- `mise run lint`・`mise run typecheck`: 緑。
- `uv run pytest`: 481 passed。
- 一時 datadir でアプリを起動し、幅 412px で playwright から各要素の
  高さを測った。フッタのアイコンは 20px から 25.59px になり、検索欄・
  フィルタ欄（25.5px）と揃った。ホームボタンのアイコンは 30px で、
  隣の `.my-home-date`（30px）と一致。
- `<footer>` の外のアイコンが 20px のままであること、`edit.html` が
  変わっていないこと、フッタが 2 段とも折り返したりはみ出したり
  していないことを確認した。
