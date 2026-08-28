# TODO-090 reviewer 報告

`git diff` / `git status` の全変更、新規 `src/ytsched/conf.py`、
`archives/agents/TODO-090/README.md`・`implementer-report.md` を読んだ。
tornado (`web.py`) の `RequestHandler.__init__`/`finish()`/
`_execute()`/`_handle_request_exception()` の実装も確認した。

## 直すべき（確信度: 高）

### 1. `ConfFile._save()` が失敗すると、以後ずっと書き込みも読み直しも壊れる

`src/ytsched/conf.py` の `save_if_dirty()`:

```python
def save_if_dirty(self) -> None:
    if not self._dirty:
        return
    self._save()
    self._dirty = False
```

`_save()`（`open(..., mode="w")`）が `PermissionError` などで例外を
投げると、`self._dirty = False` が実行されないまま例外が
`on_finish()` まで伝播する。以前の実装では `HandlerBase` が
リクエストごとに新しく作られ、`self._conf` もそのたびに
`load_conf()` し直していたので、1 回の書き込み失敗は次のリクエスト
に影響しなかった。今回、`ConfFile` は `WebServer` が 1 個だけ作って
**全リクエストで共有**するので、`_dirty` が一度 `True` のまま
止まると、その状態がプロセスの寿命いっぱい残る。結果:

- `ConfFile.refresh()` は `if self._dirty: return` を先頭でやるので、
  以後どのリクエストでも `conf.json` の外部からの書き換え
  （`LoadMonths`/`AutoTurnMsec` の手編集など）を一切拾わなくなる
- `on_finish()` は `_dirty` を見ているだけなので、**`set_conf()` を
  一度も呼んでいない GET リクエストでも**、以後 `on_finish()` の
  たびに `_save()` が再試行され、失敗するたびに例外が発生し続ける

### 2. `on_finish()` での書き込み失敗が、利用者から見えなくなった

`tornado.web.RequestHandler.finish()`（`web.py:1319-1323`）は
`self._log()` → `self._finished = True` → `self.on_finish()` の順で、
**レスポンスをクライアントへ送り終えたあとに** `on_finish()` を呼ぶ。
`on_finish()` 内で例外が起きると `_execute()` の `except Exception`
節で捕まり、`_handle_request_exception()` は `self._finished` が
`True` なので `send_error()` を呼ばずに `log_exception()` するだけで
戻る（`web.py:1934-1938`）。

つまり以前は「`conf.json` への書き込み失敗 → `set_conf()` の中で
例外 → `render()` に到達せず 500 をクライアントへ返す」だったのが、
今回の変更で「200 のページは正常に返り、書き込み失敗はサーバの
ログだけに残る」に変わった。しかも 1 の指摘と組み合わさると、一度の
書き込み失敗のあとは**ずっと**この「クライアントには見えない失敗」が
続く。これは CLAUDE.md の「黙って失敗する書き方」に当たると思う。

（比較として `SchedData`/`SchedDataFile` 側 (`ytsched.py` の
`save()`) にも、`for sdf in self._dirty_sdf.values(): sdf.save()` の
途中で例外が起きると `_dirty_sdf` がクリアされず似た状態になる作りが
既にあるが、これは今回の diff の範囲外で、`TODO-090` が触った
`conf.json` については、1 つを全リクエストで共有する形にしたことで
新しく生まれた問題だと考える。）

## 気になったが確信度は低いもの

- `ConfFile.is_stale()` と `SchedDataFile.is_stale()` は
  `os.stat()` の `st_mtime`/`st_size` を比べる同じロジックを
  それぞれ持っている（意図的に真似た設計と README にあるので、
  重複としては軽微）。共通化する動機は薄いと思うが、念のため記載

## 確認できたこと（問題なし）

- **`on_finish()` が例外・404/400・`redirect()` の経路でも確実に
  呼ばれるか**: `redirect()`/`render()`/`send_error()` はいずれも
  最終的に `RequestHandler.finish()` を通るため、`on_finish()` は
  呼ばれる。実装の想定どおり
- **非同期の重なり**: `main_handler.py`/`edit_handler.py`/
  `handler.py` に `async def`/`await` は無い（grep で確認）。
  `tornado._execute()` は `await` の無いコルーチンなので、1 リクエスト
  の `prepare()`〜`finish()` は途中でイベントループへ制御を返さず、
  他のリクエストの処理と重ならない。`ConfFile` を複数ハンドラで
  共有していることそのものは問題にならない
- **`HandlerBase.__init__` での `self._conf.refresh()`**:
  `tornado.web.RequestHandler.__init__` は `super().__init__()` の
  中で `self.initialize(**kwargs)` を呼ぶ（`web.py:242`）ので、
  `self._conf` は `refresh()` を呼ぶ時点で必ず設定済み。順序の問題は
  無い
- **`get_sdf()` の `_dirty_sdf` ガードと `ConfFile.refresh()` の
  `_dirty` ガード**: どちらも「未保存の変更があれば読み直さない」で
  一致している。`save()`/`save_if_dirty()` が成功した場合は、
  それぞれ `_stat_key` を持ち直すので、直後の再読み込みは起きない
  （両者とも確認済み）
- **`AppInfo.url_prefix`**: `webapp.py`/`tests/helpers.py` とも
  `url_prefix + "/"` で末尾に `/` を付けており、以前
  `app.settings["url_prefix"]` に入れていた値と同じ
- **新しい 5 つのテスト**（`test_conf_reloads_when_file_changed_outside`
  `test_conf_keeps_unsaved_changes` `test_conf_write_happens_once_per_request`
  `test_update_conf_args_returns_and_saves_all_four`
  `test_get_sdf_does_not_reload_dirty_day`）は、それぞれ狙った挙動
  （外部変更での読み直し／未保存中は読み直さない／書き込みが 1 回
  だけ／4 値のまとめと反映／dirty な日は読み直さない）を、実装を
  壊せば落ちる形で押さえている
- `src/README.md` の記述（クラス図・シーケンス図・本文）は実装と
  一致している。`_title`/`_author`/`_url_prefix` などの旧属性の
  残骸も無い（grep で確認済み）

## 判断が要る点

- 上の 1・2 は同じ根（`save_if_dirty()` が失敗時に `_dirty` を
  戻さない）から出ている。直すなら `_save()` を `try/except` で
  囲むか、`_dirty` を先に `False` にしてから `_save()` する
  （後者は「書いたことにして実は失敗」になるので望ましくない）か、
  失敗を検出してログだけでなく別の形で気づけるようにするか、の
  判断が要る。単一ユーザ用アプリで発生頻度は低いと思うが、
  「一度起きると気づかないまま直らない」性質が気になった
