# TODO-061 verifier 報告

依頼書 `archives/agents/TODO-061/verifier-request.md` を読んで確認した。

## 1. mise run lint / typecheck / test

```
mise run lint       # ruff format: 25 files left unchanged / ruff check: All checks passed!
mise run typecheck  # basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success: no issues found in 22 source files
mise run test       # pytest: 439 passed in 3.40s
```

すべて OK。`upgradeproject` は走らせていない。

## 2. アプリの起動

`uv run ytsched webapp --port 8931 --datadir /tmp/tmp.jmYbhkHZ09` で起動。
`curl` で `/` に 200。取得した HTML に `{{` `{%` の生残りなし。終了後、
プロセスは kill、一時ディレクトリも削除済み。

## 3. playwright（`/usr/bin/chromium`、`viewport` 390x844 / 360x800、
   `device_scale_factor` は既定）

- **`scrollWidth` と `innerWidth` の一致**: 390px → 両方 390。
  360px → 両方 360（直す前は 780/720 だった）。○
- **フッタの日付（`.my-home-date`）**: 390px で
  `date top=806 bottom=836` / `menu_bar top=798 bottom=844` →
  日付の範囲がメニューバー内側に収まる。360px も同様
  （`762–792` が `754–800` の内側）。○
- **ゲージの目盛り 14 個**: 両方の幅で 14 個検出。隣接ラベルの最小隙間は
  390px で 6.32px、360px で 4.45px（どちらも 0 より大）。両端のラベルは
  390px で左 12.2px・右 11.2px、360px で左 12.2px・右 11.2px、画面端に
  接していない。○
- **スワイプ（`new Touch()`/`new TouchEvent()` を `window.dispatchEvent()`
  する方式。TODO-057 の verifier が使った手順に合わせた）**:
  `date=2026-08-26` から左へ 200px 分ゆっくり動かしたところ、
  - ドラッグ中に `#week_wrap` の `transform` が `translateX(-200px)` と
    指に追従する
  - `.my-week-next` の `visibility` が `visible`（隣週が見えている）
  - ドラッグ中も `document.documentElement.scrollWidth` は 390 のまま
    （`overflow-x: clip` で隣週まで切れて見えなくなってはいない）
  - `touchend` 後、`date=2026-08-31` へ正しく遷移
  いずれも OK。TODO-054・TODO-057 の挙動は壊れていない
- console のエラー・警告は 0 件。`webapp.log` にも例外・トレースバックなし

## 判断が要る点

とくに無し。依頼の 5 項目すべて確認でき、不具合は見つからなかった。
