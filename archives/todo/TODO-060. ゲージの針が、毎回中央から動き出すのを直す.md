# TODO-060. ゲージの針が、毎回中央から動き出すのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort medium | main + verifier + wording |
| 消費 | output 12,310 / cache_creation 101,459 / 概算 $2.4 |
|      | main 85% + verifier 8% + wording 7%（料金の割合） |

## きっかけ

TODO-059 を済ませたあと、利用者が見つけた（2026-08-26）。
**ページが切り替わるたびに、針がいったん中央に出てから所定の位置へ
動く。** TODO-059 とは関係なく、前からあった症状。

TODO-049 で入れた「前に見ていた週の位置から、今の週へ動かして見せる」
動きが、実際には効いていなかったことになる。

## やったこと

原因は 2 つあった。どちらも
`src/ytsched/webroot/static/js/my.js` の中。

### 1. レイアウトを確定させる 1 行が効いていなかった

`placeGageWithoutTransition()` は、`transition: none` を付けてから
位置を入れ、レイアウトを確定させてから `transition` を戻す、という
順で書いてあった。その「確定させる」1 行がこれだった。

```js
void elGageR0.offsetHeight; // 強制的にレイアウトを確定させる
```

**針は `<svg id="gage_r">` で、実体は `SVGSVGElement`。`offsetHeight`
は `HTMLElement` のものなので、SVG 要素には無い。** ブラウザで
`'offsetHeight' in el` が `false` になることを確かめた。読んでも
`undefined` が返るだけで、レイアウトは確定しない。

位置が反映されないまま `transition` が戻るので、CSS の初期値
（`left: 50%`、つまり中央）を起点に補間が始まっていた。

`getBoundingClientRect()` は SVG でも効くので、そちらに変えた。

### 2. 前の週が無いとき・同じ週のときも中央から動いていた

`dispGage()` の最後は `setGagePosition()` を直に呼んでいた。このとき
針の `left` は CSS の `50%` のままなので、transition が中央から掛かる。

**同じ週のまま読み直す経路（予定を編集して戻る、ホームを押す、その週の
別の日を開く）はすべてここを通る**ので、目につくのはこちらだった。

動かす先が無いのだから、`placeGageWithoutTransition()` で置けばよい。

## テスト

playwright で毎フレーム `getComputedStyle(el).left` を読み、中央
（幅 412px なら 190px）を通るかどうかを見た。スクリプトは
`archives/agents/TODO-060/probe.py` に置いてある。

| 経路 | 直す前 | 直したあと |
|---|---|---|
| 初回（`sessionStorage` が空） | 190px → 288px へ補間 | いきなり 288px |
| 同じ週をもう一度 | 190px → 288px へ補間 | いきなり 288px |
| 隣の週へ | 190px → 288px へ補間 | 288.3px（前の週）→ 288.7px |
| 今週 → +1y | — | 190px（前の週＝今週）→ 288px |

いちばん下は正しい。前の週が今週なら、中央が出発点で合っている。

- `mise run fmt` / `typecheck` / `lint` / `test`（439 件）は通過。
  Python は触っていないので、テストの結果は変わらない
- 検索モードでは週バーごと帯が出ず `gage_r` が無いが、`dispGage()` の
  先頭で見ているので例外は出ない（verifier が確かめた）

## 気づいたこと

- **`offsetHeight` は `my.js:449` `:451`、`main.html:47` `:55`、
  `edit.html:87` でも使っているが、そちらは `<div>` などなので効いて
  いる。** まとめて置き換えないこと
- **JavaScript の退行は今のテストでは捕まらない**（`pytest` は
  `my.js` を実行しない）。TODO-056 で扱う。この項目の `probe.py` は、
  そこで書くテストの材料になる
