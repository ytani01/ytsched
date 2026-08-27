# TODO-088 reviewer への依頼

TODO-088 の変更を見てほしい。**挙動を変えないための分割**なので、
「分ける前と後で挙動が変わっていないか」を最優先で見ること。

- 設計: `archives/agents/TODO-088/implementer-request.md`
- 実装の報告: `archives/agents/TODO-088/implementer-report.md`
- 変更範囲: `git diff`（新規の `src/ytsched/sched_load.py` も
  `git add -N` 済み）。分ける前のコードは
  `git show HEAD:src/ytsched/main_handler.py` の `load_sched()`

## 特に見てほしいところ

分ける前の `load_sched()` は、1 つの `while` の中に `search_mode` の
分岐が 4 か所あった。**それを 2 つのメソッドに書き分けたので、
条件の写し間違いが起きやすい。**

1. **検索の打ち切り**（`search()`）
   - 判定はループの先頭で、**1 件以上当たっているときだけ**行うか
   - 「目標件数に達した」と「365 日さかのぼった」の**順序**、
     どちらのときも `date_from = date1` にしてから抜けるか
   - `date_from` の初期値（`SEARCH_MODE_MAX_DAYS`＝1,825 日前）と、
     1 件も当たらなかったときの `date_from`
   - **数えるのはファイルから当たった件数だけ**か（ToDo は数えない）
2. **1 件も当たらない日**を、検索では落とし、通常モードでは残すか。
   **ToDo だけが当たった日は検索でも残る**（元は ToDo を足したあとに
   `if not out_sde` を見ていた）
3. **並び順**。`sched` が日付の昇順か（元は `sched[::-1]`）。
   1 日の中の `sde` の並びが変わっていないか
   （ファイル → `todo_by_date` → `todo_today_sde` の順に足してから
   ソート。同着のときの並びに効く）
4. `todo_today_sde` を足すのが**通常モードの今日だけ**か
5. `todo_days_value < 0` のときに ToDo を混ぜないところ
6. ファイルが無い日を開かない（`sdf_exists()`。TODO-028）が
   両方に残っているか
7. `SchedLoadCond` から外した `search_re` / `search_n` / `todo_sde` が、
   本当にどこからも要らなくなっているか
8. `main.html` の `data-monday` の条件を
   `{% if w['monday'] %}` から `{% if not search_mode %}` へ変えたことで、
   出力される HTML が変わらないか
9. `get()` から出した `mk_weeks()` が、元の `for offset in range(...)` と
   同じ範囲・同じ順序で週を作っているか

## 見なくてよいもの（既知）

- `mk_todo_by_date()` の二重の `search_match()`、`SEARCH_MODE_DAYS` /
  `SEARCH_MODE_MAX_DAYS` の名前（どちらも TODO-094）
- `load_week()` / `search()` が `list[dict]` を返すこと、
  `sd=self._sd` をテンプレートへ渡すこと（TODO-091）
- テンプレートの掃除（TODO-092）

報告は `archives/agents/TODO-088/reviewer-report.md`。返事は 5 行以内。
