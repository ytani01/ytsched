# TODO-061 verifier への依頼

スマホの幅（390px・360px）でヘッダとフッタの表示が崩れる件を直した。
**実際に確かめてほしい。コードは直さないこと**（見つけたことは報告に書く）。

## 直したもの

- `src/ytsched/webroot/templates/main.html`
  `#week_wrap` を `.my-week-viewport` で包んだ
- `src/ytsched/webroot/static/css/my.css`
  - `body` の `overflow-x: hidden` を外し、`.my-week-viewport` に
    `overflow-x: clip` を置いた
  - `.my-gage-bar` の左右のマージンを 12px → 16px
  - `.my-gage-label` を `x-small`(10px)/`line-height: 12px`/`top: 9px` →
    `8px`/`10px`/`top: 10px`
  - `.my-home-date` の `line-height` を 8px → 10px

## 確かめてほしいこと

1. **幅 390px・360px で `document.documentElement.scrollWidth` が
   `innerWidth` と一致すること。** 直す前は 2 倍（780 / 720）だった
2. **フッタの日付（`.my-home-date`）の 3 行が重ならず、メニューバーに
   収まっていること。** 上端・下端がメニューバーの内側にあること
3. **ヘッダのゲージの目盛り 14 個が、はみ出しも重なりも無いこと。**
   隣り合うラベルの隙間が 0 より大きいこと、両端の ±30y が画面の端に
   接していないこと
4. **左右のスワイプで週を送れること、追従中に隣の週が見えること
   （TODO-054・TODO-057 の挙動が壊れていないこと）。**
   `overflow-x: clip` で隣の週まで切れていないかが心配なところ。
   手順は `archives/agents/TODO-054/verifier-report.md` にある
   （CDP の `Input.dispatchTouchEvent`）
5. `mise run lint` / `typecheck` / `test` が通ること

## 確かめ方の注意

- アプリは `uv run ytsched webapp --port <空きポート> --datadir <一時ディレクトリ>`
  で起動する。**`~/ytsched/data` は使わない**
- **playwright は `viewport` に 390x844 / 360x800 を指定し、
  `device_scale_factor` は既定のままにする。** `device_scale_factor` を 2 に
  したり `is_mobile` を立てると `width=device-width` が 780px と解釈され、
  実機と違う幅で組まれる
- ブラウザは `/usr/bin/chromium`（`executable_path` に渡す）。
  `env -u DISPLAY` を付けて起動する
- playwright は `uv run --with playwright python ...` で使う
  （依存には入っていない）

## 報告

`archives/agents/TODO-061/verifier-report.md` に書くこと。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
