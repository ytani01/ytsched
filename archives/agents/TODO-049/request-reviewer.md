# TODO-049 reviewer への依頼

`TODO.md` の「## TODO-049. 1 画面 1 週間の表示にする」の節と、
[request-implementer.md](request-implementer.md)、
[implementer-report.md](implementer-report.md) を先に読むこと。

## 見てほしいもの

変更したコードの質。**コードは直さないこと。**見つけたことを報告し、
直すかどうかは main が決める。

差分は `git diff`（`src/` と `tests/` の 12 ファイル）。

### とくに見てほしいところ

1. **`my.js` から消したものが、消しすぎ・消し足りないになっていないか。**
   `getTopDateString()` / `scrollHdr()` / `scrollHdr0()` /
   `scrollHdrTimer` / `scrollFlag` / `getDaysFromToday()` が落ちている。
   残った側（`scrollToId()` / `scrollToDate()` / `popstateHdr()` /
   `moveToMonday()`）から参照が切れていないか、逆に使われないまま
   残っている関数・変数が無いか
2. **`dispGage()` の作り。** `sessionStorage` を素で読み書きしている
   （`GAGE_MONDAY_KEY`）。private mode などで例外になる環境で画面が
   壊れないか。`placeGageWithoutTransition()` の
   `void elGageR0.offsetHeight` によるレイアウト確定が、意図どおり
   効くか（`classList` の付け外しと `requestAnimationFrame` の順序）
3. **`mondayOf()` の日付の扱い。** `my.js` の先頭のコメントにある
   「`new Date()` の区切り文字が `/` だと JST、`-` だと UTC」という
   落とし穴を踏んでいないか。月曜へ丸める計算（`1 - wday`、日曜を 7 と
   みなす）が、`moveToMonday()` の同じ計算とずれていないか
4. **`load_sched()` の週の計算。** `date.weekday()` を使った月曜の
   求め方と、検索モードの分岐が混ざっていないか
5. **`--days` を消した跡。** `handler.py` の `date_range()`、
   `webapp.py`、`__main__.py`、`tests/helpers.py` に残りかすが無いか。
   `webapp.py` の `MainHandler` の import が要らなくなっていないか
6. **テストの直し方。** implementer が「判断が要る」として挙げた 5 件
   （報告の「迷ったところ」1・2）が、**変更を通すためにテストを緩めて
   いないか**。とくに次の 2 つ:
   - `test_todo_one_day_over_the_boundary_is_not_shown` が
     `body` 全体から `day_block(body, today)` に変わった。これは
     「見る範囲を正しく絞った」のか「見なくなった」のか
   - `test_overdue_todo_is_shown_on_today` が
     `body.count(TITLE) == 1` から `TITLE in day_block(...)` に変わった。
     曜日によって落ちる不安定さを取り除いたという説明が妥当か
7. **`my.css` の `.my-gage-r-no-transition`。** 打ち消しクラスの
   詳細度が足りているか（`.my-gage-r` と同じ 1 クラスなので、
   後ろに書いてあることに依存している）

## 変えていないはずのもの

ここが変わっていたら報告すること。

- 検索モード（`SEARCH_MODE_MAX_DAYS` / `SEARCH_MODE_DAYS` /
  `search_n` の打ち切り、`sde_align` の `bottom`）
- Python 側の `GAGE` と `days2y_offset()`
- ToDo の `load_todo()` / `mk_todo_by_date()`
- テンプレートへ渡す `date`（指定された日のまま。月曜へ丸めない）
- `sde.html` が使うテンプレート変数の `date_to`

## 報告

`archives/agents/TODO-049/reviewer-report.md` に書くこと。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。

指摘は**重さの順に並べ、それぞれ「何が起きるか」を具体的に**書くこと。
「気になる」だけでなく、どういう入力・操作で問題になるかまで。
