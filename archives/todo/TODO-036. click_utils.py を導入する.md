# TODO-036. click_utils.py を導入する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + wording |
| 実施 | Opus 5 / effort high | implementer + verifier + **reviewer** + wording |
| 消費 | output 26,155 / cache_creation 261,332（全体） | main 27% + reviewer 21% + implementer 20% + wording 19% + verifier 13% |

## きっかけ

利用者が `src/ytsched/click_utils.py` を持ち込んだ。他のプロジェクト
（`~/work/tmr`）と共通の、click の共通オプションをまとめたメタデコレータ
（デコレータを返すデコレータ）`click_common_opts()`。これを `__main__.py` から使う。

`__main__.py` は `--debug` / `-d` を 3 箇所に手書きし、`-h` / `--help` は
`cli` の `CONTEXT_SETTINGS` で指定していた。`--version` は `webapp` にしか
無く、フラグを `WebServer` へ渡して**コンストラクタの中で**
`Ytsched <ver> by <author>` を表示して `sys.exit(0)` していた。

## 決めたこと

着手前に調べて衝突点を洗い出し、利用者と決めた。

- **`-v` / `--version` は `version_option` に寄せる。** `WebServer` の
  `version` 引数と `sys.exit(0)` ごと消す。表示から `by <author>` が
  消えるのは了承済み
- **`cli` と 3 つのサブコマンドすべてに付ける。** `CONTEXT_SETTINGS` は
  `help_option` が肩代わりするので消せる
- **`click_utils.py` は型ヒントが無いので、lint・型チェックが通るまで直す。**
  他プロジェクトと共通のファイルなので、**中身の動きは変えない**
- **グループ側の `--debug` はサブコマンドへ引き継ぐ。** 実装の途中で
  `ytsched --debug migrate` が DEBUG を出さない（サブコマンドの
  `loggerInit(debug=False)` が上書きする）ことが分かり、追加で決めた。
  受け付けるのに効かないオプションになるため
- **`--version` の表示は `ytsched <ver>`（小文字）のままでよい。**
  `%(prog)s` に入るのは console script 名なので、`__prog_name__`
  （`"Ytsched"`）は使われない。実際に打つコマンド名と一致するほうが自然
  だと判断した。`__prog_name__` が効くのは `python -m ytsched` の経路だけ

## やったこと

- `click_utils.py` に型ヒントを付けた（`Func` / `Decorator` の別名）。
  ロジックの行の並びは `~/work/tmr` 版と同じに保った
- `__main__.py` の `cli` / `x_data1` / `migrate` / `webapp` に
  `@click_common_opts(__version__)` を付け、手書きの `--debug` 3 箇所と
  `CONTEXT_SETTINGS`、`webapp` の `--version` を消した。
  `click_common_opts()` は `click.pass_context` も付けるので、各コマンド
  関数の第 1 引数に `ctx` を足した
- `_is_debug(ctx, debug)` を `__main__.py` に足し、グループ側の `--debug`
  （`ctx.obj["debug"]`）と自分の `--debug` のどちらかが立っていれば DEBUG に
  なるようにした。`ctx.obj` が dict でないとき（`cli` を経由しない
  呼び出し）でも落ちない
- `WebServer.__init__` から `version` 引数と `sys.exit(0)` を消した。
  `tornado.web.Application(..., version=VERSION)` は**残した**
  （テンプレートが使っている）。未使用になった `import sys` は消した
- `src/README.md` のモジュール一覧に `click_utils.py` を足し、共通
  オプションと `_is_debug()` の意図を書いた
- `mylog.loggerInit()` の docstring「1 度だけ呼ぶ」を直した。今回から
  グループとサブコマンドの両方で呼ばれるため

## テスト

- `mise run fmt` / `lint` / `typecheck` / `test`（412 passed）
- `--version` / `-V` / `-v`、`--help` / `-h`、各サブコマンドの `--help`
- `webapp -V` でサーバが起動しないこと
- `--debug` の 4 通り（`--debug migrate` / `migrate -d` /
  `--debug migrate -d` / 無指定）で DEBUG の出方。`webapp` でも同じ 4 通りを
  見て、tornado の `debug` / `autoreload` まで届いていることを確認
- `webapp` を起動して `curl` で 200。バージョンがページに描画されること
  （`WebServer` の `version` を消してもテンプレートが壊れていない）
- `README.md` / `docs/Developer.md` のコマンド例がそのまま通ること

## 見送ったもの

- **`click_utils.py` を `~/work/tmr` 版と揃え直すこと。** 差は型ヒントだけ。
  ytsched の範囲外なので、ずれたままにした。次にどちらかからコピーする
  ときは型ヒントの扱いに注意する
- **`__main__.py` の関数に型ヒントを付けること。** `_is_debug()` を含めて
  どれも型ヒントが無い。今の lint・型チェックの設定では通るので、
  ファイル全体を揃えるなら別項目
- **`cli` の help が `sample package`、モジュール docstring が
  `main for musicbox package` のまま**（雛形の名残）。`ytsched --help` の
  先頭に出るが、この項目の範囲外

## 担当

`archives/agents/TODO-036/` に依頼書と報告がある。
