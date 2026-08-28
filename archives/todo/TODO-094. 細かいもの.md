# TODO-094. 細かいもの

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | verifier |
| 実施 | Sonnet 5 / effort medium | verifier + wording |
| 消費 | output 33,894 / cache_creation 362,615 / 概算 $2.7 |
|      | main 82% + wording 12% + verifier 6%（料金の割合） |

基本設計のレビュー（2026-08-27）の P のうち、直す 3 件。`wording` は、
コミットに `.md`（この文書と `archives/agents/TODO-094/`）が入るため足した。

## きっかけ

基本設計のレビューで挙がった細かい 3 点。

1. `SEARCH_MODE_DAYS`（365）と `SEARCH_MODE_MAX_DAYS`（1825）は、
   名前が似ているのに意味が違う。
2. `mk_todo_by_date()` が `search_match()` をもう一度かけている。
3. CLI の `--size_limit` だけアンダースコアで、他（`--dry-run` /
   `--error-file`）とそろっていない。

着手時、1 について項目本文の説明（「前者は『1 件も当たらないときに
諦める日数』」）とコードの挙動が食い違っていることが分かった。コードでは
365 の打ち切りは `if search_count > 0` の中にあり、**1 件でも当たった
あと**の打ち切り。1825 はさかのぼりの絶対の上限。テスト
`test_search_mode_stops_365_days_after_first_hit` /
`test_search_mode_max_days_when_nothing_is_found` がこの挙動を押さえて
いる。コードの挙動を正として、名前を利用者に選んでもらった（2026-08-28）。

## やったこと

1. **定数の改名**
   - `SchedLoader.SEARCH_MODE_DAYS` → `SEARCH_ENOUGH_DAYS`
   - `handler_util.SEARCH_MODE_MAX_DAYS` → `SEARCH_HARD_LIMIT_DAYS`
   - `sched_load.py` のクラス変数コメントを、挙動に合わせて書き直した
     （旧「1 件も当たらないときに諦める日数（元 MainHandler.…）」→
     新「1 件でも当たったら、ここまで戻って検索を打ち切る日数」）。
   - `main_handler.py` / `ytsched.py` のコメント、`sched_load.py` の
     docstring、`tests/`（`test_handler_util.py` /
     `test_main_handler.py` / `test_web.py`）の参照も追随。テスト関数
     `test_date_range_margin_is_search_mode_max_days` は
     `..._search_hard_limit_days` に改名。

2. **`mk_todo_by_date()` の二重の `search_match()` を除去**
   - `mk_todo_by_date()` に渡る `todo_sde` は `load_todo()` が同じ
     `search_re` で `search_match()` 済みのもの。中の照合ループを
     `by_date.setdefault(...).append(sde)` だけにし、不要になった
     `search_re` 引数も外した。docstring にその旨を追記。
   - 呼び出し側（`main_handler.py`、`tests/test_main_handler.py` の
     `call_load_sched`）を追随。

3. **CLI オプション名**
   - `webapp` の `--size_limit` → `--size-limit`。短縮形 `-l` と
     click が渡す引数名 `size_limit`、`WebServer` への引数はそのまま。
     `--help` で `-l, --size-limit INTEGER` と出る。

## テスト

- `mise run fmt` / `typecheck`（basedpyright + mypy）/ `lint` /
  `test`（481 件）が通る。
- `uv run ytsched webapp --help` に `-l, --size-limit INTEGER`。
- `git grep 'SEARCH_MODE_DAYS\|SEARCH_MODE_MAX_DAYS'` は src/ tests/ で空。
- `tests/test_browser.py::test_tap_again_stops_auto_page_turn` が
  日付依存でときどき落ちる（`git stash` して変更なしでも再現）。
  TODO-094 とは無関係。

分担の理由と各担当の報告は
[archives/agents/TODO-094/README.md](../agents/TODO-094/README.md)。
