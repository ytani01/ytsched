# TODO-090 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

## なぜこの分担か

`webapp.py`・`handler.py`・`main_handler.py`・`edit_handler.py`・
`ytsched.py` と、`tests/helpers.py` を含むテスト数本にまたがる。新しい
クラスを 2 つ置き、`conf.json` の書き込みの回数と、キャッシュの読み直しの
条件が変わる。実装は `implementer` に分ける。

**挙動が変わるので `reviewer` を入れる**（TODO-017 の基準）。変わるのは
次の 2 つ。

- `conf.json` の書き込みが、`set_conf()` のたびから、リクエストの
  終わりに 1 回だけになる
- `get_sdf()` が、未保存の変更を抱えている日を読み直さなくなる

確認は `~/.claude/CLAUDE.md` の決まりどおり `verifier` を別に立てる。

## main が決めたこと（着手前）

### D: 依存の渡し方

- **`AppInfo`（frozen dataclass）を `handler.py` に置く。** フィールドは
  `title` / `author` / `version` / `url_prefix` / `datadir` の 5 つで、
  型はすべて `str`。`url_prefix` は**末尾に `/` が付いた形**（いまの
  `app.settings["url_prefix"]` と同じ）を入れる
- **`tornado.web.Application` の設定からは、この 5 つを外す。**
  `static_path` / `static_url_prefix` / `template_path` / `debug` /
  `autoreload` は tornado 自身が使うので残す
- `initialize(self, sd, app_info, conf)` の 3 引数で受け取る。
  ハンドラの中では `self._app_info.title` のように参照し、
  `self._title` などの属性は作らない

### D・P: `webapp.py` の URL 登録

- `{"sd": ..., "app_info": ..., "conf": ...}` を 1 つの dict に作って、
  5 つの `URLSpec` で使い回す

### E: `conf.json` のキャッシュ

- **`ConfFile` を新しいモジュール `conf.py` に置く。** `SchedUpdater` /
  `SchedLoader` と同じく **tornado を知らない**クラスにする
- `WebServer` が 1 つだけ作り、`initialize()` で全ハンドラへ渡す
  （`SchedData` と同じ持ち方）
- ファイルの変更の検出は、`SchedDataFile.is_stale()` と**同じやり方**
  （`os.stat()` の `st_mtime` と `st_size` の組）。読み直すのは
  リクエストごとに 1 回（`HandlerBase.__init__`）
- **未保存の変更があるうちは読み直さない。** 読み直すと、その変更が
  消えるため（F と同じ判断）
- 書き込みは `set_conf()` では行わず、リクエストの終わり
  （`HandlerBase.on_finish()`）に 1 回だけ。変更が無ければ書かない。
  書いたあとは `SchedDataFile.save()` と同じく `_stat_key` を持ち直す
- `HandlerBase` の `load_conf()` / `save_conf()` は `ConfFile` へ移す。
  `get_conf()` / `set_conf()` は `ConfFile` へ渡すだけにして残す
  （`MainHandler` / `EditHandler` の呼び出し側は変えない）

### C: `get_conf_arg()` の 4 つ

- **`update_conf_args()` 1 つにまとめる。** 4 つの値を引数から取り込んで
  `conf.json` へ反映し、`ConfArgs`（dataclass。`search_str` /
  `filter_str` / `todo_days_value` / `search_n`）で返す。置き場所は
  `main_handler.py`
- 1 件ぶんの `get_conf_arg()` は **`update_conf_arg()` に改名**する
  （読むだけでないことが名前で分かるようにする）
- `post()` は戻り値を使わない。`_ =` で捨てる形はやめ、そのまま呼ぶ

### F: `get_sdf()` の読み直し

- `_dirty_sdf` に載っている日は、`is_stale()` が真でも読み直さない
