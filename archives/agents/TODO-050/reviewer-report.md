# TODO-050 レビュー報告（reviewer）

## 確信度の高い指摘

### 1. `search_str`／`search_n` が、JS の一部の経路で URL に載ってしまう

TODO.md の TODO-050 の節で「検索文字列とフィルタは URL に入れない。
入れるのは日付だけ」と決めているが、`doPost` を `doGet` へ機械的に
置き換えたことで、この決めごとに反する経路が 2 つ残っている。

- `src/ytsched/webroot/templates/main.html:20-24`
  （`homeButtonHdr` の単一クリック、検索中にホームへ戻るとき）
  ```js
  doGet('{{ url_prefix }}',
         { date: '{{ today }}', search_str: search_str } );
  ```
  検索欄の値をそのまま `doGet` に渡している。以前は `doPost`
  （form の POST body）だったので URL には出なかったが、いまは GET の
  クエリになるので、`?date=...&search_str=...` がアドレスバーに残る。
- `src/ytsched/webroot/templates/main.html:104`
  （`changeSearchN`、検索期間の「目標件数」を変えたとき）
  ```js
  doGet('{{ url_prefix }}', {date: cur_day.value, search_n: val} );
  ```
  同様に `search_n` が GET のクエリに載る。

どちらも `get_conf_arg()` はメソッドを見ずに `get_argument()` で読むので
（`main_handler.py:399` 以降）、値自体は今までどおり `conf.json` に
保存され、機能としては壊れていない。**問題は URL に出てしまうこと**
（ブックマーク・共有・ブラウザ履歴に検索語が残る）。

`tests/test_web.py` の `TestRedirect.test_search_str_is_not_in_url` は
サーバー側（`<form method="POST">` → `post()` の PRG）だけを見ており、
この 2 か所のような、フォームを介さず JS が直接 `doGet` を呼ぶ経路は
テストの対象になっていない（JS を実行するテストが無いため）。
「テストが通ることを見ても出てこない」抜けの実例だと思う。

3 つのフォーム（検索・ToDo 日数・絞り込み）は POST のまま残す、という
決めごとの意図からすると、この 2 か所も POST 経由にするか、あるいは
`date` だけを `doGet` で送り、`search_str`/`search_n` は POST のままの
フォームに任せる形にするのが筋に合うと思う。

### 2. `src/README.md` が、`post()` の記述のまま更新されていない

`src/README.md:141-143` に

> `MainHandler`（`main_handler.py`）が一覧表示と、追加・修正・削除の
> 実行（`cmd=add/fix/update/del`）を兼ねる。`GET`/`POST` とも同じ
> `get()` を呼ぶ（`post()` は `self.get()` に委譲するだけ）

とあり、リクエストのシーケンス図（`src/README.md:179-181`）にも

```
alt POST
    Handler->>Handler: post() は get() に委譲するだけ
end
```

とある。今回の変更で `post()` は `get()` を呼ばなくなり、
POST-Redirect-GET になった。`cmd` の実行も `get()` から抜けて `post()`
だけが行うようになったので、「`GET`/`POST` とも同じ `get()` を呼ぶ」も
成り立たなくなっている。`src/README.md` はこの diff に含まれておらず、
実装と食い違ったまま残っている。`CLAUDE.md` で「コードを触る前に
`src/README.md` を読むこと」としている以上、ここが古いままだと次に
触る人を誤らせる。

## 確信度が低い指摘（気になる程度）

### 3. キーボードでの週送りは、履歴が増えないことが多い

`moveToMonday()`（`my.js:411-`）は、移動先の週の要素が既に DOM に
あれば `replaceDateInUrl()` だけで済ませ、無いときだけ `doGet()`
（実際のページ遷移、履歴が増える）を呼ぶ。既定の表示範囲は前後 45 日と
広いので、←→ を何度か押しても大半は `replaceState` で処理され、履歴は
増えない。

TODO.md の「ブラウザの戻る/進むで、前に見ていた日へ戻れるようにする」を
「矢印キーで移動した 1 回 1 回に戻れる」という意味だとすると、この作りは
外れる（戻るボタンを押すと、キー操作の分は飛ばされて、このページに来る
前の画面へ一気に戻る）。実装者の報告にある「スクロールでの移動では履歴を
増やさない」という決めごとの範囲に、キーボードでの移動も同じ扱いで
含めてよいかどうかは、設計判断だと思うので、指摘というより確認事項として
挙げておく。

## 問題無しと判断した点（依頼の着眼点のうち）

- **`exec_cmd()` の `edit_url` と `orig_date`**：`cmd=update` で
  `edit_url` に積む `date`/`sde_id`/`todo_flag`/`search_str` は、
  `EditHandler.get()` が `sde_id` から `sdf.date` を再取得して
  `orig_date` を決める作りと整合していた（ToDo は `get_sdf(None)`、
  それ以外は `get_sdf(date)`）。旧コードが `render()` に直接渡していた
  `orig_date` と同じ値になることを、`get_modified_sde()`／
  `exec_update()` の分岐まで辿って確認した
- **`mkurl()` の `if val` によるフィルタ**：`date`・`modified_sde_id`・
  `sde_align`・`sde_id`・`todo_flag`（`"true"`/`"false"` 文字列）・
  `search_str` のいずれも、空文字や `"0"` が意味を持つ値として渡る
  経路は無く、実害は見当たらなかった
- **`get()` から `cmd` を外したこと**：以前は GET でも `cmd` が効いて
  いた（`post()` が `get()` に委譲していたため）が、いまは GET に
  `cmd` を付けても無視される。状態を変える操作が GET で効かなくなる
  方向の変更なので、問題ではなくむしろ妥当だと思う
- **`EditHandler.post()` を消したこと**：`edit.html` の保存フォームは
  もともと `post_url`（`MainHandler` のルート）へ送っており、
  `/edit/` への POST は他のどこからも来ていない（`grep` で確認）
- **`keyHdr()`／`isTyping()`**：`input`/`textarea`/`select`/
  `contenteditable` を拾う判定で、抜け・拾いすぎは見当たらなかった。
  `main.html` にしか `keydown` を登録していないことも確認した

## 判断が要る点

- 指摘 1（検索語・目標件数が URL に出る）を直すかどうか、直すなら
  どちらの形にするか（2 か所も POST に戻す／`doGet` に渡す値から
  `search_str`・`search_n` を外す）
- 指摘 2（`src/README.md` の更新漏れ）を、この TODO-050 の中で直すか、
  別途にするか
