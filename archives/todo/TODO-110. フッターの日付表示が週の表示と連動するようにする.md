# TODO-109. フッターの日付表示が週の表示と連動するようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort medium | main のみ |

## きっかけ

フッターの日付表示（`<input id="date" ...>` および `#cur_day`）が、スワイプや週切り替え（`setActiveWeek`）の際に同期せず古い日付のままになっていた。

## やったこと

- `src/ytsched/webroot/static/js/week.js` の `setActiveWeek()` 内で、フッターの隠しフィールド `#cur_day` も切り替えた週の月曜（`monday`）に更新されるように修正。

## テスト

- `mise run test`（ruff, basedpyright, mypy, eslint, pytest）を実行し、全 503 テストが合格することを確認。
