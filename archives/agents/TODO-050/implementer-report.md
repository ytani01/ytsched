# TODO-050 実装の報告（main が実装した）

**implementer はセッション上限で落ちた**（ファイルを読み始めたところで停止、
コードは 1 行も変わっていなかった）。利用者の指示で main が引き継いで実装した。

## 何をどう変えたか

### `static/js/my.js`

- **`doPost()` を消し、`doGet()` と `mkUrl()` にした。** form を作って submit する
  代わりに、クエリを組み立てて `location.href` へ入れる。`mkUrl()` は
  `URLSearchParams` を使い、値が `undefined`・`null` のものは入れない
- **`doPostDate()` → `doGetDate()`**（中身は変えていない）
- **`scrollToDate()` と `moveToMonday()` の「画面内にあればスクロール」は残した。**
  そのとき `pushDateInUrl()` で URL の `date` を書き換え、**履歴を 1 つ増やす**
  （`history.pushState`）。戻ってきたときは `popstateHdr()` がその日まで
  スクロールする（読み込んである範囲の外なら `location.reload()`）
- **`keyHdr()` と `isTyping()` を足した。** ←/→ は `moveToMonday()`、Home は
  `scrollToDate()` で今日へ、`/` は検索欄へ、Esc は入力欄から抜ける。
  `isTyping()` が真のときは Esc 以外を拾わない

### `templates/main.html`・`templates/sde.html`

- `doPost(` → `doGet(`（main.html 6 か所、sde.html 1 か所）、
  `doPostDate(` → `doGetDate(`（2 か所）
- **`main.html` の `onloadHdr` の隣で `keydown` を登録した。** 一覧だけに効かせる
  ため（編集画面で ←→ が効くと、入力の途中で画面が変わる）
- **3 つのフォーム（検索・ToDo の日数・絞り込み）は `method="POST"` のまま。**
  値は `conf.json` に保存するもので、URL には入れないと決めたため（TODO-050）。
  POST は下の PRG で GET へ飛ぶ

### `main_handler.py`

- **`post()` を POST-Redirect-GET にした。** `get()` を呼んで描くのをやめ、
  `conf.json` へ保存される値を読み（`get_conf_arg()` が保存する）、`cmd` を
  実行してから `redirect()` する
- **`mkurl()`（staticmethod）を足した。** 値が `None`・空のものは入れない
- **`exec_cmd()` から `render()` を外した。** 3 番目の戻り値を `rendered: bool`
  から `edit_url: str | None` に変えた。`cmd=update` のときは編集画面の URL を
  返し、`post()` がそこへ飛ばす
- **`get()` から `cmd` の処理を外した。** `modified_sde_id` は
  `get_argument()` でクエリから受け取る

### `edit_handler.py`

- **`post()` を消した。** 一覧からは GET で来るようになったので、呼ばれない。
  保存の POST は `edit.html` の form が `MainHandler`（`post_url`）へ送るので、
  そちらは変わっていない

### `tests/test_web.py`

- `test_update_search_str_is_lowered` を直した。`cmd=update` は編集画面へ
  リダイレクトするようになったので、`MainHandler.render` ではなく
  `EditHandler.render` の引数を見る
- **`TestRedirect` を足した（7 件）。** 302 になること、飛び先が
  一覧／編集画面のどちらか、`modified_sde_id` が付くこと、
  **検索語が URL に入らず `conf.json` に入ること**、クエリの日付で表示できること

## 迷って決めたこと

- **`modified_sde_id` は URL に入れた。** 「URL に入れるのは日付だけ」と決めたが、
  これは検索語・フィルタ（`conf.json` に保存されるもの）の話。更新した行を
  光らせる（`class_blink`）ための一時的な値で、保存する筋のものではないので、
  クエリで渡すことにした
- **最初は `replaceState` にしていたが、`pushState` + `popstate` に直した。**
  「スクロールのたびに戻るで辿れても嬉しくない」と考えて履歴を増やさない形に
  したが、**それだと戻るときに途中の日付を飛び越える**。verifier が実測で
  見つけた（← を 8 回押してから戻ると、3 回分の移動が 1 つにまとまり、
  3 回目の戻るで `about:blank` まで行った）。TODO-050 のチェック項目
  「戻る/進むで、前に見ていた日へ戻れるようにする」を満たしていなかった。
  読み直しを伴う移動と揃えて、どちらでも 1 つずつ辿れるようにした
- **表示の形は変えていない。** 前後 45 日を縦に並べる今のままで、
  スクロールでの追加読み込みも残っている（TODO-049 で変える）

## 確かめた結果

- `mise run test` → **425 passed**（もとの 418 + 足した 7）
- `ruff format --check` / `ruff check` / `basedpyright` / `mypy` → すべて通った
- 実際に起動して curl で確認
  - `GET /ytsched/?date=2026-09-01` → 200
  - `POST /ytsched/` → **302**、`Location: /ytsched/?date=2026-09-01`
  - `POST` に `search_str=ABC` を付けても、**Location に `search_str` は入らない**
  - `GET /ytsched/edit/?date=2026-09-01` → 200
  - 一覧の HTML に `doPost` は残っていない（`doGet` が 6 か所）

**ブラウザでの戻る/進む・リロード・キーボードは、まだ試していない。**
verifier に任せる。

---

## 確認・レビューの指摘を受けて直したこと

### verifier の指摘: 戻るが途中の日付を飛び越える

`replaceState` では履歴が増えないので、画面内で完結する移動（←→ を続けて
押したときなど）が戻るで辿れなかった。**`pushDateInUrl()`（`pushState`）に変え、
`popstateHdr()` を足した。** 戻ってきたら URL の `date` までスクロールし、
読み込んである範囲の外なら `location.reload()` する。`main.html` で
`popstate` を登録した（一覧だけ）。

### reviewer の指摘 1: 検索語・目標件数が URL に載る

`doPost` を `doGet` へ機械的に置き換えたせいで、**`conf.json` へ保存される値まで
GET のクエリに載っていた**。「URL に持たせるのは日付だけ」という決めごとに
反していた。**`doPost()` を、用途を限って復活させた。**

| どこ | 直し方 |
|------|--------|
| `my.js` | `doPost()` を戻し、docstring に「`conf.json` へ保存される値を送るときだけ使う」と書いた |
| `main.html` `homeButtonHdr` | 検索中にホームへ戻る経路を `doPost` に |
| `main.html` `changeSearchN` | 目標件数を `doPost` に |
| `main.html` 日付の欄 | 検索の解除（`search_str` を空で送る）を `doPost` に |
| `sde.html` | 編集画面へ `search_str` を送るのをやめた |
| `edit_handler.py` | 検索語を `self.get_conf(self.CONF_KEY_SEARCH_STR)` から読む |
| `main_handler.py` | `exec_cmd()` が返す編集画面の URL から `search_str` を外した |

`edit.html` での `search_str` の用途は「検索中かどうか」の判定だけ（保存したあとの
`sde_align`）なので、`conf.json` から読めば足りる。`CONF_KEY_SEARCH_STR` は
`HandlerBase` にあるので、`EditHandler` からそのまま使えた。

**テストを 2 件足した。** 編集画面の検索語が `conf.json` から来ること、
更新したあとの飛び先に検索語が付かないこと。

なお、テンプレートに入れた日本語のコメントが**テストの本文検査に引っかかった**
（`"目標件数" not in body`）。コメントは識別子で書くようにした
（`// search_n は URL に載せない`）。

### reviewer の指摘 2: `src/README.md` が旧仕様のまま

「`GET`/`POST` とも同じ `get()` を呼ぶ（`post()` は `self.get()` に委譲するだけ）」を
書き直し、シーケンス図の `alt POST` も 302 を返す形にした。URL に持たせるのは
日付だけ、という決めごともここに書いた。

### reviewer の指摘 3（確信度が低い、として挙げられたもの）

「キーボードでの週送りは履歴が増えないことが多い」は、verifier の指摘と同じ
ところ。`pushState` に変えたことで解消している。

## 直したあとの結果

- `mise run test` → **427 passed**（425 + 足した 2）
- `ruff format --check` / `ruff check` / `basedpyright` / `mypy` → すべて通った

### verifier の 2 回目の指摘: 読み直しをまたぐと戻るが 1 回分ずれる

`onloadHdr()` が読み直しのたびに `scrollToDate()` を呼び、その中で
`pushDateInUrl()` が走っていた。**読み直しそのもので履歴が 1 つ増えているので、
同じ日付が 2 つ並んでいた**（戻るを 1 回押しても画面が変わらない）。

`scrollToDate()` には**元から使われていない `push_flag` 引数があった**ので、
それを効かせた。真なら `pushDateInUrl()`（履歴を増やす）、偽なら
`replaceDateInUrl()`（URL だけ書き換える）。`onloadHdr()` からは
`false` を渡す。`replaceDateInUrl()` は、この用途で戻した。

これで 3 通りが揃う。

| 移動のしかた | 履歴 |
|--------------|------|
| 読み直した直後の位置合わせ（`onloadHdr`） | 増やさない（`replaceState`） |
| 画面内で完結する移動（←→・日付の欄など） | 1 つ増える（`pushState`） |
| 画面外への移動（`doGet`） | ブラウザが 1 つ増やす |
