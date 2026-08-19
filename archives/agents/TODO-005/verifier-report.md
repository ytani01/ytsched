# TODO-005 verifier の報告

TODO-005 の依頼項目はすべて確認でき、**問題は見つからなかった**。

**この報告は verifier 自身が書けなかった（実行環境の制約で報告用の `.md` を
作れなかった）ため、返ってきた本文を main が転記した。**

## 1. `uv sync` — ○

`Resolved 11 packages` / `Checked 10 packages`。エラーなし。

## 2. `uv run pytest -q` — ○

`158 passed in 2.80s`。**xfail 0 件。** 作業前の 140 passed, 6 xfailed から、
実装者の申告どおり増えている。

## 3. `LANG=C uv run pytest -q` — ○

`158 passed in 2.84s`。ロケール依存の失敗なし。

## 4. アプリの起動確認（`--datadir` に一時ディレクトリを指定）

- **起動時の標準出力**: `04:40:39 INFO webapp.py.WebServer.main:123>
  start server: run forever ..` のみ。`DAYS_YEAR=...` は出ない。○
- **メイン画面**: `curl` で `HTTP:200`。`{{` `{%` の生残りなし
  （7256 行の HTML が正常に展開）。○
- **`cmd=add` → `cmd=del` のデータ損失**: `cmd=add` の後、行に
  `4b114aa7-f65c-45c5-a775-5b68bda7010f`（uuid 形式）など 7 項目が正しく
  書かれた。続けて `cmd=del` で最後の 1 件を削除すると `01.cgi` は
  **0 バイトで残り**（消えない）、`01.cgi.bak` に削除前のデータがそのまま
  残った。TODO-005 で直した不具合が解消していることを確認。○
- **`cmd=update` の `search_str`**: GET で `search_str=会議` を渡すと
  `Conf.cgi` は `SearchStr\t会議`。続けて `cmd=update` に `search_str=`（空）を
  付けて POST すると `HTTP:200`、`Conf.cgi` は `SearchStr`（値が空、検索が
  クリアされた状態）になった。○
- **壊れたデータファイル**（項目 3 個の行、時刻欄に `-` の無い行）を
  該当日のファイルに置いてアクセス → いずれも `HTTP:200`（500 にならない）。○
- **壊れた `Conf.cgi`**（空行・タブの無い行 `BadLineNoTab`・値にタブを含む行
  `FilterStr\tfoo\tbar`）を置いてメイン画面へアクセス → `HTTP:200`。
  ログには `WARNING handler.py.MainHandler.load_conf:88> 'BadLineNoTab':
  no tab .. ignored` のみで、例外・トレースバックは無し。○
- **サーバのログ**: 一連の操作を通して INFO 1 行・WARNING 1 行のみ。
  例外・トレースバックなし。○

後始末: `pgrep -f "ytsched webapp"` で PID（`uv run` の親プロセスと `python3` の
実体）を確かめて `kill` 済み。一時ディレクトリはセッション終了で消える。

## 見つかった不具合

無し。

---

# 追加分の再確認（`.bak` が空で上書きされる件）

**1. `uv run pytest -q`** — ○ `161 passed in 2.80s`（前回 158 + 3、xfail なし）

**2. `LANG=C uv run pytest -q`** — ○ `161 passed in 2.89s`

**3. アプリの起動確認**（`--datadir` に一時ディレクトリを指定して起動）

- **(a) 1 件しかない日を `cmd=update` で編集**: 予定を 1 件追加後
  （`元の予定` / `元の詳細`）、`cmd=update` で `編集後の予定` /
  `編集後の詳細` に更新。結果、`2021/03/01.cgi`（本体）は編集後の内容、
  `2021/03/01.cgi.bak` は編集前（元）の内容が残った。○
- **(b) 最後の 1 件を `cmd=del` で消したあと、同じ `cmd=del` をもう一度送る**:
  1 回目の `del` 後、本体は 0 バイト、`.bak` には削除前のデータ
  （`編集後の予定`）が残った。同じリクエストで 2 回目の `del` を送っても、
  本体は引き続き 0 バイト、`.bak` にも同じデータが残り続けた
  （`.bak` が空になって完全にデータが消える、という以前の問題は
  再現しなかった）。○

**4. サーバのログ** — ○ 起動時の `INFO ... start server: run forever ..` のみで、
例外・トレースバックは一切出ていない。

## 見つかった不具合

無し。追加の直しは意図どおり機能している。
