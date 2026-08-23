# TODO-032 verifier 報告

未コミットの作業ツリー（`src/ytsched/handler.py`・`main_handler.py`・
`migrate.py` および各テスト・文書）を対象に、依頼書の 5 項目を
実際に一時ディレクトリで動かして確かめた。**すべて期待どおり。**

作業ディレクトリ:
`/tmp/claude-649/-home-ytani-work-ytsched/b36aa44a-9ea6-40fe-8875-273bf8e732e7/scratchpad/verify032`

## 1. 移行ツール

`tests/data/old_format/` をコピーし、euc_jp の値（`会議`）を含む
`Conf.cgi` を自作して置いた。

```
uv run ytsched migrate --datadir <tmp>/olddata --dry-run
```
→ `設定ファイル    : 変換 1, 飛ばした 0` と出るが `conf.json` は
**書かれない**（○）。

```
uv run ytsched migrate --datadir <tmp>/olddata
```
→ `conf.json` が生成され、euc_jp の値が正しく utf-8 の JSON へ
デコードされていた（○）。

```json
{
  "ToDo_Days": "14",
  "FilterStr": "会議",
  "SearchStr": "test",
  "SearchN": "30"
}
```

元の `Conf.cgi` は削除されず残っていた（○）。

もう一度同じコマンドを走らせると
`設定ファイル    : 変換 0, 飛ばした 1` と出て、`conf.json` は
上書きされなかった（既存ファイルの警告つきスキップ。○）。

## 2. アプリが移行後の設定を読むか

`uv run ytsched webapp --datadir <tmp>/olddata -p 18085 --urlprefix
/ytsched` を起動し、`curl -s -o main.html -w "%{http_code}"
http://localhost:18085/ytsched/` → **HTTP 200**。

取得した HTML に `{{` `{%` の生残りは無し（`grep -c` = 0）。

- `<option value="14" selected>` … `ToDo_Days` が反映されている（○）
- `<input id="filter_str" ... value="会議" />` … euc_jp から変換した
  値がそのまま画面に出ている（○）

サーバのログ（`server.log`）に例外・トレースバックは無し。

## 3. 画面から設定を変えると `conf.json` が更新されるか

`curl "http://localhost:18085/ytsched/?filter_str=hoge&search_n=99"`
→ HTTP 200。直後の `conf.json`:

```json
{
  "ToDo_Days": "14",
  "FilterStr": "hoge",
  "SearchStr": "test",
  "SearchN": "99"
}
```

JSON のまま正しく書き換わっていた（○）。

## 4. 壊れた `conf.json` でも画面が出るか

3 パターンをそれぞれ別の一時ディレクトリに置いて起動し確認。
いずれも **HTTP 200**、`{{`/`{%` の生残りなし。

- 壊れた JSON（`{ "ToDo_Days": "14", broken`）
  → ログ: `Expecting property name enclosed in double quotes: line 1
  column 22 (char 21) .. ignored`
- トップレベルが配列（`["a","b"]`）
  → ログ: `not an object .. ignored`
- 値が数値（`{"ToDo_Days": 14, "FilterStr": "ok"}`）
  → ログ: `'ToDo_Days'=14: not a string .. ignored`。
  ただし **`FilterStr` は文字列なので保持され**、画面の
  `filter_str` に `value="ok"` として反映されていた（キー単位で
  読み飛ばす仕様どおり。○）

## 5. 旧 `Conf.cgi` が残っていても読みに行かないこと

`conf.json` を置かず `Conf.cgi`（`ToDo_Days=3`、`FilterStr=zzz`）だけ
置いて起動。HTTP 200。画面に `zzz` も `value="3" selected` も
現れず、既定値のまま（○ = 旧ファイルを読みに行っていない）。

## 使ったコマンド

```
uv run ytsched migrate --datadir <tmp> [--dry-run]
uv run ytsched webapp --datadir <tmp> -p <port> --urlprefix /ytsched
curl -s -o <out>.html -w "%{http_code}" http://localhost:<port>/ytsched/
curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost:<port>/ytsched/?filter_str=hoge&search_n=99"
```

起動したプロセスは各ケースの直後に `kill <PID>` して確認済み
（最終確認: `pgrep -af "ytsched webapp --datadir /tmp/claude-649"` で
残存プロセス無し）。

## 不具合

見つからなかった。

## その他気づいたこと（報告のみ、直していない）

- `migrate.py` の `migrate_conf()` は `--dry-run` でも
  `self.stat.conf_files += 1` を先に加算してから戻る作りで、
  `migrate_file()` 側と同じ流儀（統計は dry-run でも数える）に
  揃っている。挙動として問題は無いが、依頼書には明記が無かった点なので
  念のため書いておく。
- 確認とは無関係だが、ポート 12345 で別プロセス
  （`uv run ytsched webapp -d -p 12345 -u /ytsched2`）が実データを
  対象に常駐しているのが `pgrep -af` に見えた。今回の確認では触れて
  いない。
