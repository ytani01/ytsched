# TODO-176. ミニカレンダーと月間表示の背景を薄いグレーにする

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer（最初の `my.css`）＋ main（追実装）＋ verifier ×4 |
| 消費 | output 137,872 / cache_creation 567,891 / 概算 $8.3 |
|      | main 84% + verifier 14% + implementer 2%（料金の割合） |

見込みは `my.css` 1 ファイルの色替えだった。着手後に利用者の指示で
範囲が 3 回広がり（`<main>` の背景 → ゴミ箱 → 地の色の濃さ）、
最終的に 4 ファイル。色の濃さは 4 回振った（`#F0F0F0` → `#E8E8E8`
→ `#E0E0E0` → `#D8D8D8`）。verifier は範囲が広がるたびに追認したので
4 回走った。$8.3 の大半は、この対話しながらの調整（スクショの撮り直しと
verifier の再実行）ぶん。分担そのものは見込みどおり。

## きっかけ

ミニカレンダー（週間表示）と月間表示が、白地に白いカレンダーで、
表がどこまでか分かりにくかった。表の外側を薄いグレーにして、
カレンダーの表を白いカードとして浮かせたい。

## やったこと

`my.css` を中心に、次を入れた。

- **地の色を CSS 変数に集約**。`:root` に `--my-cal-ground: #D8D8D8` を
  新設。予定ブロック `.my-date-block`（#EEE）より濃くして、ブロックや
  白いカレンダーの表がカードに見えるようにした。
- **ミニカレンダー**（週間・月間で共通）
  - `.my-mini-cal-row`（週間表示の行）に `background-color: var(--my-cal-ground)`
    と `padding` / `border-radius`。表 2 枚が白いカードとして浮く。
  - `.my-mini-cal`（表）と `.my-mini-cal-caption`（キャプション帯）を
    明示的に `#FFF`。`border-collapse: collapse` の表なので、表に背景を
    置けば曜日見出し行の透過は白で埋まるが、キャプションは表の背景
    ボックスの外なので別に要る。
- **月間表示**。`.my-month-panel`（パネル全体）に地の色と `padding-bottom`。
- **一覧ページの土台**。`#main`（一覧だけが使う id。編集は `#edit_main`）に
  地の色。`main.html` の `<main>` のインラインスタイルから
  `background-color:#FFF` を撤去（これがヘッダー下〜フッター間の白帯の
  一因だった）。
  - 中身が画面より短いとき `#main` の下からフッターまで `body` の白が
    見えていた。`#main { min-height: 100vh }` を CSS で入れると、
    `main-page.js` `onloadHdr()` の `body_h < win_h` 分岐が反転して
    「今日の行が上寄せされ、週の前半が隠れる」退行が出た。なので
    CSS では入れず、その分岐の中（`return` の手前）で `#main` の
    `min-height` を「画面の高さちょうど」（`elMain.offsetHeight + win_h
    - body_h`）に伸ばす 1 行を足した。この分岐は元々スクロール位置
    合わせをせず抜けるので、スクロール挙動は変わらない。
- **ゴミ箱**。`.my-trash-main` を、編集画面と共用の `.my-edit-body`（#EEE）
  から切り離して `--my-cal-ground` に（`trash.html` の `<main>` から
  クラスを 1 個外し、`.my-trash-main` に背景を直接指定）。ゴミ箱の予定は
  `.my-date-block`（#EEE）なので、これでカードとして浮く。`.my-edit-body`
  は編集画面専用になった（値 #EEE は不変）。

変更ファイル: `my.css` / `main-page.js` / `main.html` / `trash.html`。

分担の詳細と各担当の報告は
[../agents/TODO-176/README.md](../agents/TODO-176/README.md)。

## テスト

`mise run fmt` / `mise run lint` 通過（`test` は CSS・見た目の変更なので
対象外）。verifier が一時 datadir でアプリを起動して確認:

- 週間表示のスクロール位置に退行なし（空データで週頭の行が週バー直下に
  出て、今日より前の日が隠れない。予定入りでは従来どおり今日付近へ
  スクロール）
- 週間・月間・ゴミ箱とも、ヘッダー下からフッター（ゴミ箱はヘッダーのみ）
  まで白い無地の帯が消え、地の色で一様。ミニカレンダーの表・日セル・
  当月外の日・キャプション帯は白のまま
- 週送りで白抜け・ちらつきなし
- 編集画面に影響なし（フォームの入れ物は従来どおり #EEE）

`.my-mini-cal` の `border-radius: 0 0 6px 6px` は `border-collapse: collapse`
の表では Chromium で効かず、表下端の角丸は見えない（キャプション側の
上角丸は効く）。実害なし（TODO-135 に同種の記述あり）。

800px の広い画面では、`.my-mini-cal` の `max-width: 200px` で表が寄って
地の面積が広く見えるが、レイアウトの崩れではない（TODO-137 からの既存の
挙動）。主対象はスマホ幅で、そちらは問題ない。
