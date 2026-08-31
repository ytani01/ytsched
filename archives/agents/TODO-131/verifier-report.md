# TODO-131 verifier 報告

## 1. git diff の範囲

○ `git diff` の変更は `src/ytsched/webroot/static/css/my.css` のみ、2 箇所。

- `.my-mini-cal-dot`: `width`/`height` を 5px → 6px
- `.my-mini-cal-sq`: `width`/`height` を 5px → 6px、
  `background-color: #28F` を `border: 1px solid #28F` に変更

依頼の記述どおり。

## 2. セルへの収まり

○ CSS 上、収まる。

- `.my-mini-cal-day` は `width: 24px; height: 24px; border: 1px solid #DDD`
  （my.css 1013-1019 行）。全称セレクタ `* { box-sizing: border-box; }`
  （my.css 49 行）が効くので、border 込みで 24px（内側の実効幅は
  24 - 2×1 = 22px）。
- `.my-mini-cal-marks` は `display: flex; gap: 1px`（my.css 1056-1062 行）。
- 印は最大 2 個（`has_sched` の dot、`has_todo` の sq。
  main.html 279-290 行）。6px + gap 1px + 6px = 13px で、
  実効幅 22px に収まる。
- `.my-mini-cal-sq` は `border: 1px solid` になったが、`box-sizing:
  border-box` により `width: 6px` は border 込みの外形なので、
  6px 四方のまま（内側の塗りは 4px 四方相当）。marks 内の占有幅は
  変わらない。

## 3. 背景色の回り込み

○ 問題なし。

`grep -n "my-mini-cal-sq\|my-mini-cal-dot" src/ytsched/webroot/static/css/my.css`
の結果、`.my-mini-cal-dot`（1064 行）、`.my-mini-cal-dot-important`
（1071 行）、`.my-mini-cal-sq`（1075 行）の 3 ルールのみで、
`.my-mini-cal-sq` に対する他の `background-color` 指定は無い。
`.my-mini-cal-day-*` 系の背景色ルール（1031-1046 行）は `<td>` 側の
クラスで、`.my-mini-cal-marks` の子要素である `.my-mini-cal-sq` には
継承・カスケードで直接乗らない（`background-color` は継承プロパティ
ではない）。意図しない背景色の回り込みは見当たらない。

## 4. lint / test

○ `mise run lint` — ruff format 38 files unchanged、ruff check All
  checks passed、eslint 完了、basedpyright 0 errors、
  mypy Success: no issues found in 35 source files。

○ `mise run test` — `uv run pytest tests`、553 passed in 129.42s。

```
mise run lint
mise run test
```

## 判断が要る点

なし。
