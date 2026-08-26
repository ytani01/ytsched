# TODO-061. スマホの幅で、ヘッダとフッタの表示が崩れるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort medium | main + verifier + wording |
| 消費 | output 48,445 / cache_creation 229,606 / 概算 $5.5 |
|      | main 91% + wording 5% + verifier 4%（料金の割合） |

## きっかけ

2026-08-26 に、利用者から「スマホでヘッダとフッタの表示に不具合」と
言われた。

**どの崩れを指しているのかを着手時に聞いたが、答えは得られなかった。**
幅 390px・360px で調べて分かっていた 3 つがどれも実際に出ていたので、
3 つとも直すことにした。実機（iOS / Android）でしか出ない崩れがあれば、
それは別の項目になる。

## やったこと

### 1. 横スクロールが出るのを止めた

`documentElement.scrollWidth` が `innerWidth` の 2 倍（390 に対して
780、360 に対して 720）だった。TODO-057 で置いた
`.my-week-panel.my-week-next` が画面の右隣（`left: 100%`）にあり、
はみ出した分がそのまま横スクロールになっていた。

`body` には `overflow-x: hidden` が入っていた（TODO-057）が、
`scrollWidth` は 2 倍のままで、本文だけが横へずれる状態は残っていた。

**`#week_wrap` を `.my-week-viewport` で包み、そちらで切るようにした。**
`#week_wrap` は指の追従で横へ動くので、切る側は動かない要素でないと、
追従中に隣の週まで切れてしまう。

```css
.my-week-viewport {
    overflow-x: clip;
}
```

**`hidden` ではなく `clip` にした。** `hidden` はスクロールの入れ物に
なるので縦も切られ、今週より背の高い隣の週が、追従中に下で切れて
見える。`clip` にはそれが無い。

`body` の `overflow-x: hidden` は要らなくなったので外した。

### 2. フッタの日付が重なるのを直した

`.my-home-date` は「年 / 月日 / 曜日」の 3 行を `<br>` で明示的に
出しているが、`font-size: xx-small`（10px）に対して
`line-height: 8px` と、文字より行が低かった。上下の行が重なる。

`line-height` を 10px にした。日付の高さは 24px → 30px、メニューバーは
42.5px → 46px になる。

### 3. ゲージの目盛りを読めるようにした

目盛り 14 個は、はみ出しも重なりも無いが、中央付近の
`-1w`・`+1w`・`+1m`・`+3m` が詰まって読めなかった（幅 360px で
`+1w` と `+1m` の隙間が 1.2px）。両端の `±30y` は画面の端に接していた。

**目盛りは 14 個のまま間引かない**（TODO-059 で増やしたばかりなので、
減らすかどうかは利用者に聞いて決めた）。代わりに、

- `.my-gage-label` を `x-small`（10px）/ `line-height: 12px` / `top: 9px`
  から、`8px` / `10px` / `top: 10px` に
- `.my-gage-bar` の左右のマージンを 12px → 16px

にした。字を小さくすると隣り合うラベルの隙間が広がり、マージンを
広げると両端が画面の端から離れる。

## テスト

playwright を直に動かし、`viewport` を 390x844 / 360x800、
`device_scale_factor` は既定のままにして測った。

| 見るところ | 直す前（390 / 360） | 直したあと |
|---|---|---|
| `scrollWidth` | 780 / 720 | 390 / 360（`innerWidth` と一致） |
| フッタの日付の高さ | 24px（行が重なる） | 30px（重ならない） |
| メニューバーの高さ | 42.5px | 46px |
| 目盛りの最小の隙間 | 1.2px（360px の `+1w`–`+1m`） | 6.32px / 4.45px |
| 両端のラベル | 左 6.3px（端に接する） | 左 12.2px / 右端まで 11.2px |

- `mise run lint` / `typecheck` / `test`（439 件）は通過。Python は
  触っていないので、テストの結果は変わらない
- **スワイプが壊れていないことを確かめた**（`overflow-x: clip` で隣の週
  まで切れないか）。`touchmove` で `#week_wrap` が
  `translateX(-200px)` と指に追従し、`.my-week-next` は `visible`、
  ドラッグ中も `scrollWidth` は 390 のまま、`touchend` で翌週へ遷移する
- console のエラー・警告は 0 件

## 気づいたこと

- **撮る条件でレイアウトの幅が変わる。** playwright の
  `device_scale_factor` を 2 にしたり `is_mobile` を立てたりすると、
  `width=device-width` が 780px と解釈され、実機と違う幅で組まれる。
  この違いで「ゲージが切れている」と一度読み違えた（項目を立てた日）
- **`overflow-x: hidden` と `clip` の違いは、この画面では実際に効く。**
  隣の週は今週より背が高いことがあり、`hidden` だと追従中に下が切れる
- **`.my-home-date` の 3 行は折り返しではなく `<br>` で明示している。**
  幅を広げても行数は変わらない
- **消費の数字には、TODO-062・TODO-063 を立てた分も入っている。**
  この項目の途中で 2 件を立てたので、コミットの時刻では切り分けられない
  （`tools/token-usage.py` は始点しか指定できない）
