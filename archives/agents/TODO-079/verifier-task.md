# TODO-079 verifier への依頼

TODO-079（表示の条件を dataclass にまとめ、`load_sched()` の引数を減らす）
の実装が終わった。実際に動くかを確かめてほしい。

**挙動は変えない項目**なので、「変わっていないこと」を見るのが本題。

- 実装の報告: `archives/agents/TODO-079/implementer-report.md`
- 依頼書: `archives/agents/TODO-079/implementer-task.md`
- 背景: `TODO.md` の TODO-079、`docs/design-review.md` の F

## 確かめてほしいこと

1. `mise run lint` と `uv run pytest tests` を走らせ、結果をそのまま報告する
2. **HTML が変わっていないこと。** 実装者は 1 つの URL で確かめたと
   報告しているが、**条件を変えた複数のパターン**で見てほしい。
   変更前のコードは `git worktree add <一時dir> HEAD` で用意すること
   （`git stash` は auto mode に拒否されることがある）。
   同じデータを両方の datadir に置き、次の URL の HTML を突き合わせる
   - 何も付けない（`/`）
   - `?date=` で今日から離れた週
   - 検索したとき（`search_str` を付ける。`POST` が要る）
   - 絞り込み（`filter_str`）を付けたとき
   - ToDo の日数（`todo_days`）を変えたとき、負の値のとき
   - `conf.json` の `LoadMonths` を 0 と 2 にしたとき
   **日付やセッションで変わる部分は除いて比べること**（差が出たら、
   何が違うのかを報告に書く）
3. 週を 9 週ぶん返すとき、`mk_todo_by_date()` が 1 回しか呼ばれない
   ことを、実際に走らせて確かめる（テストが 1 本あるが、それとは別に
   ログや spy で見てもよい）
4. アプリを起動して、画面が今までどおり出ること

## 決まりごと

- **コードを直さない。** 見つけたことは報告するだけ
- 報告は `archives/agents/TODO-079/verifier-report.md` に書く。返事は 5 行以内
- **`mise run upgradeproject` は走らせない**
- `~/ytsched/data` の実データを触らない。必ず `--datadir` を指定する
