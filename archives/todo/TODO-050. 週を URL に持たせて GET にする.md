# TODO-050. 週を URL に持たせて GET にし、キーボードでも操作できるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | main + verifier + reviewer + wording |
| 消費 | output 96,694 / cache_creation 805,738 / 概算 $16.1 |
|      | main 78% + verifier 11% + implementer 5% + reviewer 4% + wording 2%（料金の割合） |

**implementer はセッション上限で落ちた**（ファイルを読み始めたところで停止し、
コードは 1 行も変わっていなかった）。利用者の指示で main が引き継いで実装した。
分担の理由と各担当の報告は
[archives/agents/TODO-050/](../agents/TODO-050/README.md) にある。

## きっかけ

**URL が変わらなかった。** `my.js` の `doPost()` が form を作って submit して
いたので、どの日を見ていても URL は `/` のまま。戻る/進むが効かず、リロード
すると再送信になり、ブックマークもできなかった。

**TODO-049（1 画面 1 週間・スワイプで週送り）の土台**でもある。週が URL に
あれば、スワイプを `history.pushState` と組み合わせられ、戻る＝前に見ていた週に
なる。iOS Safari の画面端スワイプ（戻る）とも競合しない。

PC で使うときに、週を送るのに下部のメニューバーの ←/→ を押しに行くしか
なかった点も、ここで直した。

## 決めたこと（着手時に利用者と決めた）

- **URL はクエリ。** `/ytsched/?date=2026-08-24`。`webapp.py` の割り当ては
  増やさない。TODO-049 で週が単位になっても、その週の月曜を渡すだけでよい
- **URL に入れるのは日付だけ。** 検索語・絞り込み・ToDo の日数・目標件数は
  今までどおり `conf.json` に保存する。URL に入れると「保存されている値と
  どちらを優先するか」を項目ごとに決めることになり、範囲が広がる
- **追加・修正・削除のあとは GET へリダイレクトする**（POST-Redirect-GET）
- **編集画面も GET にする。** 保存の POST はそのまま残す
- **キーボードは ←/→・Home・`/`・Esc**

## やったこと

### 移動を GET にした（`my.js`・`main.html`・`sde.html`）

- `doPost()` に代わる **`doGet()` と `mkUrl()`** を置いた。`URLSearchParams` で
  クエリを組み立てて `location.href` へ入れる
- **`doPost()` は残した。** ただし用途を限り、**`conf.json` へ保存される値
  （検索語・目標件数）を送るときだけ**使う。GET のクエリに載せると、
  ブックマークにも履歴にも検索語が残ってしまうため
- `doPostDate()` → `doGetDate()`

### 履歴の積み方を 3 通りに分けた（`my.js`）

一覧は前後 45 日を縦に並べているので、画面内の移動まで読み直しにすると遅い。
「画面内にあればスクロールで済ませる」（`scrollToDate()` / `moveToMonday()`）は
残したまま、URL と履歴を合わせた。

| 移動のしかた | 履歴 |
|--------------|------|
| 読み直した直後の位置合わせ（`onloadHdr`） | 増やさない（`replaceDateInUrl()`） |
| 画面内で完結する移動（←→・日付の欄など） | 1 つ増える（`pushDateInUrl()`） |
| 画面外への移動（`doGet()`） | ブラウザが 1 つ増やす |

**戻ってきたときは `popstateHdr()`** が URL の `date` までスクロールする。
読み込んである範囲の外なら `location.reload()`。

**ここは 2 回作り直した**（下の「履歴の積み方を 2 回作り直した」を見ること）。

### POST-Redirect-GET（`main_handler.py`）

- `post()` が `get()` を呼んで描くのをやめた。`conf.json` へ保存される値を読み
  （`get_conf_arg()` が保存する）、`cmd` を実行してから `redirect()` する
- `exec_cmd()` から `render()` を外し、3 番目の戻り値を `rendered: bool` から
  `edit_url: str | None` に変えた。`cmd=update` のときは編集画面の URL を返す
- `get()` から `cmd` の処理を外した。**GET に `cmd` を付けても効かなくなった**
  （状態を変える操作が GET で効かない方向なので、むしろ妥当）
- `modified_sde_id`（更新した行を光らせる値）は、クエリで受け渡す
- `mkurl()`（staticmethod）を足した。値が `None`・空のものは入れない

### キーボード（`my.js`・`main.html`）

`keyHdr()` と `isTyping()`。←/→ は `moveToMonday()`、Home は今日へ、`/` は
検索欄へ、Esc は入力欄から抜ける。**入力欄にフォーカスがあるときは Esc 以外を
拾わない。** 登録は `main.html` だけ（編集画面で ←→ が効くと、入力の途中で
画面が変わる）。

### 編集画面（`edit_handler.py`・`sde.html`）

- **一覧からは GET で来るようになったので、`post()` を消した。**
  保存の POST は `edit.html` の form が `MainHandler` へ送るので、そこは変えて
  いない
- **検索語を引数で渡すのをやめ、`conf.json` から読むようにした。**
  `edit.html` での用途は「検索中かどうか」の判定だけ（保存したあとの
  `sde_align`）なので、これで足りる。`CONF_KEY_SEARCH_STR` は `HandlerBase` に
  あるので、`EditHandler` からそのまま使えた

### 文書

`src/README.md` の「`GET`/`POST` とも同じ `get()` を呼ぶ（`post()` は
`self.get()` に委譲するだけ）」を書き直し、シーケンス図の `alt POST` も
302 を返す形にした。

## 履歴の積み方を 2 回作り直した

**どちらもテストが通る状態で見つかった。** 実装と確認を分けた効果が出た例。

1. **最初は `replaceState` にした。**「スクロールのたびに戻るで辿れても
   嬉しくない」と考えて履歴を増やさない形にしたが、**それだと戻るときに
   途中の日付を飛び越える**。verifier が実測で見つけた（← を 8 回押してから
   戻ると、3 回分の移動が 1 つにまとまり、3 回目の戻るで `about:blank` まで
   行った）。`pushState` + `popstate` に変えた
2. **今度は履歴が二重に増えた。** `onloadHdr()` が読み直しのたびに
   `scrollToDate()` を呼び、その中で `pushDateInUrl()` が走る。読み直しそのもの
   で履歴は 1 つ増えているので、**同じ日付が 2 つ並び、戻るを 1 回押しても
   画面が変わらない**。これも verifier が見つけた。`scrollToDate()` に
   **元からあって使われていなかった `push_flag` 引数**を効かせて直した

**reviewer も、テストでは出ない抜けを 1 つ見つけた。** `doPost` を `doGet` へ
機械的に置き換えたせいで、**`conf.json` へ保存される値まで GET のクエリに
載っていた**（検索語・目標件数）。「URL に持たせるのは日付だけ」という決めごとに
反していたが、機能としては壊れていないので、テストでは分からなかった。
`doPost()` を用途を限って戻し、5 か所を直した。

## テスト

`tests/test_web.py` に **`TestRedirect` を 9 件足した**（もとの 418 件 →
**427 件**）。

- POST が 302 になり、飛び先が一覧／編集画面のどちらか
- `modified_sde_id` がクエリで渡ること
- **検索語が URL に入らず、`conf.json` に入ること**
- 更新したあとの飛び先にも検索語が付かないこと
- 編集画面の検索語が `conf.json` から来ること
- クエリの日付で表示できること（ブックマーク）

`cmd=update` は編集画面へリダイレクトするようになったので、
`test_update_search_str_is_lowered` は `EditHandler.render` を見る形に直した。

**JS の経路はテストできない**（JS を実行するテストが無い）。reviewer が
見つけた「検索語が URL に載る」は、まさにそこだった。verifier が playwright で
実際のブラウザを動かして確かめている。

### テンプレートのコメントが、テストの本文検査に引っかかった

`main.html` に `// 目標件数は URL に載せない` と日本語で書いたら、
`assert "目標件数" not in body` を見ているテストが 2 件落ちた。テンプレートの
コメントは HTML に出る。**識別子で書くようにした**（`// search_n は URL に
載せない`）。

## 確かめたこと

- `mise run test` → **427 passed**、`ruff format --check` / `ruff check` /
  `basedpyright` / `mypy` → すべて通った
- **verifier が playwright で実機確認**（3 回）。戻る/進むが 1 回ずつ辿れること、
  進むも同じこと、検索語・目標件数が URL に載らないこと（5 通りの操作）、
  編集画面で ←→ が効かないこと、追加・修正・削除のあとリロードしても
  二重にならないこと、キャプチャで見た目が崩れていないこと

**モバイル幅でのスワイプは確かめていない**（TODO-049 の範囲）。

## 残したこと

- **表示の形は変えていない。** 前後 45 日を縦に並べ、スクロールで追加読み込み
  する今のまま。1 画面 1 週間にするのは TODO-049
- **`popstate` 以外のブラウザ操作は拾っていない**（必要が無い）
