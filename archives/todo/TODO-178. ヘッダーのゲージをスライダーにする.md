# TODO-178. ヘッダーのゲージをスライダーにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 89,950 / cache_creation 599,999 / 概算 $9.4 |
|      | main 67% + implementer 22% + verifier 6% + reviewer 5%（料金の割合） |

## きっかけ

ヘッダーの横ゲージ（TODO-058）は、タップした位置の週へ飛ぶだけで
（TODO-074）、針をつかんで動かすことはできなかった。スライダーに
したい、という利用者の要望。

着手前に「ドラッグ中に画面も追従させるか」を相談した。ゲージは中央
±30y を動くので、先読みの範囲の外まで追従させると、そのたびに
`doGet()` でページごと読み直されて `#gauge_r` が作り直され、
**ドラッグが途中で切れる**。そこで「動きが 1 秒止まったら追従する。
ただし移り先が DOM にある（先読み済みの）ときだけ」に決めた。

## やったこと

- **帯の上の操作を pointer イベントに寄せた。** それまでは
  `data-action="gauge-click"` を持ち、`swipe.js` の `mouseDownHdr()` /
  `mouseUpHdr()` が「動かずに離したらクリック」と判定していた。
  ドラッグを足すとこれが週送りのスワイプと二重に効くので、
  `main.html` から `data-action` を外し、`swipe.js` の見送りセレクタに
  `.my-gauge-bar` を足した。ハンドラ（`gaugeBarPointerDownHdr` など
  4 つ）は `gauge.js` に置き、window への委譲で拾う。ページ送りボタン
  （TODO-084）と同じ枠組みで、`setPointerCapture()` は使わない
- **ドラッグ中は針とラベルだけを動かす。** `.my-gauge-r` の
  `transition`（0.3s）が効くと指に遅れて付いてくるので、ドラッグの間は
  `my-gauge-r-no-transition` を付けたままにする。追従で
  `setActiveWeek()` を通ると `dispGauge()` が針を動かしてしまうため、
  ドラッグ中の `dispGauge()` は `sessionStorage` への記録だけして返す
- **1 秒のタイマーは `pointerdown` と `pointermove` の両方で張り直す。**
  `pointermove` だけだと、押したまま一度も動かさなければ永久に追従
  しない（Playwright の `page.mouse.down()` も `pointermove` を作らない）
- **追従してよいかは、移り先が DOM にあるかで決める。** 週間表示は
  `weekOffsetOfDate()`、月間表示は `month.js` に足した
  `hasBlockOfDate()`。パネルを探す部分は `blockPanelOf()` として
  `setActiveBlockOfDate()` と共有した（`week.js` の `weekPanelOf()` と
  同じ形）
- **履歴は、ドラッグ 1 回につき 1 つだけ積む。** 最初の追従で push、
  それ以降の追従と指を離したときは replace。追従を常に replace に
  すると、始めた週の履歴を潰してしまい、戻ったときに元の画面へ
  帰れない
- **帯を 33px から 44px にした。** 広げたぶんを下に空けると目盛りが
  指で隠れて読めないので、中身（軸・今週のしるし・針・目盛り）は
  下詰めにして、空きを上に置いた。ずらす幅は `--my-gauge-shift: 12px`
  にまとめ、各要素の `top` を `calc()` で出す。タッチで縦スクロールに
  取られないよう `touch-action: none` も付けた

## テスト

- `tests/test_browser.py` に 4 件足した。ドラッグ中は画面が動かず針と
  ラベルだけ動くこと、1 秒止まると先読み済みの週へ移ること、
  ドラッグ 1 回で履歴が 1 つしか増えないこと、動かさずに離したときは
  いままでどおり移ること
- `mise run lint`（ruff / basedpyright / mypy / Prettier / ESLint）と
  `uv run pytest` 670 件が通過
- verifier が playwright で実測した: 先読みの範囲外（+1.1m 相当）では
  1.5 秒待っても追従せず、離したときだけ移る。月間表示でも追従する。
  検索モードでは帯ごと消え、console エラーは 0 件。帯の高さ 44px と
  `body` の `padding-top` 52px が一致し、針の縦位置は週を変えても
  動かない

## 振り返り

- **implementer（Haiku 4.5）が、落ちるテストを 3 件残したまま
  「verifier に診断してほしい」と上げてきた。** 原因は main が調べた
  （タイマーを `pointermove` でしか張っていない実装の抜けと、10px
  動かしたのに移り先を「+7 日の週」と期待していたテストの誤り）。
  ゲージの対数目盛りのように、座標と意味の対応が素直でないところは、
  上位のモデルを充てるか、期待値の出し方まで指示に書いたほうがよい
- **reviewer は 5 点を指摘し、うち 4 点を直した。** 残る 1 点
  （履歴を push する瞬間）は、設計を書いた `README.md` のほうが古い
  ままだったので、実装に合わせて設計の文を直した。挙動が変わる項目に
  reviewer を入れる判断（TODO-017）は、ここでも効いた
- **JavaScript の整形とリント（`mise run fmtjs` / `lintjs`）を、
  最初の依頼で書き落とした。** ruff しか走らせておらず、Prettier が
  直すはずの長い行が残っていた。JS を触る項目では `mise run lint` を
  完了条件に書くこと

分担の理由と各担当の報告は
[../agents/TODO-178/README.md](../agents/TODO-178/README.md) にある。
