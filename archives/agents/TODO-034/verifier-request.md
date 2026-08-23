# TODO-034 verifier への依頼

## 何をした変更か

`TODO.md` の TODO-034 を main が実装した。挙動は変えていないつもりの
片付けが 2 つ。

1. `src/ytsched/webroot/templates/sde.html` が `doPost()` に載せていた
   `orig_date` を消した。受け取る `EditHandler.get()` は `orig_date` を
   読んでいない
2. `SchedDataFile.date2path()` の中で `os.path.expanduser()` を呼ぶように
   した。`SchedData.sdf_exists()` 側の `expanduser()` は消した。
   `SchedDataFile.__init__` の `self.topdir = os.path.expanduser(topdir)`
   は、外から読める属性なので残してある

`tests/test_ytsched.py` に `date2path()` 単独呼び出しのテストを 2 つ足した。

## 確かめてほしいこと

- `uv run ruff check src tests`、`uv run ruff format --line-length 78
  --check src tests`、`mise run typecheck`、`uv run pytest` を走らせて、
  出力をそのまま報告する
- アプリを起動して、一覧画面から予定をクリックして編集画面が出ること、
  編集画面で更新・削除ができることを確かめる。**`--datadir` には必ず
  一時ディレクトリを指定する**（`~/ytsched/data` を触らない）
- 編集画面の隠しフィールド `orig_date` が、今までどおり
  「その行が入っているファイルの日付」になっているか
  （ToDo のときは出ない）
- `~` 付きの `--datadir` でも今までどおり動くか

## 気をつけること

- **コードは直さない。** 見つけたことは報告するだけ
- 報告は `archives/agents/TODO-034/verifier-report.md` に書く。
  返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）
