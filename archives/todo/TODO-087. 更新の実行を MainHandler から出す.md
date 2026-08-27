# TODO-087. 更新の実行を `MainHandler` から出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 54,903 / cache_creation 342,900 / 概算 $6.3 |
|      | main 77% + implementer 12% + reviewer 5% + wording 3% + verifier 3%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-087/`](../agents/TODO-087/README.md) にある。

## きっかけ

基本設計のレビュー（2026-08-27）の A。TODO-077 が「`exec_update()`
一式の置き場所は、TODO-081 のあとで考え直す」として持ち越していた。

`MainHandler` は 1,391 行あり、更新の実行・一覧の組み立て・引数の変換の
3 つがほぼ同じ大きさ（約 490 / 510 / 300 行）で並んでいた。

## 着手前に決めたこと

### `post()` は `main_handler.py` に残す

項目を立てたときは `post()` も外へ出すつもりだったが、**残した**。

`post()` は `get_conf_arg()`（`conf.json` への保存）、`get_date()`
（表示する日付の決定）、`mkurl()`（リダイレクト先の組み立て）を使う。
どれも「引数の変換」と「表示」の側の処理で、`MainHandler` に残るもの。
tornado はハンドラ 1 つに `get()` と `post()` の両方を割り当てるので、
`post()` だけを基底クラスへ移すと、**これらを一緒に引きずることに
なり、「更新」という名前のモジュールが表示の都合を持つ**。

そこで「tornado の入口は `MainHandler` に置き、**実行の中身**を外へ
出す」形にした。TODO 項目の 2 つ目のチェック（フォームの値はハンドラ側で
取り出して dataclass に詰めて渡す）とも、こちらのほうが素直に合う。

## やったこと

`src/ytsched/sched_update.py`（269 行）を新しく作り、次の 5 つを移した。
**このモジュールは tornado を import しない。**

- `exec_update()` — 引数の取り出しを除いた、実行そのもの
- `cmd_add()` / `cmd_del()` / `fix_todo_done()` — そのまま
- `get_modified_sde()` — **404 を投げるのをやめて `SchedDataEnt | None`
  を返す**形にした。404 にするのは `MainHandler.exec_cmd()` の側

フォームの値は `SchedUpdateForm`（dataclass、13 個）にまとめ、
`MainHandler.get_update_form()` が詰める。`exec_update()` の引数は
`cmd` の 1 つから、この dataclass 1 つになった。

- 値の取り出しは `SchedUpdater` を呼ぶより先に済ませる。**空でないのに
  読めない日付・時刻を、書き込みが 1 つも起きる前に 400 で断る**
  （TODO-027）という決まりが、これで構造として見えるようになった
- `exec_cmd()` の引数 `search_str` は、docstring に書かれているだけで
  本体では使っていなかったので消した
- `MainHandler.initialize()` で `SchedUpdater` を作る（TODO-081 で
  `SchedData` を `initialize()` で受け取る形にしてあるので、その隣）

`main_handler.py` は 1,391 行から 1,215 行になった。POST 側に残ったのは
`post()` / `exec_cmd()` / `get_update_form()` / `get_date_arg()` /
`get_time_arg()` / `get_deadline_str()` / `mkurl()` で、どれも
tornado の引数を読むか、リダイレクト先を組み立てるもの。

## テスト

挙動を変えていないので、テストの期待値は変えていない。パッチを当てる
先だけを `MainHandler.cmd_add` から `SchedUpdater.cmd_add` に直した
（`tests/test_main_handler.py` と `tests/test_web.py` の 2 か所）。

- 475 件すべて通過
- `ruff format` / `ruff check` / `basedpyright` / `mypy` すべて問題なし
- verifier が、一時ディレクトリを `--datadir` にしてアプリを起動し、
  `add` / `fix` / `update` / `del` の 4 経路と、不正な日付・不正な時刻で
  400 になること（そのときファイルが作られないこと）を実際に叩いて
  確かめた
- reviewer が、移す前のコード（`git show HEAD:src/ytsched/main_handler.py`）
  と 1 行ずつ突き合わせた。指摘は無し
