# TODO-166 verifier への依頼

## 目的

TODO-166（月間表示の先読み画面数を `conf.json` の `LoadMonthPages` で
変えられるようにする）の実装が、実際に動くかを確かめる。

仕様は `TODO.md` の TODO-166 の節、実装の内容は
`archives/agents/TODO-166/implementer-report.md` にある。

## 見る範囲

`git diff`（未コミット）の分。`archives/agents/TODO-166/` は依頼と報告なので対象外。

## 確かめること

1. `uv run ruff format --check` / `uv run ruff check` /
   `uv run basedpyright` / `uv run pytest` が通ること
2. 実際にアプリを起動して、月間表示（`?view=month`）の
   `my-month-panel` / `data-block=` の数が設定どおりに変わること
   - `LoadMonthPages` 未設定 → 5 ブロック
   - `0` → 1 ブロック、`10` → 21 ブロック
   - 範囲外（`11`、`-1`）・数字でない値 → 既定の 5 ブロックに落ち、
     警告ログが出ること
   - **`--datadir` には必ず一時ディレクトリを指定する**（実データを汚さない）
3. 週間表示（`view=week`）が今までどおりであること（`LoadMonths` に影響が無い）
4. 文書（`src/README.md`・`docs/User.md`・`tests/README.md`）の記述が
   実装と食い違っていないこと

## やらないこと

- **コードは直さない。** 見つけたことは報告するだけ
- `mise run upgradeproject` は走らせない
- `TODO.md` / `archives/todo/` は触らない

## 報告

`archives/agents/TODO-166/verifier-report.md` に、確かめたこと・結果・
見つかった問題を書く。返事は 5 行以内。
