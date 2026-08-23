# TODO-027 implementer の報告（3 回目）

reviewer の指摘 1（`month`/`day` の `OverflowError`）・2（更新経路の
`date`/`orig_date`）・3（`EditHandler` の `date`）を直し、ついでの
指摘 4（docstring）も片付けた。指摘 5・6・7 は依頼書のとおり触っていない。

## 変えたファイル

### `src/ytsched/handler.py`（`HandlerBase`）

指摘 3 のために、**変換まわりを `MainHandler` から `HandlerBase` へ
上げた**（中身は変えていない）。`HandlerBase` にも `self._days` が
あることを確かめてから移した。

- `convert_value()` / `date_range()` / `check_date()` / `str2date()` を
  移動
- `SEARCH_MODE_MAX_DAYS` も移動（`date_range()` が使うため）。
  `MainHandler` 側には「`HandlerBase` にある」というコメントを 1 行残した。
  `MainHandler.SEARCH_MODE_MAX_DAYS` は継承で今までどおり読める
  （既存テストがこの名前で参照している）
- `check_int_range(name, value, value_min, value_max)` を追加。範囲外の
  整数を `ValueError` にする。`check_date()` の整数版で、「`datetime` へ
  渡す前に弾く」という同じ役目なので隣に置いた

### `src/ytsched/main_handler.py`

- **指摘 1**: `str2ymd_date()` が、`year` だけでなく `month`（1..12）と
  `day`（1..31）も `datetime.date()` を呼ぶ**前に** `check_int_range()`
  で見るようにした。3 つとも同じ形になった
- `str2todo_days()` の範囲チェックも `check_int_range()` に寄せた
  （メッセージの形は前と同じ `todo_days must be in -1..36500, not ...`）
- **指摘 2**: `get_date_arg()` を
  `convert_value(arg_name, value, self.str2date)` に載せた。日付として
  読めない値も、表示に使える範囲の外の日付も、警告 1 行 → `None`
- **指摘 2（`orig_date`）**: `exec_update()` で、`orig_date` が
  「渡されているのに読めない」ときは `cmd_del()` を**呼ばない**ように
  した（警告 1 行）。判断の理由は後述

### `src/ytsched/edit_handler.py`

- **指摘 3**: `datetime.date.fromisoformat(date_str)` を
  `self.convert_value("date", date_str, self.str2date)` に置き換えた。
  読めなければ `None` → 既存の `if not date: date = today` に乗る

### `tests/test_web.py`（+13 件）

- `TestInvalidArgs` に 4 件（指摘 1）: 巨大な `month`、巨大な `day`、
  大きく負の `day`、`month` の範囲が分かる警告が出ること
- `TestInvalidUpdateArgs`（新しいクラス、7 件。指摘 2）:
  - `cmd=add&date=abc` / `date=9999-12-31` が**今日のファイル**へ入り、
    `ToDo.jsonl` は作られないこと
  - `cmd=del&orig_date=abc` で**元の予定が消えないこと**、
    **`ToDo.jsonl` の同じ `sde_id` が消されないこと**（消し間違い）、
    警告が出ること
  - `cmd=update&orig_date=abc` でも元の予定が残ること
  - `orig_date=9999-12-31`（日付にはなるが使えない）でも ToDo を
    消さないこと
- `TestEditHandler` に 2 件（指摘 3）: `date=abc` / `date=9999-12-31` が
  今日になること（`value="<今日>"` を見る）

### `tests/test_main_handler.py`

- 指摘 4。`TestConfArgs` の docstring の「``search_n``/``todo_days`` は
  ``convert=int``」を、「`search_n` は `int`、`todo_days` は
  `str2todo_days()`（中で `int()` を呼ぶ）」に直した。結論
  （空文字は両方とも「渡されていない」のと同じ扱いになるので、
  TODO-028 で `empty_is_given` を揃えてもここは落ちない）は変えていない

## 自分で確かめたこと

- `mise run lint`（fmt + basedpyright + mypy）→ すべて通った。
  `mise run test` → **374 passed**（前は 361。13 件増）。
  `upgradeproject` は走らせていない
- **足したテストが本当に捕まえるかを、直した 3 か所を 1 つずつ潰して
  確かめた**（潰したあとは毎回、控えから戻して 374 passed を再確認）
  - `month`/`day` の `check_int_range()` を外す → 指摘 1 の 4 件が落ちる
  - `get_date_arg()` を `fromisoformat` に戻す →
    `TestInvalidUpdateArgs` の 6 件が落ちる
  - `orig_date_is_broken` を `False` に固定する →
    `..._keeps_todo` / `..._logs_a_warning` /
    `test_far_future_orig_date_does_not_delete_todo` の 3 件が落ちる
  - `edit_handler.py` を `fromisoformat` に戻す →
    `TestEditHandler` の 2 件が落ちる
- 一時ディレクトリ（scratchpad）に `ToDo.jsonl` を 1 件置いて
  `--datadir` に指定し、アプリを起こして curl で確かめた。**すべて 200**

  | 入力 | 結果 |
  |---|---|
  | `?year=2021&month=99999999999&day=1` | 200 |
  | `?year=2021&month=1&day=99999999999` | 200 |
  | `?year=2021&month=1&day=-99999999999` | 200 |
  | `?year=2021&month=13&day=1` / `?year=2021&month=2&day=31` | 200 |
  | `/edit?date=abc` / `/edit?date=9999-12-31` | 200 |
  | `?cmd=add&date=abc&title=test1&sde_id=` | 200・今日のファイルへ |
  | `?cmd=add&date=9999-12-31&title=test2&sde_id=` | 200・今日のファイルへ |
  | `?cmd=del&orig_date=abc&sde_id=id-t` | 200・`ToDo.jsonl` は無事 |

- 出た警告の実物（`--days` 既定 45 なので範囲は 0005-12-31..9995-01-01）:
  - `year/month/day='2021/99999999999/1': month must be in 1..12, not 99999999999 .. ignored`
  - `year/month/day='2021/1/-99999999999': day must be in 1..31, not -99999999999 .. ignored`
  - `year/month/day='2021/2/31': day 31 must be in range 1..28 for month 2 in year 2021 .. ignored`
    （**月末の判定は今までどおり `datetime` の言い分がそのまま出る**）
  - `date='abc': Invalid isoformat string: 'abc' .. ignored`
  - `date='9999-12-31': date must be in 0005-12-31..9995-01-01, not 9999-12-31 .. ignored`
  - `orig_date='abc': unknown file .. not deleted`
- 確かめ終わったあと、起動したサーバは止めた（`pgrep` で確認）

## 単独で決めた判断

1. **`orig_date` が読めないときは、消す処理そのものを飛ばす。**
   `None` に落とすと `cmd_del(None, sde_id)` が **`ToDo.jsonl` を
   開いて `sde_id` を探し、保存し直す**（`SchedData.del_sde()` は
   `date=None` を ToDo のファイルとして扱う）。読めない `orig_date` は
   「ToDo だ」という意味ではないので、別のファイルを触りに行くことに
   なる。**消えて困るのは元のデータのほう**で、消さずに残っていれば
   利用者が消し直せる。だから「どのファイルか分からないなら消さない」に
   した。警告 `orig_date=...: unknown file .. not deleted` を 1 行出す
   - **副作用**: `cmd=fix`/`update` で `orig_date` が読めないと、
     元の 1 件が残ったまま新しい 1 件が書かれるので、**同じ `sde_id` の
     予定が 2 つになる**（curl でも再現した）。元がどこにあるか分から
     ない以上、正しく消す手が無い。重複は画面から消せるが、消して
     しまったデータは戻らないので、こちらを選んだ
   - 「渡されているのに読めない」と「渡されていない（＝ ToDo）」を
     分けるため、`exec_update()` で `get_argument("orig_date")` を
     もう一度見て `orig_date_is_broken` を作った。`get_date_arg()` の
     戻り値だけでは、この 2 つが区別できない
2. **`date`（`cmd=add`/`fix`/`update`）が読めないときは `None`。**
   依頼書のとおり、`SchedDataEnt` 側で今日に補正される経路
   （TODO-016、`date` が空の POST と同じ）に乗せた
3. **`month` は 1..12、`day` は 1..31 で弾く。** 年と同じく「そもそも
   ありうる範囲」で弾く形にした。`month=13` の警告文は `datetime` と
   同じ言い回し（`month must be in 1..12, not 13`）なので変わらない。
   `day=32` だけは、`datetime` の
   `day is out of range for month` から `day must be in 1..31, not 32`
   に変わる。**月末（2 月 31 日など）の判定は今までどおり
   `datetime.date()` に任せている**ので、日付の正しさの判断は変えて
   いない
4. **変換まわりは `HandlerBase` へ上げた**（置き場所は任せると
   あったので）。`EditHandler` から `str2date()` を使うのに、これが
   いちばん短い。`str2ymd_date()`/`str2todo_days()` は `MainHandler`
   だけの引数（`year`/`month`/`day`、`todo_days`）を扱うので、
   `MainHandler` に残した
5. **`SEARCH_MODE_MAX_DAYS` も `HandlerBase` へ移した。**
   `date_range()` が使う値で、2 か所に同じ数字を置きたくなかった。
   `MainHandler` からは継承で今までどおり読める
6. `check_int_range()` を `HandlerBase` に置いたのは、`check_date()` と
   同じ「`datetime` へ渡す前に弾く」役目だから。**今の使い手は
   `MainHandler` だけ**なので、`MainHandler` に置く手もあった

## 直さずに残したもの

- **指摘 5・6・7 は触っていない**（依頼書のとおり）
- **`src/README.md` は直していない。** `HandlerBase` の説明が
  「`Conf.cgi` の読み書き」だけなので、変換まわりが増えたことは
  書かれていない状態になった。2 回目の依頼書に「この項目では
  `src/README.md` へ追記しない」とあり、3 回目の依頼書にも指示が
  無かったので手を出していない。**書くなら main の判断**
- **`get_time_arg()`（`time_start`/`time_end`）はそのまま。**
  `time.fromisoformat()` が素通しなので `time_start=abc` は 500 に
  なる（実測はしていない）。依頼書の A・B・C のどれでもなく、
  TODO-027 が挙げた 5 か所にも入っていないので触っていない。
  **別項目にするかは main の判断**
- `deadline_date` などの `get_deadline_str()` は文字列のまま使われる
  ので、同じ穴は無い

## うまくいかなかったところ

- **作業の途中で `git checkout -- src` を実行してしまった。**
  「足したテストが直す前のコードで落ちるか」を見るつもりだったが、
  **1・2 回目の実装はまだコミットされていない**ので、
  `src/ytsched/` が TODO-027 に手を付ける前の状態まで戻ってしまった。
  直前に `src` を scratchpad へ控えていたので**その場で書き戻し、
  `diff -r` で一致を確認、374 passed も再確認**した（`tests/` と
  `TODO.md` は `checkout` の対象にしていないので無事）。
  そのあとの確認は、`git` を使わず**控えからの書き戻しだけ**で行った。
  失われたものは無いが、危ない操作だったので記録に残す
