# TODO-054 reviewer への依頼

左右のスワイプで週を送る機能を入れた（TODO-054）。**良いかどうか**を
見てほしい。動くかどうか（起動確認・テスト実行）は verifier に任せて
あるので、やらなくてよい。

## 変更したもの

- `src/ytsched/webroot/static/js/my.js` — 末尾にスワイプの処理を追加
  （`touchStartHdr` / `touchMoveHdr` / `touchEndHdr` / `touchCancelHdr`）
- `src/ytsched/webroot/templates/main.html` — 上の 4 つを `window` に登録

`git diff` で見られる。項目の背景は `TODO.md` の TODO-054 の節にある。

## 見てほしいところ

- **判定の条件が妥当か。** 距離 60px、横が縦の 1.5 倍、800ms 以内、
  画面端 30px を除く、という決め方。取りこぼしと誤検出のどちらに
  倒れているか
- **状態（`swipeStart`）の持ち方に穴が無いか。** 指が増えたとき、
  `touchcancel` が来たとき、ページを離れるとき
- **既存のコードとの整合。** `my.js` の書き方（コメント、命名、
  `TODO-NNN` の参照の付け方）、`keyHdr` を `main.html` でだけ登録して
  いるのと揃っているか
- **iOS Safari の画面端スワイプと縦スクロールの切り分け**が、意図した
  形になっているか
- 週を送る先が正しいか（左へ払う＝次の週、で違和感が無いか）

## 報告

`archives/agents/TODO-054/reviewer-report.md` に書く。返事は 5 行以内で
「終わったか・報告ファイルのパス・判断が要る点」だけ。

**コードは直さない。** 確信度の高い指摘に絞る。
