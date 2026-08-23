# TODO-028 implementer への依頼

項目そのものは `TODO.md` の「TODO-028. リファクタリングで見つかった残り
5 件を直す」。背景はそちらに書いてあるので、**先に読むこと**。
独立した 5 件の寄せ集めで、どれも `src/ytsched/main_handler.py` にある。

## 1. `filter_str` を空で送れば解除できるようにする

いま `get_conf_arg("filter_str", ..., empty_is_given=False)` なので、
空文字を送っても「渡されなかった」扱いになり、`Conf.cgi` の値が生き残る。
**フィルタを解除できない。** `search_str` と同じ `empty_is_given=True` に
揃える。

## 2. `filter_str` を小文字にしてから `Conf.cgi` へ保存する

いま `get_conf_arg()` が元の文字列を保存し、そのあとで `.lower()` して
いる。保存する側も揃えて、小文字にしてから保存する。

（注意）**次の TODO-029 で、この `.lower()` は `normalize()` に
差し替わる。** この項目では `.lower()` のままでよいので、`normalize()` を
先取りしないこと。

## 3. `detail` の `〆` 行に残る余分な空白を直す

`fix_todo_done()` が
`f"〆{deadline_date} {deadline_time_start_str}{deadline_time_end_str}\n"`
を作るので、時刻が空のときに `〆2021/01/01 ` と末尾に空白が残る。
時刻が無ければ空白も付かないようにする。

## 4. 使われていない `MainHandler.COOKIE_TODO_DAYS` を消す

どこからも参照されていないことを確かめてから消す。

## 5. 検索モードの 1825 日スキャンを、挙動を変えずに速くする

`load_sched()` は検索モードで最大 `SEARCH_MODE_MAX_DAYS`（1825 日）を
1 日ずつ `self._sd.get_sdf(date1)` で開きに行く。ファイルが無い日でも
`SchedDataFile` を作ってキャッシュに積む。

- **さかのぼる範囲（`SEARCH_MODE_MAX_DAYS`）は変えない。** 1 件も
  当たらないうちだけ 1825 日さかのぼるのは、古い予定を拾うための設計
- **ファイルの無い日は開きに行かずに飛ばす。** ただし、
  `todo_days_value >= 0` のときは `todo_sde` のうち `sde.date == date1`
  のものを拾う処理があり、こちらはファイルの有無と関係が無い。
  飛ばしてよいのは「ファイルも無く、その日に当たる `todo_sde` も無い」日
  だけ。`todo_sde` は少数なので、日付の集合を先に作っておけばよい
- `sched` に入る中身と `date_from`/`date_to`、`search_count` の数え方が
  **今と 1 件も変わらない**ことを確かめる

## テスト

- `filter_str` の 2 件（1・2）は挙動が変わるので、TODO-021 で足した
  ゴールデンマスターテストが落ちる。**書き直してよい**
- 5 件それぞれについてテストを足す。特に 5 は「速くなった」ではなく
  **「結果が変わらない」**ことを確かめるテストにすること
  （ファイルがある日・無い日・ToDo が当たる日を混ぜたデータで、
  変更前と同じ `sched` が出るか）

## 決まりごと

- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は走らせない**
- アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する
- 終わったら報告を `archives/agents/TODO-028/implementer-report.md` に
  書く。返事は「終わったか・報告のパス・判断が要る点」の 5 行以内
