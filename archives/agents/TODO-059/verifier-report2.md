# TODO-059 verifier 報告（2 回目・最終形）

## 1. Python と JavaScript の突き合わせ

`days2x_percent()` / `days2xPercent()` を同じ定数（`DAYS_YEAR`,
`DAYS_MONTH`, `DAYS_GAGE_MAX`, `DAYS_GAGE_K=10.0`）で python3 と node に
それぞれ実装し、同じ入力（0, 1, 7, 30.4375, 365.25, 10957.5, 20000,
-1, -7, -365.25, -99999）を与えて比較した。

- ○ 全 11 件、両者の出力は完全一致（浮動小数点数の桁まで同一）
- ○ `days=0` → 0（Python: `0.0`、JS: `0`）
- ○ 端の 10957.5（=30y）と、それを超える 20000／-99999 は、両者とも
  ±50.0 に張り付く

## 2. `DAYS_GAGE_K` の一致

- `src/ytsched/main_handler.py` 83 行: `DAYS_GAGE_K = 10.0`
- `src/ytsched/webroot/static/js/my.js` 25 行: `const DAYS_GAGE_K = 10.0;`
- ○ 一致

## 3. `mise run fmt` / `typecheck` / `lint` / `test`

```
mise run fmt        → ruff format 25 files left unchanged / ruff check All checks passed!
mise run typecheck   → basedpyright 0 errors, mypy Success (22 files)
mise run lint         → 上記2つ、Finished in 5.34s
mise run test          → 439 passed in 3.20s
```

- ○ すべて通った

## 4. 14 個のラベルの重なり（キャプチャ）

```
env -u DISPLAY mise run shot -- "http://localhost:10085/ytsched/?date=2026-09-02" \
  --width 360 --width 412 --width 800 -p todo059-2
```

- **× 360px で `+1w` と `+1m` のラベルが接触している。**
  見込みは「余白 1.1px」だったが、実際にはズームして見ても隙間が
  無く、`+1w+1m` と 1 語のように見える
  （`/home/ytani/tmp/playwright-mcp/todo059-2_closed_360.png`）
- ○ 412px・800px では `+1w` と `+1m` の間、他の隣接ラベルの間にも
  はっきり隙間が見える
  （`todo059-2_closed_412.png`, `todo059-2_closed_800.png`）
- ○ 360px・412px・800px とも、それ以外の 13 箇所の隣接ラベル間は
  重なっていない

## 5. 針が週ごとに動くこと

`http://localhost:10085/ytsched/?date=YYYY-MM-DD`（ISO 形式）で
今週・+1w・+1y の 3 つを 412px でキャプチャして比較した。

- ○ 今週（`2026-08-26`）: 針は `-1w` と `+1w` の中間（中央）
- ○ +1w（`2026-09-02`）: 針が `+1w` の位置まで右へ移動
- ○ +1y（`2027-08-26`）: 針が `+1y` の位置まで右へ移動

いずれも位置が変わることを確認した。

## 6. 端（±30y）と、それを超えた日数で 50% に止まること

1 の突き合わせで、10957.5（=30y）と、それを超える 20000／-99999 の
両方が ±50.0 で頭打ちになることを確認済み（Python・JS とも）。

## サーバのログ

`uv run ytsched webapp --datadir <一時ディレクトリ> -p 10085` の標準出力・
標準エラーに、例外やトレースバックは出ていない（`grep -iE
"traceback|exception|error"` でヒットなし）。

## 見つかった不具合

- **360px で `+1w` と `+1m` のラベルが接触して見える。**
  見込み（余白 1.1px）とは合っていない。0px を割っているかまでは
  ピクセル単位で測っていないが、目視では隙間が確認できない。
  該当: `src/ytsched/main_handler.py` の `GAGE` 一覧・`days2x_percent()`、
  `src/ytsched/webroot/static/js/my.js` の同名関数
