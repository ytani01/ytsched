# TODO-213 reviewer 報告

対象: `git diff`（main_handler.py、main-page.js、my.css、src/README.md、
tests/test_web.py）。main が直した `closest(".my-sde")` を含む。

実測の環境: 一時ディレクトリを `--datadir` にして `ytsched webapp` を
port 10199 で起動し、Python の playwright（chromium、800x900）から
POST と表示を行った。アニメーションは `document.getAnimations()` で
止めて時刻を指定し、画素と `getComputedStyle` を読んだ。

## 要修正

### 1. 予定の多い日では、日付の行の点滅がほとんど見えない（削除では点滅が事実上出ない）

- my.css:652-660、main-page.js:458（`#date-…` に class を付ける箇所）
- `.my-date-block` の背景（#EEE）は、左の日付欄（`.my-wday-N` の色）と
  予定の枠（`.my-sde-normal` などの白）にほぼ覆われている。点滅させて
  いるのはこの見えない背景
- 実測: 予定 5 件の日に `flash_date` だけを付けた（削除と同じ状態）。
  0ms で止めて `#date-2026-10-02` を撮ると、黄色 (255,235,59) の画素は
  **92,800 画素中 244（0.26%）**。予定の枠の角の隙間だけが黄色になる。
  枠の中心の画素は白のまま
- 予定の無い日（最後の 1 件を消したとき）は、予定欄の空き部分が黄色に
  なり、見える
- 要件「削除したときは日付の行だけ点滅させる」は、他の予定が残る日を
  消したときに目で分からない。追加・修正でも、日付の行は予定の行に
  隠れて点滅して見えない（予定の行の点滅は見える）

### 2. 消えている相で、元の背景色ではなく下の地の色が出る。終わりで色が跳ぶ

- my.css:657-659（`transparent` の keyframe）
- アニメーション中は要素自身の背景が `transparent` に置き換わるので、
  元の背景（`.my-sde-normal` の #FFF、`.my-sde-holiday` の #FAA、ToDo の
  #FFE/#FFC/#EEB、`.my-date-block` の #EEE）ではなく、下にあるものが
  透けて見える
- 実測（480ms = 16% で停止して中心の画素を読んだ）:
  - 点滅中の予定の行: 本来 #FFF のところが (208,216,223) = `--my-cal-ground`
    の #D0D8DF。日付の行も同時に透明なので、さらに下の地の色まで透ける
  - 予定の無い日の予定欄: 本来 #EEE のところが (208,216,223)
- 2999ms でも同じ (208,216,223)、3100ms（アニメーション終了後）で
  元の色に戻る。最後の 83%〜100% が透明のままなので、**3 秒の終わりに
  灰色から白へ一瞬で切り替わる**
- 点滅が「黄色 ⇔ 元の色」ではなく「黄色 ⇔ 灰色」に見え、休日・ToDo の
  色付きの行では元の色が一度も出ない。実害の大きさ（見た目の
  不自然さをどこまで許すか）は未確認

### 3. ページ内で週を 2 週以上離れて戻ると、点滅し直す

- main-page.js:464（`my-flash` を付けたまま外さない）、my.css:832-856
  （離れた週の `.my-week-panel` は `display: none`）
- CSS の仕様で、`display: none` から表示に戻った要素のアニメーションは
  最初から始まる。`week.js` の `layoutWeeks()` は今の週と隣の 2 週以外を
  `display: none` にするので、点滅させた週から 2 週以上ページ内で
  移って戻ると、もう一度 3 秒点滅する
- 実測: 点滅の終わった後に `animationstart`（`my-flash`）を数え、
  キーボードで → → ← ← と週を移った。**2 回発火した**（日付の行と
  予定の行）。URL のクエリは戻っていない（`?date=2026-09-28`）ので、
  クエリではなく class が残っていることが原因
- 同じ理由で、表示中でない週にある要素（期限切れの ToDo は今日の行にも
  出るので、`date` の週と今日の週が違うとき、もう一方の週の写し）は、
  その週へ移ったときに初めて点滅する。1 週だけ移る（隣の週になり
  `display: flow-root` のまま）場合は点滅し直さない

## 検討

### 4. JS の点滅にテストが無い

- `tests/test_browser.py`（playwright で chromium を動かすテスト、
  TODO-056）があるが、`flashUpdated` を見るテストは足されていない
- Python のテスト（tests/test_web.py の 4 本）はリダイレクトのクエリ
  だけを見る。main が直した `closest(".my-sde")`（内容欄でなく行全体に
  付ける）、`flash_*` を URL から消して `date` などを残すこと、上の 3 の
  点滅し直しは、どれを壊しても落ちるテストが無い

## 問題無し（1 行ずつ）

- `exec_cmd()` / `post()` の分岐: add・fix は (日付, 新しい sde_id)、
  del は日付だけ、update は編集画面の URL に flash を付けない、cmd 無し・
  不明な cmd は付けない。いずれも要件どおり。`date` / `sde_align` は
  そのまま
- fix で日付を移したとき: `flash_date` は移動先、`flash_sde_id` は次の版。
  移動元は付かない（テストあり、実測でも確認）
- ToDo: `flash_date` は `sde.date`（従来の `date` と同じ値）。ToDo は
  その日と今日の両方に出るが、`querySelectorAll` で両方に付く（実測）
- `history.replaceState(history.state, …)`: `onloadHdr` の
  `replaceDateInUrl` が入れた `{date}` を保ったまま `flash_*` だけ消す。
  読み込み後の URL は `?date=2026-10-02` で `date` は残る（実測）。
  リロード・戻る（popstate）で `flash_*` が戻ることは無い
- `load` を 2 つ登録: `onloadHdr` が先で同期的に終わり、`flashUpdated` は
  `onloadHdr` の早期 return（1 画面に収まるとき）の影響も受けない。問題無し
- テストの強さ（ソースを一時ディレクトリへ写して壊した）:
  `flash_date` の行を消す → 3 件落ちる。`flash_sde_id` の行を消す →
  2 件落ちる。fix で古い sde_id を返す → 2 件落ちる。del で
  `modified_sde_id` を返す → 落ちないが、del の `exec_update` は sde_id に
  None を返すので同じ挙動（テストの穴ではない）

## 作り込みすぎ

- main-page.js:445-468: shrink: `els` 配列に集めてから `forEach` する
  2 段構え。`getElementById(...)?.classList.add(...)` と
  `querySelectorAll(...).forEach((el) => el.closest(".my-sde")?.classList.add(...))`
  を直接書けば、配列と二重スプレッドが要らない（数行減）
- my.css:659: delete: `100% { background-color: transparent; }`。
  83% と同じ値で、書かなければ元の背景色へ戻る補間になる
  （上の 2 の「終わりで色が跳ぶ」もこの行による）

net: -5 lines possible.

## 再確認（指摘 1〜4 の修正後）

前回と同じやり方で測った（一時の datadir、chromium 800x900、
`getAnimations()` で止めて画素を読む）。データは implementer の
`measure_flash.py` と同じ 3 件（通常・休日・ToDo）。

- 1 日付の欄: 一致。0ms で日付の欄も予定の行も (255,235,59)
- 2 消えている相・終わり: 一致。480ms・2490ms・2999ms・終了後のどれも
  元の色。予定の行は #FFF / #FAA / #FFC（ToDo near）、日付の欄は曜日の色
  (#F0FFFF / #FFEEEE / #FFCCCC)。2999ms と終了後が同じ値なので、色は跳ばない
- 3 終わってから週を移る: 一致。→ → ← ← で `animationstart` は 0 回、
  `.my-flash` は 0 個
- 4 テストの強さ: 一致。写しで壊して確かめた。`closest(".my-sde")` を外す・
  `classList.remove` を外す・日付の欄でなく日付の行に付ける・
  `flash_date` を URL に残す、の 4 つとも 1 件ずつ落ちる

### 検討（新しく見つけたもの）

- main-page.js の `animationend` で外す仕組みは、**点滅の途中で週を
  2 週以上移ると効かない**。`display: none` で止まったアニメーションは
  `animationend` ではなく `animationcancel` になるので、class が残る。
  実測: 読み込みから 500ms で → → ← ← と移ると、`animationstart` が
  2 回起き（戻ったところで点滅し直す）、直後の `.my-flash` は 2 個。
  点滅し直すのはこの 1 回で、終われば外れる。表示中でない週にある
  ToDo の写しも同じで、その週を開いたときに点滅する。実害の大きさは未確認
- 色の跳びを直した my.css（`box-shadow` の内側の影）は、テストで守られて
  いない。前の `background-color` と `transparent` の keyframe に戻しても、
  足した 2 本は通る。画素を測るテストが要るかどうかは main の判断
