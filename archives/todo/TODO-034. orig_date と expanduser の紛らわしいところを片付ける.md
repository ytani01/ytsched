# TODO-034. `orig_date` と `expanduser()` の紛らわしいところを片付ける

見込み: main = Opus 5 / effort medium、担当 = verifier + wording（実装は main）
実施: main = Opus 5 / effort medium、担当 = verifier + wording（実装は main）

分担の理由と各担当の報告は `archives/agents/TODO-034/` にある。

## きっかけ

どちらも**バグではない**が、読む人に誤解させる。TODO-029 の reviewer と
TODO-028 の reviewer から、それぞれ据え置かれていたもの。

1. `sde.html` が `orig_date` を組み立てて `doPost()` のパラメータに
   載せていたが、受け取る `EditHandler.get()` は `orig_date` を読んで
   いない（TODO-029 より前からそう）。ToDo のときは `'{{ None }}'` が
   文字列 `"None"` として送られていた。TODO-029 で「`orig_date` は
   handler が決める」と方針が定まったので、送る側が残っているのは
   紛らわしい
2. `date2path()` に渡す前の `expanduser()` が `SchedDataFile.__init__` と
   `SchedData.sdf_exists()` の 2 か所に分かれていた。`topdir` を省いて
   `date2path()` を単独で呼ぶと `~` が展開されないまま渡る道が開いていた
   （そう呼んでいる箇所は無かった）

## やったこと

**1. `sde.html` の `orig_date` を消した。**
消す前に、`sde.html` の `doPost()` を通る経路を洗った。`sde.html` を
`{% include %}` しているのは `main.html` だけで、この `doPost()` の
宛先は `url_prefix + 'edit/'` の 1 つ、受け取るのは `EditHandler` の
`get()` / `post()` だけ。`EditHandler.get()` が読む引数は `date` /
`search_str` / `sde_id` / `todo_flag` で、`orig_date` は入っていない。
パラメータの行と、そのための `{% set orig_date = ... %}` 2 行を消し、
「`orig_date` は `EditHandler` が決めるので、ここからは送らない」と
コメントを残した。

編集画面の隠しフィールド `orig_date` は今までどおり出る。値を決めるのは
`EditHandler.get()`（TODO-029）で、そこは触っていない。

**2. `expanduser()` を `date2path()` の中へ寄せた。**
`SchedData.sdf_exists()` 側の `expanduser()` は消した。
`SchedDataFile.__init__` の `self.topdir = os.path.expanduser(topdir)` は
残した。`topdir` は外から読める属性で、展開済みの値が入っていることを
`test_topdir_is_expanded` が見ているため。残した理由はコメントに書いた。
`~` の展開そのものの挙動は変えていない。

## テスト

`tests/test_ytsched.py` に、`date2path()` を単独で呼んだときに `~` が
展開されることを見るテストを 2 つ足した
（`test_date2path_expands_topdir` / `test_date2path_todo_expands_topdir`)。

verifier の確認（報告は `archives/agents/TODO-034/verifier-report.md`）:

- `ruff check` / `ruff format --check` / `basedpyright` / `mypy` /
  `pytest`（404 件）がすべて通る
- 一時ディレクトリを `--datadir` にしてアプリを起動し、予定の追加 →
  編集画面 → 更新 → 削除がひととおり動く。編集画面の `orig_date` は
  その行が入っているファイルの日付になっている
- 一覧画面の HTML から `orig_date:` が消えている
- `~` 付きの `--datadir` でも、実ホーム配下に書かれる

## 途中の失敗

素の `uv run ruff format` を走らせてしまい、プロジェクトの
`--line-length 78`（`mise.toml` の `fmt`）と違う整形が無関係な箇所に
入った。78 桁で入れ直し、それでも戻らなかった 3 か所（一度結合された
文字列は `ruff format` が分割し直さない）は手で元へ戻した。
**整形は `mise run fmt` を使うか、`--line-length 78` を付けて呼ぶ。**
