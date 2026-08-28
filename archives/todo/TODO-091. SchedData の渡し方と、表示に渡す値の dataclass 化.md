# TODO-091. `SchedData` の渡し方と、表示に渡す値の dataclass 化

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer + verifier |
| 消費 | output 27,061 / cache_creation 221,722 / 概算 $2.2 |
|      | main 60% + implementer 20% + verifier 14% + wording 5%（料金の割合） |

基本設計のレビュー（2026-08-27）の G・H。分担の理由と各担当の報告は
[archives/agents/TODO-091/](../agents/TODO-091/) にある。

## きっかけ

- `sd=self._sd` は、データを持つオブジェクトがそのままテンプレートに
  入る唯一の経路だった。テンプレートからは `SchedData` のどのメソッドも
  呼べたが、実際に使っていたのは `main.html` の `sd.get_cache_size()`
  1 つだけ。
- `SchedLoader.load_week()` / `search()` が返す `sched` は
  `date` / `is_holiday` / `sde` の 3 キーを持つ `list[dict]`、
  `mk_weeks()` が作る `weeks` は `offset` / `monday` / `sched` を持つ
  `list[dict[str, object]]` で、テンプレートも tests も文字列でキーを
  引いていた。キー名を変えても型チェッカは気づかない。

## やったこと

- `sched_load.py` に dataclass を 2 つ追加。
  - `SchedDay`: `date` / `is_holiday` / `sde`
  - `SchedWeek`: `offset` / `monday` / `sched`（`list[SchedDay]`）
- `_load_day()` が返す `day` を `SchedDay` に。`load_week()` / `search()`
  の戻り値注釈を `list[SchedDay]` に。`search()` の
  `if not day["sde"]:` を `if not day.sde:` に。
- `main_handler.py` `mk_weeks()` が返す各週を `SchedWeek` に。引数・
  戻り値・変数の注釈も合わせた。
- `render()` へ渡すのを `sd=self._sd` から
  `cache_size=self._sd.get_cache_size()` に変更。**キャッシュ件数の
  表示は残す**（版数の隣に小さく出している値。消すかどうかは別途決める
  ことなので、この項目では触らない）。
- `main.html`: 週ループの `w['offset']` などの添字を `w.offset` の
  属性参照に。`sched_ent['date']` / `sched_ent['sde']` も同様。
  版数の隣を `({{ cache_size }})` に。
- `tests/test_main_handler.py`: `TestLoadSchedScan` の
  `s["date"]` / `s["is_holiday"]` / `day["sde"]` を属性参照に。
  `skipped == opened` の比較は dataclass の `__eq__` でそのまま通る。

挙動は変えていない。`monday` を省略できる型にはしない（検索モードでも
実際の月曜が入る。`data-monday` を出すかは `main.html` が `search_mode`
で決める。TODO-088）。

## テスト

- `mise run test` 482 passed、`mise run typecheck` 0 errors
  （basedpyright / mypy）、`mise run lint` 通過。
- `uv run ytsched webapp --datadir <一時ディレクトリ>` で起動。
  `GET /ytsched/` と検索モード（`?date=...&search_str=会議`）が
  ともに 200。テンプレートに `{{` `{%` の生残りなし。版数の隣に
  キャッシュ件数が出る。サーバログに例外なし。
- 複数週での属性参照は、`test_web.py` / `test_browser.py` が実
  テンプレートで通っていることで確認できている（空の一時 datadir では
  週パネルが 1 個だが、これは変更前と同じ出力で回帰ではない）。
