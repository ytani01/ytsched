# TODO-027 verifier への依頼

TODO-027（不正な入力で 500 になるのをやめる）の実装が終わった。
**動くかどうかを確かめてほしい。コードは直さないこと**（見つけたことは
報告に書く。直すかどうかは main が決める）。

## 読むもの

- `TODO.md` の「TODO-027」の節
- `archives/agents/TODO-027/implementer-request.md`（依頼した内容）
- `archives/agents/TODO-027/implementer-report.md`（実装者の報告）
- 変更そのものは `git diff`（`src/ytsched/main_handler.py`,
  `tests/test_main_handler.py`, `tests/test_web.py`）

## 確かめてほしいこと

1. `uv run ruff format --line-length 78 src tests` /
   `uv run ruff check --extend-select I src tests` /
   `uv run basedpyright src tests` / `uv run mypy src tests` /
   `uv run pytest tests` を順に走らせ、**出力をそのまま報告する**
2. **実装者の報告にある表を、自分で再現する。** 一時ディレクトリを
   `--datadir` に指定してアプリを起こし、TODO-024 の表と同じ入力
   （`search_n=`（空）/ `search_n=abc` / `todo_days=abc` /
   `year=abc` / `month=13` / `day=32` / `date=abc` / `cur_day=abc`）を
   curl で叩く。**1 回目が 200 か、そのあとの素の GET が 200 か、
   `Conf.cgi` に不正な値が残っていないか**の 3 つを見る
3. `Conf.cgi` に `SearchN\tabc` / `ToDo_Days\tabc` を手で書いた状態から
   トップページが開けるか
4. **正しい値が壊れていないか。** `search_n=10` / `todo_days=7` /
   `date=2021-01-02` / `year=2021&month=1&day=2` が今までどおり効き、
   `Conf.cgi` に保存されるか
5. 警告ログが実際に出ているか（何がどう不正だったか分かる形か）
6. 確かめ終わったら、起動したサーバを止める

## 決まりごと

- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。`--datadir` に必ず一時
  ディレクトリを指定する
- 報告は `archives/agents/TODO-027/verifier-report.md` に書く。
  返事は「終わったか・報告のパス・判断が要る点」の 5 行以内
