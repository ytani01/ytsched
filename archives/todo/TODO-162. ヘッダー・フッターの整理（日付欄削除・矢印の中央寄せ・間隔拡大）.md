# TODO-162. ヘッダー・フッターの整理（日付欄削除・矢印の中央寄せ・間隔拡大）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier + reviewer |
| 実施 | Sonnet 5 / effort medium | implementer（×4） + verifier + reviewer |
| 消費 | output 39,159 / cache_creation 399,472 / 概算 $4.1 |
|      | main 44% + implementer 39% + reviewer 11% + verifier 6%（料金の割合） |

## きっかけ

ヘッダーの日付入力欄が不要になっていたのと、フッターの左右矢印
（週送りボタン）の配置・間隔について、次の要望があった。

- ヘッダーの日付入力欄を削除する。不要になったアクションも削除する
- フッターの左右矢印を、メニューボタンとホームボタンの中央に来るように
  配置を変える
- フッターの左右矢印ボタンの間隔をもっと開ける

## やったこと

- `main.html` の週バーから `#header_date` の input（`my-week-bar-date-row`
  / `my-week-bar-date-col`）を削除し、`my.css` の対応するルールも削除した
- `main-page.js` の `actionChangeHdr()` から、`#header_date` の
  `onchange` からしか発火しない `case "date-get":` を削除した
- `main-page.js` の `onloadHdr()`、`week.js` の `setActiveWeek()` から
  `#header_date` への参照を削除した。`src/README.md` の週移動の
  シーケンス図コメントの記述も直した
- フッターの back/forward ボタンを新しいラッパー `.my-menu-nav-center`
  で包み、ハンバーガーの隣に配置。`.my-menu-nav-center` を
  `flex: 1 1 0; justify-content: center;` にすることで、ハンバーガーの
  右端とホームボタンの左端の間の中央に矢印が来るようにした
  （TODO-161 で作った、ホームボタンを行全体の中央に揃える仕組みは
  そのまま維持）
- `.my-menu-nav-col-gap` の `margin-left` を `0.5em` から `1.5em` に
  拡大した
- `tests/test_browser.py` の、`#header_date` の値を検証していたテストを
  改名し、`#header_date` が存在しないことを確かめる内容に書き換えた

### 追加の調整（利用者の見た目確認から）

- ハンバーガー〜矢印間と矢印〜ホーム間の余白が揃って見えなかったのを、
  `.my-row-middle > *` の汎用 `gap` が `.my-menu-nav-left` にも掛かって
  非対称な余白を作っていたのが原因と特定し、`.my-menu-nav-left` に
  `gap: 0;` を追加して打ち消した。ハンバーガーラベルの `&nbsp;` も
  アイコンの前後で対称（1 個ずつ）にした
- back/forward の SVG アイコンだけ `my-align-middle` が付いておらず
  縦位置がずれて見えていたのを、他のフッターアイコンと同じく追加した

### reviewer 指摘の修正

`onloadHdr()` で `#header_date` の代わりに `ytState.activeMonday`
（常にその週の月曜）を使うようにしていたため、月曜以外の特定の日を
指定して開く経路（ゴミ箱の日付欄クリック TODO-149・月間表示の日付セル
クリック TODO-137）で、意図した日ではなく月曜が上端に来てしまう不具合が
あった。`#cur_day`（フッターの検索フォーム内の hidden input。読み込み
直後は `header_date` と同じ「リクエストされた正確な日」を持つ）を
使うように直した。

## テスト

- `mise run fmt` / `mise run lint` / `mise run test`（pytest 607 件）:
  通過
- `--datadir` に一時ディレクトリを指定してアプリを実際に起動し、
  Playwright でヘッダー・フッターをスクリーンショットで確認
  （`~/tmp/playwright-mcp/todo-162-header.png` /
  `todo-162-footer.png`）。日付入力欄が消えたこと、矢印の中央寄せ・
  間隔・アイコンの縦位置が揃ったことを、`bounding_box()` の実測と
  目視の両方で確認
- 月曜以外の日付を指定した URL
  （`?date=2026-09-03&sde_align=top`）で、`#cur_day` の値と
  週の月曜（`data-monday`）が異なることを実測し、修正後は正しい日が
  使われることを確認
- 週送り・検索・フィルタなど、フッターの他の操作が壊れていないことを
  確認
