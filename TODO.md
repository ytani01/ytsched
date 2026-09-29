# TODO

**残っている項目: TODO-204〜209。** これまでに 203 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-210` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-204. 古い編集画面から保存すると同じ sde_id の予定が 2 件できるのを 409 で止める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `cmd=fix`/`update` で、送られた `sde_id` が `orig_date` のファイルに
      無ければ、何も書かずに 409 を返す（`SchedUpdater` は判定だけ返し、
      409 にするのは `MainHandler`。404 と同じ分け方）
- [ ] 2 つのタブで同じ予定を編集したとき・同じフォームを 2 回送ったときの
      テストを足す（ファイルの行数が増えないこと、409 になること）

`sched_update.py` の `exec_update()` は、`cmd_del()` が何も消さなくても
`cmd_add()` を続ける。1 回目の保存で版が `-1` → `-2` になったあと、
古い画面（`-1`）から保存すると、削除は空振りし、`next_id()` が同じ `-2` を
もう一度作る。2026-09-30 のレビューで再現した（同じファイルに
`…-2` が 2 行）。

409 で止めると決めた（利用者が決めた。2026-09-30）。保存ボタンの
2 回押しでは 1 回目は保存されているので、2 回目がエラー画面になるのは
受け入れる。`del` の空振りは書き込みが起きないので今回は変えない。

---

## TODO-205. ゴミ箱から復活した ToDo が日付のファイルに入るのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `TrashHandler._restore()` で、`is_todo()` なら `ToDo.jsonl`
      （`add_sde(None, …)`）へ入れる。`SchedUpdater.cmd_add()` と同じ分け方
- [ ] ToDo を復活させて、一覧のリンク（`todo_flag=true`）から編集画面が
      開けるテストを足す

いまは `add_sde(restored.date, …)` なので、ToDo も締切日のファイルへ入る。
一覧のリンクは `is_todo()` で `todo_flag=true` を付け、`EditHandler` は
`ToDo.jsonl` を探すので 404 になる。`sched_load.py` の
`load_month_cal()` のコメントは「正常な操作では混ざらない」としているが、
復活はその例外になっている。

---

## TODO-206. POST に CSRF 対策を入れる（xsrf_cookies）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `WebServer` の `tornado.web.Application` に `xsrf_cookies=True` を渡す
- [ ] テンプレートのフォーム（`main.html`・`edit.html`・`edit_menu.html`・
      `trash.html` など。`rg -n '<form' src/ytsched/webroot/templates`）に
      `{% module xsrf_form_html() %}` を入れる
- [ ] `nav.js` の `doPost()` が作るフォームにもトークンを入れる
- [ ] テストの POST（`tests/` の `rg -n 'method="POST"|fetch\(.*POST'` と
      ブラウザテスト）を通す。トークンの無い POST が 403 になるテストを足す

いまは POST にトークンが無い。リバースプロキシが Basic 認証なら、
ブラウザは他のサイトから送らせた POST にも認証情報を付けるので、外の
ページから予定の削除やゴミ箱の全消去ができる。

xsrf_cookies を有効にすると決めた（利用者が決めた。2026-09-30）。
テスト用にだけ切る設定は作らず、テスト側でトークンを取って送る。
取り方が込み入るなら、着手時に相談する。

---

## TODO-207. SchedDataFile.save() を一時ファイル経由にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] 同じディレクトリの一時ファイルへ書いてから `replace()` する
      （`trash.py` の `_write_lines()` と同じ形）
- [ ] 保つもの: 空でないファイルだけを `.bak` に残す、`skipped_lines` を
      元のバイトのまま書き戻す、書いたあとの `_stat_key` を持ち直す、
      元のファイルのパーミッション（`mkstemp()` は 0600 で作る）
- [ ] 書き込みの途中で失敗したとき、元のファイルと `.bak` が残るテストを足す

いまは `.bak` へ `shutil.move()` してから、元の名前へ直接書く。書き込みが
途中で失敗すると壊れたファイルが残り、次の保存でそれが `.bak` になって、
正しい内容がどこにも無くなる。

---

## TODO-208. trash.jsonl にデコードできないバイトがあると一覧が 500 になるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `TrashFile` の `entries()`・`count()`・`delete_many()` で、デコード
      できない行はその行だけ警告して飛ばす（`delete_many()` は元のバイトの
      まま残す。壊れた行を消さない方針は今と同じ）
- [ ] 不正なバイトを含む `trash.jsonl` で、一覧・ゴミ箱画面・一括削除が
      動くテストを足す

テキストモードで開いていて、デコードは `try` の外（`for line in f`）で
起きる。`count()` は `MainHandler.get()` が毎回呼ぶので、一覧画面ごと
500 になる。`SchedDataFile` はバイトで読んで行ごとにデコードしている。

---

## TODO-209. レビューで見つかった小さい食い違いをまとめて直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ConfFile.DEF_CONF` の `ToDo_Days` を `"1y"` から `"365"` にする。
      `tests/test_handler.py:334`（`TODO_DAYS[...]` で引いている）も直す
- [ ] `holiday.py` の `urlopen()` にタイムアウトを付ける
- [ ] 使われていない `SchedData.sdf_has_sde()` と、そのテストを消す
- [ ] `base.html` の `{% autoescape None %}` を消す
- [ ] `src/README.md` を実装に合わせる: CLI の数（5 つ）、
      `load_month_cal()` の判定のしかた、「テンプレートの autoescape」の節

`"1y"` は `int()` で読めず、リクエストのたびに WARNING が出る（値は既定の
365 に落ちるので表示は変わらない。2026-09-30 に実測）。**既にある
`conf.json` は書き換えない**ので、手元の `"1y"` は画面で ToDo の日数を
一度変えるか、手で直す。

`{% autoescape None %}` は tornado では書いたファイルの中だけに効き、
`base.html` にはそのあと式が無いので何も変えていない。子テンプレートは
エスケープされている（2026-09-30 に実測）。`src/README.md` の
「エスケープを切っている」はこれと食い違う。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
