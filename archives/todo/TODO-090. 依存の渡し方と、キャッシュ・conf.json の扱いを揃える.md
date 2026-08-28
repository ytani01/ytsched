# TODO-090. 依存の渡し方と、キャッシュ・`conf.json` の扱いを揃える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 41,732 / cache_creation 747,383 / 概算 $10.1 |
|      | main 43% + implementer 41% + verifier 8% + reviewer 6% + wording 3%（料金の割合） |

基本設計のレビュー（2026-08-27）の C・D・E・F と、P の `webapp.py` の件。
分担の理由と各担当の報告は
[archives/agents/TODO-090/](../agents/TODO-090/) にある。

## きっかけ

- **D**: TODO-081 で `SchedData` は `initialize()` で受け取る形になったが、
  `title` / `author` / `version` / `url_prefix` / `datadir` の 5 つは
  `app.settings.get()` のままで、型はどれも `Any` だった。`self._datadir`
  は `os.path.join()` に渡るので、設定が欠けていれば `TypeError` になるが
  型チェッカは何も言わない。
- **P**（`webapp.py` の件）: URL の登録で `{"sd": self._sd}` が 5 回並び、
  渡すものが増えるとそのまま 5 行に効く。
- **E**: データファイルは TODO-080（読み直し）・TODO-077（書き込みを最後に
  1 回）で直ったのに、`conf.json` はリクエストのたびに読み、`set_conf()` の
  たびに全体を書いていた。`get()` で 4 つの設定値が同時に変われば 4 回書く。
- **C**: その 4 つを呼んでいるのが `post()` と `get()` に並ぶ
  `get_conf_arg()`。`post()` の 3 つは戻り値を `_ =` で捨て、「読むと
  `conf.json` へ保存される」という副作用のためだけに呼んでいた。名前が
  `get_` で始まるのに `set_conf()` を呼ぶ。
- **F**: 1 リクエストの中で同じ日を 2 回引き、その間に外部がそのファイルを
  書き換えると、`_dirty_sdf` の古いインスタンスが読み直した内容を消す。
  TODO-080 と TODO-077 の 2 つの仕組みが互いを見ていなかった。

## やったこと

- **D**: `AppInfo`（frozen dataclass、`handler.py`）を作り、5 つを
  `initialize(sd, app_info, conf)` の引数へ移した。`tornado.web.Application`
  の設定からはこの 5 つを外し、tornado 自身が使う `static_path` /
  `static_url_prefix` / `template_path` / `debug` / `autoreload` だけ残した。
  ハンドラ側は `self._app_info.title` のように参照する。
- **P**: `webapp.py` の 5 つの URL 登録は、`{"sd", "app_info", "conf"}` の
  dict を 1 つ作って使い回す形にした。
- **E**: `ConfFile` を新しいモジュール `conf.py` に置いた。`SchedUpdater` /
  `SchedLoader` と同じく **tornado を知らない**クラスで、`WebServer` が
  1 つだけ作って全ハンドラで共有する（`SchedData` と同じ持ち方）。
  外部の書き換えの検出は `SchedDataFile.is_stale()` と同じやり方
  （`os.stat()` の `st_mtime` と `st_size` の組）で、読み直しは
  `HandlerBase.__init__` から 1 リクエストにつき 1 回。書き込みは
  `HandlerBase.on_finish()` で 1 回だけ、変更があったときだけ行う。
- **C**: `get_conf_arg()` を `update_conf_arg()` に改名し、`post()` と
  `get()` に並んでいた 4 つの呼び出しを `update_conf_args()` 1 つに
  まとめた。戻り値は `ConfArgs`（dataclass。`search_str` / `filter_str` /
  `todo_days_value` / `search_n`）。`post()` は戻り値を使わない。
- **F**: `SchedData.get_sdf()` で、`_dirty_sdf` に載っている日は
  `is_stale()` が真でも読み直さないことにした。`ConfFile.refresh()` の
  「未保存の変更があるうちは読み直さない」と同じ決め方。
- `src/README.md` を実装に合わせて直した（モジュール一覧に `conf.py`、
  クラス図に `AppInfo` / `ConfFile`、リクエストの流れの図の
  `conf.json` の読み書きの回数）。

### レビューで見つかって直したもの

`ConfFile` を 1 プロセスで共有するようにしたことで、**`conf.json` への
書き込みが 1 度失敗すると、その状態がプロセスの寿命いっぱい残る**経路が
できていた（`save_if_dirty()` が失敗時に `_dirty` を `False` に戻さない）。
`refresh()` が `if self._dirty: return` で止まるので外部の書き換えを
二度と拾わなくなり、`set_conf()` を呼んでいない GET でも `on_finish()` の
たびに書き込みを再試行して失敗し続ける。

`save_if_dirty()` で `OSError` を捕まえ、**警告を 1 行出して `_dirty` を
`False` に戻す**ことにした。書けなかった値はメモリ上に残したまま使い、
`_stat_key` は持ち直さない（あとで外部から書き換えられれば読み直せる）。500 には
しない。`conf.json` は設定だけなので、書けなくても画面は出したほうがよい
（TODO-032 と同じ考え方）。

## テスト

- 既存のテストは、`app.settings` から読んでいたところ（`tests/helpers.py` /
  `tests/test_handler.py` / `tests/test_webapp.py`）と、`set_conf()` の
  直後にファイルを見ていたところを、新しい仕様に合わせて直した。
  書き込みが `on_finish()` に移ったので、往復を見るテストは
  `handler.on_finish()` を挟み、読む側は `make_app()` を呼び直して
  別インスタンスの `ConfFile` に読ませる形にした。
- 足したテストは 6 つ。`conf.json` を外部で書き換えたら読み直すこと、
  未保存の変更があるときは読み直さないこと、1 リクエストの中で
  `set_conf()` を何度呼んでも書き込みは 1 回だけであること、
  `update_conf_args()` が 4 つの値を返して `conf.json` へ反映すること、
  `get_sdf()` が `_dirty_sdf` に載っている日を読み直さないこと、
  書き込みに失敗しても次のリクエスト以降が止まらないこと。
- `ruff format --check` / `ruff check` / `basedpyright` / `mypy src` /
  `pytest`（481 件）が通ることを verifier が確認した。
- verifier がアプリを実際に起動して、一覧と編集画面が 200 で返ること、
  検索語が `conf.json` に保存されること、外から書き換えた `conf.json` が
  次のリクエストで効くこと、予定の追加・修正・削除が反映されることを
  確かめた。書き込みの失敗については、`chmod` で書けない状態にしても
  200 が返り続けて警告が 1 行出ること、書ける状態に戻せば普通に
  保存できることを確かめた。
- 足したテストのうち 3 つは、実装を一時的に壊して実際に落ちることを
  確かめてある。
