# TODO-027 verifier への依頼（4 回目）

4 回目の実装が終わった。**動くかどうかを確かめてほしい。コードは
直さないこと。**

3 回目の確認では `pytest` が走らせられなかったが、その原因
（`WebServer.URL_PREFIX` の追随漏れ）は TODO-033 で直った。
**今回はテストも走る。**

**注意: この項目の変更はまだコミットされていない。**
`git checkout` / `git restore` / `git stash` など、作業ツリーを戻す
コマンドは絶対に使わないこと。

## 読むもの

- `archives/agents/TODO-027/implementer-request4.md`（依頼した内容）
- `archives/agents/TODO-027/implementer-report4.md`（実装者の報告）
- `archives/agents/TODO-027/reviewer-report3.md`（指摘の元）
- 自分の前回の報告 `verifier-report3.md`
- 変更そのものは `git diff`（**読むだけ**）

## 今回の変更の要点

更新経路（`cmd=add`/`fix`/`update`/`del`）で、日付・時刻の引数が
**空でないのに読めない**ときは、`HTTPError(400)` で断るようになった。
**書き込みが 1 つも起きる前に弾く**のが肝。
空のときの扱いは変わっていない（`date` が空 → 今日、`orig_date` が
空 → ToDo のファイル）。

## 確かめてほしいこと

1. `uv run ruff format --check --line-length 78 src tests` /
   `uv run ruff check --extend-select I src tests` /
   `uv run basedpyright src tests` / `uv run mypy src tests` /
   `uv run pytest tests` を順に走らせ、**出力をそのまま報告する**
2. **400 になり、かつデータが 1 行も変わらないこと**を curl で自分で
   再現する。一時ディレクトリに `ToDo.jsonl` と日付ごとのファイルを
   置いて `--datadir` に指定し、叩く前と後で **`datadir` 以下の全
   ファイルの中身を比べる**（`diff -r` でよい）。
   - `?cmd=add&date=abc&title=t&sde_id=`
   - `?cmd=add&date=9999-12-31&title=t&sde_id=`
   - `?cmd=del&orig_date=abc&sde_id=<ToDo の sde_id>`
   - `?cmd=update&orig_date=abc&date=<正しい日付>&sde_id=…`
   - `?cmd=update&orig_date=<正しい日付>&date=9999-12-31&sde_id=…`
     （**元の予定が動いていないこと**）
   - `?cmd=add&date=<正しい日付>&time_start=abc&title=t&sde_id=`
     （**500 でなく 400** であること）
   - `time_end=abc` / `time_start=25:00` も同じ
3. **正しい操作が壊れていないか。ここを念入りに。**
   ブラウザからの普通の操作と同じ順で curl を叩き、
   - 新規追加（`cmd=add`）で狙った日のファイルに入るか
   - `cmd=fix` で**別の日へ動かしたとき**、元の日から消えて新しい日に
     1 件だけ入るか（**重複していないか**）
   - `cmd=del` で消えるか
   - ToDo（`orig_date` を送らない）の追加・修正・削除が今までどおりか
   - **`date` を空で送ったとき**に今日のファイルへ入るか
     （TODO-016 の「空 ＝ 省略」が生きているか）
4. **表示経路（GET）が今までどおり既定値へ落ちるか。**
   ここは 400 にしない約束。`?date=abc` / `?cur_day=abc` /
   `?search_n=abc` / `?todo_days=abc` / `?year=2021&month=13&day=1` /
   `/edit?date=abc` を叩いて、**200 が返る**ことを見る
5. 警告ログが実際に出ているか
6. 確かめ終わったら、起動したサーバを止める

## 決まりごと

- **コードは直さない**
- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。`--datadir` に必ず一時
  ディレクトリを指定する
- **アプリを起こすポートは 8891 を使う**（別の担当が同時に動いている）
- 報告は `archives/agents/TODO-027/verifier-report4.md` に書く。
  返事は 5 行以内
