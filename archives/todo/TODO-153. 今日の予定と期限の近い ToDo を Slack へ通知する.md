# TODO-153. 今日の予定と期限の近い ToDo を Slack へ通知する

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | main のみ（実装）+ verifier |
| 消費 | output 18,184 / cache_creation 148,462 / 概算 $1.3 |
|      | main 87% + verifier 13%（料金の割合） |

## きっかけ

毎朝、その日の予定と期限の近い ToDo を Slack へ流したい。

**ytsched 側は Slack を知らない。** 通知したい内容をテキストで標準出力へ
出すだけにして、Slack へ送るのは既にある `~/bin/slack-send.sh`
（<https://github.com/ytani01/slack-send>）に任せる。Incoming Webhook の
URL は `~/.webhook-url` にあり、`jq` と `curl` で送っている。この形なら
依存ライブラリも増えず、Webhook URL の置き場も増えず、ytsched 側には
テストしやすい処理だけが残る。

繋ぐのは cron:

```
0 7 * * * $HOME/.local/bin/ytsched notify | $HOME/bin/slack-send.sh -c '#ytsched' -t 'ytsched'
```

コマンドの形:

```
ytsched notify [--datadir DIR] [--date DATE] [--no-todo]
```

出力の例:

```
2026-09-02 (水)
  10:00-11:00 打ち合わせ
  14:00-      買い物

期限が近い ToDo
  09-05 請求書を出す
```

- 期限の近さは、既にある `SchedDataEnt.todo_urgency()` の `over` と
  `near`（`TODO_NEAR_DAYS` = 7 日）をそのまま使う
- **予定も ToDo も無い日も、日付行と「予定なし」を出す。** 毎朝必ず
  1 通届くようにして、届かないこと自体が異常だと分かるようにする
- 動作を確かめるときは `--datadir` に一時ディレクトリを指定する
  （`~/ytsched/data` の実データを汚さないため）

## やったこと

- `src/ytsched/notify.py` を新規に作った。`SchedDataEnt.todo_urgency()`
  をそのまま使い、通知テキストを組み立てる純粋関数群
  （`build_notify_text()` / `build_schedule_section()` /
  `build_todo_section()` / `format_header()` / `format_schedule_line()` /
  `format_todo_line()`）だけを置いた。Slack を知る処理は無い
- `src/ytsched/__main__.py` に `ytsched notify` サブコマンドを足した。
  `--datadir` / `--date` / `--no-todo` を受け、`SchedData` を作って
  `build_notify_text()` を呼び、標準出力へ出すだけ
- 予定の時刻欄は `HH:MM-HH:MM` を 11 桁に揃え、終了時刻が無い予定は
  `HH:MM-` のあとを空白で埋める。時刻そのものが無い予定（終日）は
  時刻欄を出さずタイトルだけにする
- ToDo の節（`期限が近い ToDo`）は、対象が 1 件も無ければ見出しごと
  出さない
- `README.md`・`docs/User.md`・`docs/Developer.md` に機能を書き足した。
  `docs/User.md` には項目番号を書かず、機能の現状だけを書いた

## テスト

`tests/test_notify.py` を新規に作り、`notify.py` の関数を直接呼んで
確かめた（`SchedData` を一時ディレクトリで組み立てる）。

- 予定も期限の近い ToDo も無い日 → 日付行と「予定なし」だけになること
- 予定（時刻あり・終了時刻なし）と期限の近い ToDo が両方あるときの
  整形が、TODO-153 に書いた出力例と一致すること
- 期限が 7 日より先の ToDo は出さないこと
- 期限を過ぎた（`over`）ToDo は出すこと
- `include_todo=False` なら ToDo の節を出さないこと
- 時刻の無い予定は、時刻欄を出さずタイトルだけになること

verifier に別途確かめさせ、`pytest`・`ruff format`・`ruff check`・
`basedpyright` が通ること、実際に一時ディレクトリへテストデータを
仕込んで `ytsched notify` を実行した出力が出力例と一致することを
確認した。問題は見つからなかった。
