# TODO-084 implementer への依頼

フッターの ◀ ▶ をダブルタップして、自動ページ送りを始められるようにする。

`TODO.md` の TODO-084 の節を先に読むこと。**そこに書いてある仕様が優先**で、
この依頼書は決めごとを具体化したもの。

## 決めたこと（この通りに実装する）

### 1. `conf.json` の設定

- キー名は **`AutoTurnMsec`**、既定 **700**、範囲 **300〜10000**。
- 読み方は `LoadMonths` と同じで、`get_conf_arg()` を通さず読むだけ
  （利用者が手で書く値なので、`set_conf()` で消さない。TODO-069）。
- `MainHandler` に `get_load_months()` とほぼ同じメソッドが 2 つ並ぶことに
  なるので、**共通の `get_conf_int(key, default, min_value, max_value)` を
  1 つ作り、`get_load_months()` もそれを使う形に書き直す。**
  使われなくなる `str2load_months()` は消す（呼び出しは他に無い）。
  読めない値（数字にならない、範囲の外）で警告を 1 行出して既定値へ落とす
  挙動は、いまのまま変えない。
- 下限を 300 にしたのは、週送りのアニメーション（`week.js` の
  `SWIPE_SLIDE_MSEC` = 200 と、その後始末の +100）より短い間隔だと、
  `slideWeekWrap()` の呼び出しが重なって**送り先へ移らずに週が飛ばされる**
  ため。この理由をコードのコメントに残すこと。

### 2. ブラウザへの渡し方

`main.html` の先頭の `<script>`（`search_str0` / `today_str` がある所）に
`const auto_turn_msec = {{ auto_turn_msec }};` を足す。`MainHandler.get()` の
`render()` に `auto_turn_msec=...` を渡す。

### 3. ボタン

`main.html` の `#back_button` / `#forward_button` から `onmousedown` 属性を
やめ、`data-page-turn="-1"` / `data-page-turn="1"` を持たせる。
リスナーの登録とハンドラは **`main-page.js`** に置く（一覧画面だけのもの）。

- `pointerdown` で、押した位置と時刻を覚える。
- `pointerup` で決める。
  - 自動ページ送りが走っていれば、**止めるだけ**（週は送らない）。
  - 押した位置から 30px 以上動いていれば、**何もしない**
    （ボタンの上から始めた横の払いを、週送りとして拾わないため）。
  - それ以外は `moveToMonday(direction, url_prefix)` で 1 週送る。
    直前のタップが**同じボタンで 350msec 以内**なら、続けて自動ページ送りを
    始める（350 は `homeButtonHdr()` のダブルクリック判定と同じ値）。
- `pointercancel` で覚えた位置を捨てる。
- 自動ページ送りは `setInterval(..., auto_turn_msec)` で
  `moveToMonday(direction, url_prefix)` を繰り返す。
- 止まるのは次の 4 つ。
  - ページ送りボタンをもう一度タップした
  - 画面の他の場所をタップ・クリックした（`pointerdown` を capture で拾う。
    ボタンの上のものは上の分岐に任せるので、ここでは見送る）
  - キーを押した
  - 画面が隠れた（`visibilitychange` で `document.hidden`）
- 読み込んだ範囲の外へ出ると `moveToMonday()` が `doGet()` してページごと
  読み直すので、そこで自動的に止まる。これはコメントに書いておく。

### 4. `swipe.js`

ボタンが `onmousedown` を持たなくなり、`mouseUpHdr()` が呼び直す仕掛けを
通らなくなる。**ボタンの上から始めたスワイプを見送る**ようにする。

- `touchStartHdr()` の `el.closest("input, textarea, select")` に
  `[data-page-turn]` を足す。
- `mouseDownHdr()` の `el.closest("input, textarea, select, label, a")` にも
  足す（`stopPropagation()` / `preventDefault()` の前で返すこと。
  pointer イベントを邪魔しないため）。

### 5. 変えないもの

- 週切り替えのアニメーションの速さ（`SWIPE_SLIDE_MSEC`）。
- シングルタップで 1 週送る挙動。
- 他のボタン（ホーム・日付セル・スケジュール項目）の `onmousedown`。
  今回触るのは ◀ ▶ の 2 つだけ。

## テスト

### `tests/test_web.py`

`LoadMonths` のテスト（`test_load_months_*`）に倣って `AutoTurnMsec` の分を
足す。既定値、範囲の外、数字でない値、`conf.json` が書き換えられないこと。

### `tests/test_browser.py`

**既存のテストが落ちる。** `#forward_button` を続けてクリックしている所
（`test_week_move_reloads_outside_the_loaded_range` など）は、350msec 以内に
2 回目が入るとダブルタップになる。**クリックとクリックの間に 350msec を
超える待ちを入れて、理由をコメントに書くこと**（`page.wait_for_timeout()`）。
`#forward_button` / `#back_button` を叩いているテストを全部見ること。

足すテストは次の 3 つ。`conf.json` に `AutoTurnMsec` と、送る余地を作る
`LoadMonths` を書いてから開く（`write_conf` 相当の使い方は既存に倣う）。

1. ダブルタップで週が送られ続ける（入力を止めても週が変わる）
2. その次のタップで止まる（止めたあと、しばらく週が変わらない）
3. ボタンの上から横に払っても週が変わらない

## 前提

- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は叩かない。**
- アプリを起動して確かめるときは `--datadir` に一時ディレクトリを渡す。
- 文書（`src/README.md` など）は**このあと別の担当が書く**ので、
  **`.md` は触らない**。コード・テンプレート・テストだけを直す。

## 報告

`archives/agents/TODO-084/implementer-report.md` に、変えたファイルと、
判断が要った点、テストの結果を書く。返事は 5 行以内で、
「終わったか・報告ファイルのパス・判断が要る点」だけ。
