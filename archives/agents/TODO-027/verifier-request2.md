# TODO-027 verifier への依頼（2 回目）

reviewer の指摘を受けた 2 回目の実装が終わった。**動くかどうかを確かめて
ほしい。コードは直さないこと。**

## 読むもの

- `archives/agents/TODO-027/implementer-request2.md`（依頼した内容）
- `archives/agents/TODO-027/implementer-report2.md`（実装者の報告）
- `archives/agents/TODO-027/reviewer-report.md`（指摘の元）
- 1 回目の `verifier-report.md`（自分の前回の報告）
- 変更そのものは `git diff`

## 確かめてほしいこと

1. `uv run ruff format --line-length 78 src tests` /
   `uv run ruff check --extend-select I src tests` /
   `uv run basedpyright src tests` / `uv run mypy src tests` /
   `uv run pytest tests` を順に走らせ、**出力をそのまま報告する**
2. **実装者の報告にある表を、自分で再現する。** 一時ディレクトリに
   `ToDo.jsonl` を 1 件置いて `--datadir` に指定し、アプリを起こして
   curl で叩く。`year=99999999999&month=1&day=1` / `date=9999-12-31` /
   `date=0001-01-01` / `year=9999&month=12&day=31` /
   `todo_days=99999999999` / `todo_days=-99999999999` について、
   **1 回目が 200 か、次の素の GET が 200 か、`Conf.cgi` に残らないか**
3. **1 回目に確かめた 8 通り（`search_n=abc` など）が壊れていないか。**
   前回の報告と同じ手順で叩き直す
4. **正しい値が壊れていないか。** `search_n=10` / `todo_days=7` /
   `todo_days=-1`（off）/ `date=2021-01-02` /
   `year=2021&month=1&day=2` が今までどおり効き、`Conf.cgi` に保存
   されるか。`todo_days=7` を保存したあと `todo_days=99999999999` を
   叩いても `7` のままか
5. **検索モードが壊れていないか。** 実装者は日付の使える範囲を
   「`SEARCH_MODE_MAX_DAYS`（5 年）だけ内側」にしたと書いている。
   `search_str` を入れた検索（5 年さかのぼる）が今までどおり動くか
6. 警告ログが実際に出ているか。何がどう不正だったか（範囲も）分かる形か
7. 確かめ終わったら、起動したサーバを止める

## 決まりごと

- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。`--datadir` に必ず一時
  ディレクトリを指定する
- 報告は `archives/agents/TODO-027/verifier-report2.md` に書く。
  返事は 5 行以内
