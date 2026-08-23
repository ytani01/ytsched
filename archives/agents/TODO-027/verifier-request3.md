# TODO-027 verifier への依頼（3 回目）

3 回目の実装が終わった。**動くかどうかを確かめてほしい。コードは
直さないこと。**

**注意: この項目の変更はまだコミットされていない。**
`git checkout` / `git restore` / `git stash` など、**作業ツリーを戻す
コマンドは絶対に使わないこと**（3 回目の implementer が
`git checkout -- src` で未コミットの実装を一度消している）。

## 読むもの

- `archives/agents/TODO-027/implementer-request3.md`（依頼した内容）
- `archives/agents/TODO-027/implementer-report3.md`（実装者の報告）
- `archives/agents/TODO-027/reviewer-report2.md`（指摘の元）
- 自分の前回の報告 `verifier-report2.md`
- 変更そのものは `git diff`（**読むだけ**）

## 確かめてほしいこと

1. `uv run ruff format --line-length 78 src tests` /
   `uv run ruff check --extend-select I src tests` /
   `uv run basedpyright src tests` / `uv run mypy src tests` /
   `uv run pytest tests` を順に走らせ、**出力をそのまま報告する**
2. **3 回目の実装者の報告にある表を、自分で再現する。** 一時ディレクトリに
   `ToDo.jsonl` を 1 件置いて `--datadir` に指定し、アプリを起こして curl で:
   - `?year=2021&month=99999999999&day=1` / `?year=2021&month=1&day=99999999999`
     / `?year=2021&month=1&day=-99999999999` / `?year=2021&month=13&day=1`
   - `/edit?date=abc` / `/edit?date=9999-12-31`（**今日の日付が入って
     いるか**まで見る）
   - `?cmd=add&date=abc&title=test1&sde_id=` /
     `?cmd=add&date=9999-12-31&title=test2&sde_id=`
     （**どのファイルに書かれたか**を確かめる。今日のファイルのはず。
     `ToDo.jsonl` が汚れていないか）
   - `?cmd=del&orig_date=abc&sde_id=<ToDo の sde_id>`
     （**`ToDo.jsonl` の中身が消えていないか**）
3. **1・2 回目に確かめたものが壊れていないか。** 前回までの報告と同じ
   手順で、`search_n=abc` / `todo_days=abc` / `todo_days=99999999999` /
   `date=9999-12-31` などを叩き直す
4. **正しい操作が壊れていないか。ここを念入りに。** 3 回目は
   **データを書き込む経路**を触っている。ブラウザからの普通の操作と
   同じ順で curl を叩き、
   - 新規追加（`cmd=add`）で狙った日のファイルに入るか
   - 追加した予定を `cmd=fix` で**別の日へ動かしたとき**、元の日から
     消えて新しい日に 1 件だけ入るか（**重複していないか**）
   - `cmd=del` で消えるか
   - ToDo（`orig_date` を送らない）の追加・修正・削除が今までどおりか
5. 警告ログが実際に出ているか
6. 確かめ終わったら、起動したサーバを止める

## 決まりごと

- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。`--datadir` に必ず一時
  ディレクトリを指定する
- 報告は `archives/agents/TODO-027/verifier-report3.md` に書く。返事は 5 行以内
