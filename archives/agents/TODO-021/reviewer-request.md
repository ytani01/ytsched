# TODO-021 reviewer への依頼

## この項目の性質

TODO-021 は**リファクタリング**。**挙動を一切変えない**のが前提で、
`MainHandler.get()` / `exec_update()` の分割、`ytsched.py` と
`handler.py` の整理、意味の無い記述の削除を行った。

`verifier` が「動くか」を見る。あなたは「**良いか**」と、
とくに**「本当に挙動が変わっていないか」**を見る。
テストの実行や起動確認はしなくてよい。

## いちばん見てほしいこと

**分割で条件式の意味がずれていないか。** テストが通ることでは
捕まらない種類の変化を探す。具体的には:

1. **設定値の取り出し 4 か所**（`search_str` / `todo_days` /
   `filter_str` / `search_n`）を 1 つのメソッドにまとめてある。
   この 4 つは条件が揃っていない:
   - `search_str` と `search_n` は `value is not None` で分岐
   - `todo_days` と `filter_str` は `bool(value)` で分岐

   まとめた後も、**4 か所それぞれが元と同じ分岐**になっているか。
   空文字を渡したとき、`Conf.cgi` への保存が起きるかどうかが
   元と同じか。`filter_str` は元が `get_argument("filter_str", "")` と
   既定値が違っていた点にも注意（truthy 分岐なので等価のはずだが、
   本当に等価かを見てほしい）

2. **`search_re` によるマッチ 3 か所**を `search_match()` にまとめてある。
   元は `if search_re is not None and not search_re.search(...)` で
   `continue`。`search_re is None` のときに**絞り込まない**という
   意味が保たれているか。3 か所とも同じ意味だったか

3. **一覧を集めるループ**（`while date1 > date_from:`）。
   打ち切り条件（`search_count >= search_n`、`date1 <= date_from1`）と、
   **ループの中で `date_from` を書き換えている**点。切り出した結果、
   `render()` に渡る `date_from` が元と同じ値になっているか

4. **`cmd == "update"` のときに `render()` して `return` する**経路。
   切り出した後も、その先の処理へ落ちていかないか

5. **`exec_update()` の ToDo 完了時の補正**。走る条件
   （`deadline_date` があって、かつ `sde_type` が ToDo でない）と、
   `date` / `time_start` / `time_end` / `detail` の書き換えが元と同じか

6. **`ytsched.py`** の `is_important()` / `is_canceled()` の共通化で、
   `title` が空のときの結果が元と同じか。`is_todo()` を
   `type_is_todo()` へ委譲した結果が元と同じか

7. **`__main__.py`** の `DataFileApp.end()` 削除で、
   例外が出たときの `_log.info("end")` の出方が変わっていないか

## そのほか

- **既存のテストが書き換えられていないか**（書き換えは挙動が変わった印）
- 分割した結果が**読みやすくなっているか**。
  引数が多すぎるメソッド、名前と中身がずれているメソッドが無いか
- 「ついでに揃えた」箇所が無いか。**揃っていない条件は
  揃っていないまま残す**のがこの項目の仕事
- TODO-021 の A〜E の**範囲を超えた変更**が無いか

## 見ないもの

- 好みの問題（変数名の趣味、コメントの多寡）
- 行長 78 のような機械で見るもの
- `TODO.md` に「別の項目にする」と書いてある事柄
  （4 か所の条件を揃えること、など）

## 報告

`archives/agents/TODO-021/reviewer-report.md` に書く。

指摘ごとに、ファイル名・行・何が問題か・**どういう入力や状態で
問題になるか**（＝元と結果が食い違う具体例）。
確信度の高いものを先に、低いものは節を分けて後ろに。
指摘が無ければ「無し」でよい。無理に挙げない。

---

## 追記（main より）

- 変更の中身は `archives/agents/TODO-021/implementer2-report.md`、
  ゴールデンマスターテストは
  `archives/agents/TODO-021/implementer1-report.md` に
  一覧がある。**両方を先に読むこと**
- implementer(2) が単独で決めた判断が 7 件ある（報告の「単独で決めた判断」）。
  とくに次の 3 つは、**判断そのものが妥当かを見てほしい**:
  1. `get_conf_arg()` の分岐を
     `value is not None and (empty_is_given or value)` の 1 行にした。
     **`empty_is_given=True` のとき元の `is not None`、
     `False` のとき元の `bool(value)` と本当に等価か**
  2. `delta_day1` をクラス定数 `MainHandler.DELTA_DAY1` にした
     （`datetime.timedelta(1)`）。テンプレートへ渡る値が変わらないか
  3. `get_timestr()` を `time2str()` を使う形にした。
     `time2str()` は `None` のとき `None` を返す。
     元の `if self.time_start:` との差（`datetime.time(0, 0)` は truthy）が
     出ないか
- **`git diff` は `src/` だけ見ればよい。** `tests/` の差分は
  別の担当が足したゴールデンマスターテストで、レビューの対象外
