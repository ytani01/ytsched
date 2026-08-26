# TODO-055 reviewer 報告

`git diff`（未コミットの作業ツリー）を対象に見た。実行は行わず、コードと
テストを読んで確かめた。

## 確信度の高い指摘

無し。

- `calc_week_diff()` は、どちらも月曜へ丸めてから引き算しているので、
  `(monday - this_monday).days` は必ず 7 の倍数になる。負の週・年またぎ
  でも `// 7` に余りが出ないので、丸め方向で誤ることはない。
  `test_calc_week_diff` も同じ週（月曜・日曜の両端）・翌週・3 週後・
  前の週の 4 パターンを見ており、`monday` を戻す・`// 7` を `/ 7` に
  戻す・丸め処理を削るのいずれで壊しても落ちる作りになっている
- `body` の `padding-top` は `body_h` を測る行（line 58）より前
  （line 55）に入れており、要件どおり。検索モードでは `week_bar` 要素が
  無いので `if (elWeekBar)` で弾かれ、`padding-top` は既定の 0 のまま
  になる。`followKeyboard()` は `.my-follow-keyboard` が付いた要素だけを
  動かす関数で、`week_bar` にはそのクラスが無いので、ソフトキーボード
  追従とは干渉しない
- `.fixed-top` の `z-index: 1030` は、既存の `.fixed-bottom` と同じ値。
  日付欄の `onmousedown` の分岐（`search_mode` で `doPost`／通常時で
  `doGet('.../edit/', ...)`）は、既存の「＋」ボタン
  （`main.html` 353 行目付近）と同じパターンを踏襲しており、
  `sde_id: ''` を渡したときの挙動（`EditHandler.get()` の
  `if not sde_id:` で新規追加扱いになる）も確認済み
- `TestWeekBar` / `TestDateColumn` は、テンプレートの該当箇所を
  読んで確かめた限り、実装を差し戻すとそれぞれ意味のある形で失敗する
  作り（帯が消える → `bar is not None` で落ちる、`doGet` に戻さない
  → `"doGet(" in onmousedown` で落ちる、等）になっている

プロジェクトの決まり（`src/README.md` の autoescape の記述、
`CLAUDE.md`）からの逸脱も見当たらない。

## 気になった点（確信度は低い）

- **ゲージの中心位置がずれる可能性。** `onloadHdr()` の `centerY` は
  `document.documentElement.clientHeight` から求めており、新設した
  `week_bar`（`position: fixed`、`z-index: 1030`）が上に重なって隠す
  実際の表示領域の分だけ短くなったことを踏まえていない。ゲージの目盛り
  （`GAGE`、`-30y`〜`+30y`）は対数目盛りで両端が画面の上下端に寄る設計
  なので、`-30y` 側が帯の高さぶん余分に隠れる、あるいは中心が数十px
  ずれる可能性がある。ただし、下端側も従来からメニューバー
  （`.my-menu-bar` の `z-index: 200`）に極端な目盛りが隠れる前提の
  設計に見え、同じ考え方の延長とも取れる。実機で確かめていないので
  確信は無い（verifier の確認事項にも入っていない）
