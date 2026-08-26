# TODO-059 verifier 報告

## 1. Python と JavaScript の突き合わせ

`math.log10` (Python) と `Math.log10` (Node v26.7.0) で、同じ式に
0, 1, 7, 30.4375, 365.25, 10957.5, 20000, -20000, -7 を入れて突き合わせた。
全て完全一致。

```
0 -> 0.0
1 -> 1.1850146288086407
7 -> 5.690184304434375
30.4375 -> 12.728351500011186
365.25 -> 27.979031134186897
10957.5 -> 50.0（= DAYS_GAGE_MAX、端）
20000 -> 50.0（端を超えても 50% で止まる）
-7 -> -5.690184304434375
-20000 -> -50.0
```

○ 一致。○ 端（±30y = 10957.5 日）とそれを超えた値で 50% に止まる。

## 2. mise run fmt / typecheck / lint / test

- `mise run fmt` ○ ruff format 25 files unchanged、ruff check All checks passed
- `mise run typecheck` ○ basedpyright 0 errors、mypy Success (22 files)
- `mise run lint` ○ 上記 2 つがまとめて通過
- `mise run test` ○ 439 passed

## 3. `1w` と `1m` のラベルの重なり

`mise run shot -- --width 412 --width 800 -p todo059` で撮影。
両幅とも `-30y -1y -1m -1w +1w +1m +1y +30y` の 8 ラベルが重ならず
並んでいるのを目視で確認。
保存先: `~/tmp/playwright-mcp/todo059_closed_412.png`,
`todo059_closed_800.png`

## 4. 針が週ごとに動くこと

`http://localhost:10085/ytsched/?date=2026-08-26`（今週）、
`?date=2026-09-02`（+1w）、`?date=2027-08-26`（+1y）で撮影。
針（▽）が、今週は中央、+1w は `+1w` ラベルの位置、+1y は `+1y`
ラベルの位置まで、それぞれ動いて見えることを確認した。
保存先: `todo059_now_closed_412.png`, `todo059_1w_closed_412.png`,
`todo059_1y_closed_412.png`

## 5. サーバログ

起動から終了まで、例外・トレースバックなし
（`start server: run forever ..` の INFO ログのみ）。

## 判断が要る点

なし。すべて期待通りの結果だった。
