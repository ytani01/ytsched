# TODO-050 implementer への依頼

`TODO.md` の「## TODO-050.」の節を**必ず先に読むこと**。背景・今の作り・
気をつけることが書いてある。以下はその補足。

## チェック項目（TODO.md より）

- [ ] 表示する日を URL に持たせる
- [ ] 画面の移動を POST から GET にする
- [ ] ブラウザの戻る/進むで、前に見ていた日へ戻れるようにする
- [ ] キーボードで週を送れるようにする（PC で使うとき）
- [ ] 追加・修正・削除のあと、リロードで再送信にならないようにする

## 決まっていること（変えないこと）

`TODO.md` の「### 決めたこと」にある 5 つ。要点だけ再掲する。

1. **URL はクエリ。** `/ytsched/?date=2026-08-24`。`webapp.py` の割り当ては
   増やさない
2. **URL に入れるのは日付だけ。** 検索文字列・フィルタ・ToDo の日数・目標件数は
   今までどおり `conf.json`（`get_conf_arg()`）に任せる
3. **追加・修正・削除のあとは GET へリダイレクトする**（POST-Redirect-GET）
4. **編集画面（`/edit/`）も GET にする。** 一覧から日付と `sde_id` をクエリで
   渡す。**保存の POST（`edit.html` の `input_form`）はそのまま残す**
5. **キーボードは表のとおり。** ←/→ で前の週・次の週、Home で今日、
   `/` で検索欄へ、Esc で検索欄から抜ける。↑/↓ は今までどおり

## 移動をどう変えるか（方針）

`my.js` の `doPost()`（202 行目）が form を作って submit している。ここが起点。

- **ページを読み直す移動は、URL への遷移（GET）にする。** `doPost()` の
  代わりになる関数を作り、クエリを組み立てて `location.href` へ入れる
- **`moveToMonday()`（380 行目）の「DOM にあればスクロールで済ませる」は
  残すこと。** 今の一覧は前後 45 日を縦に並べているので、画面内の移動まで
  読み直しにすると遅くなる。ただし**スクロールで移動したときは
  `history.replaceState()` で URL の `date` だけ更新する**（履歴は増やさない）。
  こうすると、リロードしても今見ている位置から始まる
- **`popstate` を拾う必要は無い。** `location.href` での遷移も
  `replaceState` も、戻る/進むはブラウザが素直に処理する

**TODO-049（1 画面 1 週間・スワイプ）はまだ着手していない。**この項目では
表示の形（前後 45 日を縦に並べる）を変えないこと。「週を送る」は、今の
メニューバーの ←/→ と同じ動き（`moveToMonday()`）をキーボードにも割り当てる、
という意味。

## POST-Redirect-GET

`MainHandler.get()` の中で `cmd`（`add`/`fix`/`update`/`del`）を処理している
（`main_handler.py:397` あたり、`exec_update()`）。`update` のときだけ編集画面を
描き、それ以外は一覧へ落ちている。

- **`cmd` は POST で受ける**（フォームの送信なので）。処理が終わったら
  `self.redirect(...)` で日付付きの GET へ飛ばす
- `update` のあと編集画面を描いている経路も、リロードで再送信にならない形に
  すること。どう変えるかは任せるが、**保存した内容が失われないこと**
- `MainHandler.post()` が `get()` を呼ぶだけになっている今の作りは、
  変えてよい

## 触ることになるファイル（見込み）

- `src/ytsched/webroot/static/js/my.js` — `doPost()` ほか
- `src/ytsched/webroot/templates/main.html` — `doPost(...)` の呼び出しが 8 か所
- `src/ytsched/webroot/templates/edit.html` — 一覧へ戻るところ
- `src/ytsched/main_handler.py` — `post()` / `get()` / リダイレクト
- `src/ytsched/edit_handler.py` — `get()` で引数を読む形
- `tests/test_web.py` — POST を投げているところ

## 気をつけること

- **`.longtext`（詳細の欄）を `row` の孫にしないこと。** `min-width: 0` は
  `my.css` の `.row > *` にまとめてかけてあり（TODO-047）、直接の子にしか
  当たらない。入れ子を深くすると `text-overflow: ellipsis` が黙って効かなくなる
  （TODO-045 と同じ症状に戻る）
- **入力欄にフォーカスがあるときはキーを拾わないこと。** 検索欄で `/` が
  打てなくなったり、編集画面で ← を押すと日付が変わったりする
- **`--urlprefix` を変えても動くこと。** テンプレートは `{{ url_prefix }}` を
  使っている。URL を組み立てるところで前置きを落とさないこと
- **アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する**
  （`~/ytsched/data` を汚さない）
- `mise run upgradeproject` は走らせないこと

## 確かめること

- `mise run test` が通ること（POST が GET に変わる分、テストも直す）
- `mise run lint` / `typecheck` / `fmt` が通ること
- 実際に起動して、日付を変えると URL が変わること、戻る/進むが効くこと、
  リロードで再送信の警告が出ないこと

## 報告

`archives/agents/TODO-050/implementer-report.md` に書くこと。
**何をどう変えたか、迷って決めたこと、確かめた結果**を書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内で。
