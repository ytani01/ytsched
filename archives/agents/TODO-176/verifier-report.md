# TODO-176 検証報告（verifier）

## 結論

問題なし。`fmt` / `lint` 通過。週間・月間とも、表は白のまま周囲にグレーが敷かれ、
レイアウトの崩れ・テンプレートの生残り・サーバ例外はいずれも無し。

## 1. fmt / lint

- `mise run fmt` → ○ ruff format「43 files left unchanged」、ruff check「All checks passed」
- `mise run lint` → ○ basedpyright 0 errors、mypy「no issues found in 40 source files」、eslint 通過
- `git diff` は `src/ytsched/webroot/static/css/my.css` のみ（CSS 4 か所）

## 2. アプリ起動と見え方

- 起動: `uv run ytsched webapp --datadir <一時dir> --port 10085`（バックグラウンド）
- HTTP: 週間 `/ytsched/` → 200、月間 `/ytsched/?view=month` → 200
- テンプレート生残り: 両画面とも `{{` `{%` の grep 一致 0 件
- サーバログ: error / traceback / exception 無し
  （`ToDo_Days='1y'` の WARNING はサンプルデータ由来で本件と無関係）
- スクショ: `tools/screenshot.py` を 412px / 800px で撮影
  - `/tmp/claude-649/-home-ytani-work-ytsched/8754c5df-fd2a-4202-a316-1d6554e581e5/scratchpad/shots/week_closed_412.png`
  - `.../week_closed_800.png`
  - `.../month_closed_412.png`
  - `.../month_closed_800.png`

### 週間表示（ミニカレンダー 2 枚）

- ○ 2 枚の周り・間・下に薄いグレー (#F0F0F0) が見える（`.my-mini-cal-row` 全幅）
- ○ キャプション帯「YYYY/MM」・曜日見出し行「月火水木金土日」・日セル・当月外の日は
  すべて白。グレーの透けなし（CSS 上も `.my-mini-cal-wday` `.my-mini-cal-day-out` は
  背景指定なしで表の #FFF を継承、`.my-mini-cal-day` は明示的に #FFF）
- ○ 崩れなし。表の欠け・はみ出し・枠の二重化なし

### 月間表示（6 か月・2 列）

- ○ パネル全体（月見出し＋グリッド）にグレーが敷かれ、6 枚が白いカードに見える。
  表の周り・間・下にグレーが見える
- ○ 白い部分（見出し行・日セル・当月外の日）にグレーの透けなし
- ○ 崩れなし

## 3. main が挙げた点への所見

- **800px での寄り**: 指摘のとおり。`.my-mini-cal` の `max-width: 200px` により、
  週間ではグレー帯の中央に 2 枚が寄って左右に広いグレーの余白、月間では各列の表が
  左寄せになり左右列の間にも広いグレーの隙間ができる。412px ではほぼ気にならない。
  レイアウトの崩れではない。広い画面ではグレー面積が大きく、やや間延びして見えるが、
  「カードを浮かせる」意図からは外れていない。許容範囲と判断。
- **色差**: `#F0F0F0` と `#FFF` の差は小さく、特に月間表示（`.my-month-panel` 全体が
  グレー）では 800px でグレーがほぼ視認できないほど薄い。412px なら列右側の余白で
  かろうじて分かる。TODO で色は指定済みなので意図どおり。より浮かせたいなら
  `#EAEAEA` 程度まで濃くする余地あり（判断は main）。

## その他気づいた点

- `.my-mini-cal` は `border-collapse: collapse` のため `border-radius: 0 0 6px 6px` が
  Chromium では効かず、表下端の角丸は視認できない。キャプション側の上角丸は効いている。
  実害なし（TODO-135 に同種の記述あり）。

---

## 追加変更の確認（main.html の `<main>` インラインスタイル追加ぶん）

対象: `git diff` の 2 ファイル。
- `my.css`: `.my-mini-cal-row` / `.my-mini-cal` / `.my-mini-cal-caption` に色・角丸、
  新規 `.my-month-panel { background-color:#F0F0F0; padding-bottom:8px; }`
- `main.html` 8 行目: `<main>` の `background-color:#FFF` → `#F0F0F0`

### 1. fmt / lint

- `mise run fmt` → ○ ruff format「43 files left unchanged」、ruff check「All checks passed」、
  prettier 変更なし
- `mise run lint` → ○ basedpyright 0 errors、mypy「no issues found in 40 source files」、
  eslint 通過

### 2. 起動と見え方

- 起動: `nohup uv run ytsched webapp --datadir <一時dir> --port 10088`
  （ポート 10087 に前セッションの残プロセスが居たので kill してから 10088 で起動）
- HTTP: 週間 `/ytsched/` → 200、月間 `/ytsched/?view=month` → 200
- サーバログ: error / traceback 無し（`ToDo_Days='1y'` WARNING はサンプルデータ由来、無関係）
- スクショ（`tools/screenshot.py --full-page`、~/tmp/playwright-mcp/）:
  - `t176_week_closed_412.png` / `t176_week_closed_800.png`
  - `t176_month_closed_412.png` / `t176_month_closed_800.png`
  - `t176_wkprev_closed_412.png`（2026-08-28 週） / `t176_wknext_closed_412.png`（2026-09-11 週）

週間表示:
- ○ 週バーの下からフッターまで白い無地の帯が無く、全面グレー(#F0F0F0)。
  ミニカレンダー 2 枚より下・フッターとの間もグレーで、ミニカレンダー行の
  グレーと地続き。以前あった白帯は消えている（412 / 800 とも）
- ○ ミニカレンダーの表（キャプション帯・曜日見出し行・日セル・当月外の日）は白のまま
- △ 日付ブロック `.my-date-block`(#EEE) は、地の #F0F0F0 との差がごく僅かになり
  塗りではほぼ見分けられない。ただし `border: 2px solid #888` があるので行の区切りは
  読める。月見出し行 `.my-month-header`(#CCC) は従来どおり視認できる。崩れは無し
- ○ 崩れ無し

月間表示:
- ○ 6 枚のカレンダーより下・フッターとの間がグレー。`.my-month-panel` のグレーと地続き。
  800px では従来ここが広い白面だったのがグレーになった
- ○ 表は白のまま、崩れ無し

週送り:
- `.my-week-panel` は CSS に `background-color` 指定が無く透明。従来は地が白、今回は
  地が #F0F0F0。current / near いずれのパネルも透明なので、スライド中に白い矩形が
  出る経路は無い
- 前後週の静止スクショ（wkprev / wknext）を見比べ: いずれも週バー〜フッターまで
  グレーで一様。パネル外に白抜けや隙間は見当たらない
- ○ 問題なし

### 3. 所見（`#EAEAEA` 前後まで濃くした場合）

グレーを濃くしたとき見づらくなり得るのは 1 要素:
- `.my-date-block`（週間表示の 1 日ぶんの行、塗り #EEE）。地が #EAEAEA になると
  塗りの差はほぼ 0。ただし #888 の 2px ボーダーで囲まれているので行としては
  読める。気になるなら塗りを #FFF に上げるか、そのままボーダー頼みにするか

影響を受けない要素:
- ミニカレンダーの表・日セル(#FFF)・当月外の日（`.my-mini-cal-day` の #FFF 継承）・
  キャプション(#FFF)・`.my-mini-cal-caption-btn`(#EEE、白いキャプション内)・
  `.my-mini-cal-day-out`（色のみ、白セル上）は、いずれも白カードの内側なので
  地を濃くすると白カードのコントラストはむしろ上がる
- `.my-month-header`(#CCC) は元々地より濃いので問題なし

なお色を変えるときは #F0F0F0 を 4 か所（`.my-mini-cal-row` / `.my-month-panel` /
`main.html` の `<main>` インラインスタイル）そろって直す必要がある。
`<main>` だけリテラルが CSS の外（テンプレート）にあるので直し漏れに注意。

### まとめ

- fmt / lint 通過。週間・月間・週送りいずれも白帯が消えてグレーに統一され、表は白のまま、
  崩れ・例外・テンプレート生残り無し。
- main の判断が要る点: (a) グレーを #EAEAEA 前後まで濃くするか（利用者の
  「白い部分もグレーに」に照らすと #F0F0F0 は 800px でほぼ見えない）。
  濃くするなら `.my-date-block` の塗りをどうするかも合わせて。
  (b) 色リテラルが 3 ファイル 4 か所に分散している点（今後 CSS 変数へ寄せるか）。

---

## 最終確認

対象: `git diff` の 3 ファイル（`my.css` / `main-page.js` / `main.html`）。
`--my-cal-ground: #E8E8E8` を新設し、`#main`・`.my-mini-cal-row`・
`.my-month-panel` に適用。`.my-mini-cal` / `.my-mini-cal-caption` を明示 `#FFF`。
`main.html` の `<main>` インラインから `background-color:#FFF` を削除。
`main-page.js` `onloadHdr()` の `body_h < win_h` 分岐で `#main` の
`min-height` を「画面の高さちょうど」に伸ばす 1 行を追加。

### 1. fmt / lint

- `mise run fmt` → ○ ruff format「43 files left unchanged」、ruff check「All checks passed」、
  prettier 変更なし
- `mise run lint` → ○ basedpyright「0 errors」、mypy「no issues found in 40 source files」、
  eslint 通過

### 2. アプリ起動

- `uv run ytsched webapp --datadir <一時dir> --port 10176`（バックグラウンド）
- HTTP: 週間 `/ytsched/` 200、月間 `/ytsched/?view=month` 200、
  イベント入り週間 200、`?date=` 前後週 200
- テンプレート生残り: 週間・月間とも `{{` `{%` の grep 一致 0 件
- サーバログ: error / traceback / exception なし（`ToDo_Days` WARNING は無関係）

### (a) 週間表示のスクロール位置（最重要）— 退行なし

- 空データの週間 `/ytsched/`（今日 = 2026-09-04 金、週頭 = 08-31 月）:
  週バーの直下に「31 (Mon)」が出て、月〜木（今日より前）がすべて見えている。
  今日「04 (Fri)」は青枠付きで画面中ほど。上寄せで前の日が隠れる現象なし。
  スクショ: `~/tmp/playwright-mcp/t176f_week_empty_closed_412.png` /
  `t176f_week_empty_closed_800.png`
- 各日 6 件の予定を一時 datadir に置いて縦長にした週間: 従来どおり
  今日「04 (Fri)」が週バー直下付近へスクロールされる（直前の「03」が少しだけ覗く）。
  スクショ: `t176f_week_full_closed_412.png` / `t176f_week_full_closed_800.png`
- コード確認: 追加行は `body_h < win_h` 分岐内、`return` の手前。
  `fill_h = elMain.offsetHeight + win_h - body_h` で body 高さが
  ちょうど win_h になり、新たなスクロールバーは出ない。scrollToDate は
  この分岐では元々呼ばれず、スクロール挙動は不変。

### (b) 白帯 — 消えている

- 週間（空・イベント入り・前後週いずれも）: 週バー下からフッターまで
  無地の白帯なし、地の色 `#E8E8E8` で一様。ミニカレンダー 2 枚より下・
  フッターとの間もグレー。
- 月間 `/ytsched/?view=month`: 6 枚のカードより下・フッターとの間もグレー。
  スクショ: `t176f_month_empty_closed_412.png` / `t176f_month_empty_closed_800.png`
- ミニカレンダーの表（キャプション帯・曜日見出し行・日セル・当月外の日）は
  白のまま。グレーの透けなし。
- 週間の日付ブロック `.my-date-block`(#EEE) は #E8E8E8 の上でわずかに明るい
  カードに見え、#888 ボーダーで行の区切りが読める。崩れなし。
- 月間の 6 枚は白いカード、崩れなし。

### (c) 週送り — 問題なし

- `?date=2026-08-28`（前週）/ `?date=2026-09-11`（次週）の静止スクショを
  見比べ: どちらも週バー〜フッターまでグレーで一様、白抜けや隙間なし。
  スクショ: `t176f_wkprev_closed_412.png` / `t176f_wknext_closed_412.png`
- `.my-week-panel` は背景指定なし（透明）。地がグレーになったので、
  スライド中に白い矩形が出る経路はない（前回までの所見と同じ）。
- ミッドトランジションの動画的確認は screenshot.py では撮れないため、
  静止 2 枚＋CSS 上の確認にとどまる。

### その他

- 800px では `.my-mini-cal` の `max-width: 200px` で週間のミニカレンダー 2 枚が
  中央に寄り、左右に広いグレー余白。月間も各列の表が左寄せでグレー面積が広い。
  #E8E8E8 にしてグレーがはっきり見えるぶん目立つが、レイアウトの崩れではない
  （前回まで「許容」と確認済み。今回も崩れなしを再確認）。
- 月間 412px で右列（2026/08・10・12）の曜日見出し行が左列よりわずかに
  グレがかって見えるが、これは当月外セルのグレー文字の量の差による見え方で、
  表の背景は白（`.my-mini-cal` / `.my-mini-cal-caption` は明示 #FFF）。実害なし。

### まとめ

- fmt / lint 通過。(a) スクロール位置の退行なし、(b) 白帯は週間・月間・
  前後週いずれも消えて #E8E8E8 に統一、(c) 週送りで白抜け・ちらつきの経路なし。
- テンプレート生残り・サーバ例外なし。崩れなし。
- main の判断が要る点: なし（機能面の退行は見当たらない）。強いて言えば
  800px でのグレー面積の大きさは前回同様「許容」の範囲。

---

## ゴミ箱ぶんの確認

対象: `git diff` の 4 ファイル。前回 3 ファイル（`my.css` / `main-page.js` /
`main.html`）に加え、`trash.html` 36 行目から `my-edit-body` を外し、
`my.css` の `.my-trash-main` に `background-color: var(--my-cal-ground)`
（`#E8E8E8`）を追加、`.my-edit-body` のコメントを編集画面専用に更新。

### 1. fmt / lint

- `mise run fmt` → ○ ruff format「43 files left unchanged」、ruff check「All checks passed」、
  prettier 変更なし
- `mise run lint` → ○ basedpyright「0 errors, 0 warnings」、mypy「no issues found in 40 source files」、
  eslint 通過
- `git status` → 変更は上記 4 ファイルのみ。想定外のファイルなし
  （`archives/agents/TODO-176/` は本報告の置き場）

### 2. ゴミ箱画面（一時 datadir・空きポート 10176）

- 起動: `nohup uv run ytsched webapp --datadir <一時dir> --port 10176`
- `trash.jsonl` を自作。UUID `1111…1111` の版 1/2/3 で複数版グループ、
  `2222…2222-1` と `3333…3333-1` で単独 2 件（`ToDo` 含む）。計 5 行
- HTTP `/ytsched/trash` → 200。テンプレート生残り（`{{` `{%`）0 件。
  サーバログに error / traceback / exception なし
- グループ化の実装確認: `TrashHandler.get()` が `SchedDataEnt.id_uuid()`
  （版を除いた UUID 部分）で `by_id` にまとめる。`len(group) > 1` で
  `.my-trash-group-multi` が付く。自作データで `my-trash-group-multi` は 1 個、
  `my-date-block` は 5 個で期待どおり
- スクショ（`tools/screenshot.py --full-page`）:
  - `~/tmp/playwright-mcp/t176_trash_closed_412.png` / `t176_trash_closed_800.png`
  - `~/tmp/playwright-mcp/t176_trash_empty_closed_412.png` / `t176_trash_empty_closed_800.png`

確認点:
- ○ 地が `#E8E8E8` になり、予定（`.my-date-block` = #EEE）が一段明るい
  カードとして浮く。#888 の 2px ボーダーも効いて地とカードの区別が付く
- ○ `.my-trash-group-multi`（#CCC の帯）が地・カードより濃く、3 件の
  グループを囲む帯としてはっきり分かる。「同じ予定の内容が 3 件」の
  見出しも従来どおり
- ○ 削除日時の行 `.my-trash-trashed-at`（「版 N ・ YYYY-MM-DD … に削除」）、
  復活ボタン（丸い矢印）、チェックボックスいずれも表示・配置とも崩れなし
- ○ 空データで「ゴミ箱は空です」（`.my-trash-empty`）が表示され、画面全体が
  `#E8E8E8` で埋まる。白い無地は残らない（412 / 800 とも）
- ○ ゴミ箱ヘッダー（`.my-trash-header` = 青）は従来どおり
- ○ 中身が少ない 800px でも最下部まで地の色で埋まる
  （`.my-trash-main` の `min-height: 100vh`）
- ○ レイアウトの崩れなし

気づいた点（本差分と無関係・既存）:
- 412px の先頭エントリで、時刻列「13:00-14:00」の太字が種別「[予定]」に
  少しかぶる。狭幅での既存の詰まりで、800px では解消。今回の変更が
  原因ではない（地の色だけの変更で、グリッドは触っていない）

### 3. 編集画面への影響（ポート 10176・412px）

- `/ytsched/edit/?date=2026-09-10` → 200。テンプレート生残り 0 件
- クラス確認: `<main id="edit_main">` に `my-edit-main`、フォームの入れ物に
  `my-edit-body my-edit-form-body`。従来どおり
- スクショ: `~/tmp/playwright-mcp/t176_edit_closed_412.png`
- ○ フォームの入れ物（`.my-edit-body.my-edit-form-body`）の背景は `#EEE` のまま。
  `.my-edit-main` は白のまま。色変化・崩れなし
  （`.my-edit-body` の値 `#EEE` は不変、`--my-cal-ground` は使っていない）

### 4. 一覧（週間・月間）

- 前回「## 最終確認」で退行なしを確認済み。今回は撮り直しせず、
  `mise run lint` 通過と `git diff` に想定外ファイルが無いことを再確認（上記 1）

### まとめ

- fmt / lint 通過。ゴミ箱は地が `#E8E8E8` になり予定がカードとして浮く。
  グループ帯・削除日時行・復活ボタン・チェックボックス・空表示・青ヘッダー
  いずれも崩れなし。空・データありとも最下部まで地の色で埋まる。
- 編集画面は背景色・レイアウトとも従来どおりで影響なし。
- テンプレート生残り・サーバ例外なし。
- main の判断が要る点: なし。
