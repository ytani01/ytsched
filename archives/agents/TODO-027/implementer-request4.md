# TODO-027 implementer への依頼（4 回目）

3 回目のレビュー（`reviewer-report3.md`）で出た指摘に、利用者が方針を
決めた。**そのとおりに直してほしい。**

**注意: この項目の変更はまだコミットされていない。**
`git checkout` / `git restore` / `git stash` など、**作業ツリーを戻す
コマンドは絶対に使わないこと**（3 回目に `git checkout -- src` で
未コミットの実装を一度消している）。`git diff` / `git status` は読むだけ
なので構わない。

## 読むもの

- `archives/agents/TODO-027/reviewer-report3.md`（指摘の元。特に
  「確信度の高い指摘」1・2・3 と「main の判断が要るところ」）
- `archives/agents/TODO-027/verifier-report3.md`
- `archives/agents/TODO-027/implementer-report3.md`（自分の前回の報告）
- 変更そのものは `git diff`

## 先に知っておくこと（重要）

**`uv run pytest` は今、コレクション段階で全滅する。** 原因は
TODO-027 とは無関係で、コミット `2b4fcce feat(webapp): add url_prefix
option` が `WebServer.URL_PREFIX` を `DEF_URL_PREFIX` に変えたのに、
`tests/helpers.py:23` と `tests/test_webapp.py:30,34` が追随していない。

```
tests/helpers.py:23: URL_PREFIX = WebServer.URL_PREFIX
AttributeError: type object 'WebServer' has no attribute 'URL_PREFIX'
```

**これは直さないこと。** 別項目として扱うと利用者が決めた。
`tests/helpers.py` と `tests/test_webapp.py` には手を触れない。

**したがって、この依頼ではテストを走らせて確かめられない。**
テストは書くが、通ることは確かめられない状態で終わる。
`uv run ruff format` / `ruff check` / `basedpyright` / `mypy` は
（`tests` を外せば）走るので、そちらは通しておくこと。
**「テストが通った」とは報告しないこと。走らせられなかったと書く。**

## 直してほしいこと

### 1. 更新経路で日付が読めないときは 400 を返す（指摘 1・2）

**方針: 「書き込む経路は、読めない引数を受け取ったら断る」で一本に
揃える。** reviewer が推した案 1 を採用した。

`exec_update()`（`main_handler.py:817`）で、`cmd` が
`add`/`fix`/`update`/`del` のとき:

- **`date` が空でないのに日付として読めない**（形式が不正、または
  `date_range()` の外）→ `tornado.web.HTTPError(400)`
- **`orig_date` が空でないのに日付として読めない** → 同じく 400
- **`time_start` / `time_end` が空でないのに時刻として読めない**
  → 同じく 400（下の 2 と合わせて）

**空のときの扱いは今までどおり変えない。** `date` が空 → `None` →
`SchedDataEnt` 側で今日（TODO-016 で決めた「空 ＝ 省略」）。
`orig_date` が空 → `None` → ToDo のファイル。

**400 は、書き込みが 1 つも起きる前に返すこと。** `cmd_del()` /
`cmd_add()` より前で弾く。

前例は `main_handler.py:454` の 404（TODO-016）。同じ形で、
`raise tornado.web.HTTPError(400, ...)` にメッセージを付ける。

**`orig_date_is_broken` の二度読み（`main_handler.py:838-841`）は消える。**
`cmd in ["del", "fix", "update"]` のところにある `if
orig_date_is_broken:` の分岐と警告も要らなくなる（400 で断るので、
「消さずに進む」経路そのものが無くなる）。指摘 4 はこれで片付く。

**表示経路（`GET` の `date` / `cur_day` / `year`+`month`+`day` /
`search_n` / `todo_days`）は変えない。** そちらは今までどおり
「警告を出して既定値へ落とす」。変えるのは**書き込む経路だけ**。

### 2. `get_time_arg()` の 500 を塞ぐ（残る唯一の 500）

`main_handler.py:947`。`datetime.time.fromisoformat(value)` が素通しで、
`time_start=abc` / `time_end=abc` は 500 になる。

**1 と同じ判断で、400 にする。** `convert_value()` に載せて `None` に
落としたうえで、`exec_update()` 側で「空でないのに `None`」なら 400。
`date` / `orig_date` と同じ形に揃えること。

（`datetime.time.fromisoformat()` は `OverflowError` を投げないので、
`check_int_range()` のような下ごしらえは要らない。`ValueError` だけ
見ればよい。念のため自分で確かめること）

### 3. `src/README.md` の `HandlerBase` の説明を直す（指摘 3）

`src/README.md:14` と `55-58`。どちらも `HandlerBase` を
「`Conf.cgi` の読み書き」とだけ書いているが、今は
`convert_value()` / `date_range()` / `check_date()` / `str2date()` /
`check_int_range()` / `SEARCH_MODE_MAX_DAYS` が入っていて、
**引数の変換と検証の置き場所**でもある。

**1〜2 行足すだけでよい。** 書き換えすぎないこと。
`CLAUDE.md` が「コードを触る前に必ず開くこと」と名指ししている文書
なので、次に触る人が変換まわりを `MainHandler` に探しに行かないように
するのが目的。

## テストの直し

`tests/test_web.py` の `TestInvalidUpdateArgs`（1156 行〜）は、今の
挙動（今日へ寄せる／消さずに足す）をそのまま固定しているので、
**400 を返す挙動に書き直す。**

書き直しになるはずのもの:

- `test_add_with_unreadable_date_becomes_today`（1199）
- `test_add_with_far_future_date_becomes_today`（1224）
- `test_del_with_unreadable_orig_date_deletes_nothing`（1247）
- `test_del_with_unreadable_orig_date_keeps_todo`（1265）
- `test_del_with_unreadable_orig_date_logs_a_warning`（1287）
- `test_update_with_unreadable_orig_date_keeps_the_original`（1305）
- `test_far_future_orig_date_does_not_delete_todo`（1325）

**押さえること:**

- 400 が返ること
- **400 のときにデータが 1 行も変わっていないこと**（`ToDo.jsonl` も、
  日付ごとのファイルも）。ここが本丸。`cmd_del()` の前で弾けているか
  はこれで分かる
- `time_start=abc` / `time_end=abc` でも同じ（500 でなく 400、データは
  無傷）
- **`orig_date` が正しいときに削除・更新が今までどおり効くこと。**
  reviewer が指摘 7 で「足すとしたら」と書いていた分。
  400 のガードが普通の操作まで止めていないことを、同じクラスの中で
  読めるようにする
- `GET` の表示経路（`date=abc` など）が**今までどおり既定値へ落ちる**
  ことを固定しているテストは、**変えないこと**（`TestInvalidArgs` など）

`tests/test_main_handler.py` にも落ちるものがあれば同じ方針で直す。

## 決まりごと

- **`tests/helpers.py` と `tests/test_webapp.py` には触らない**（上記）
- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。動きを見るときは
  `--datadir` に必ず一時ディレクトリを指定する
- 行の長さは 78 桁（`ruff format --line-length 78`）
- ログは `mylog.py` のラッパを使う
- 新しく足したもの・変えたものには `(TODO-027)` を添える
- **自分だけで決めた判断は、報告に「単独で決めた判断」として並べる**
- 報告は `archives/agents/TODO-027/implementer-report4.md` に書く。
  返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内
