# TODO-143 verifier への依頼

## 目的

TODO-143（週間表示フッターのゴミ箱アイコンの横に件数を表示）の実装が
実際に動くかを確かめる。**コードは直さない。** 見つけたことは報告する。

## 対象範囲

未コミットの差分（`git diff`）。`src/ytsched/trash.py`,
`src/ytsched/main_handler.py`,
`src/ytsched/webroot/templates/main.html`, `tests/test_trash.py`,
`tests/test_web.py`。

implementer の報告は `archives/agents/TODO-143/implementer-report.md`。

## 確かめること

- `uv run pytest` が通る
- `uv run ruff format --check` / `uv run ruff check` /
  `uv run basedpyright` / `uv run mypy` が通る
- **実際にアプリを起動して、週間表示のフッターに件数が出ることを見る。**
  `--datadir` に一時ディレクトリを指定すること（実データを汚さない）。
  0 件のとき「0」が出ること、ゴミ箱に入れたあと件数が増えることを、
  curl で HTML を取って確かめる
- `TrashFile.count()` が 100 件を超えても正しく数えること
  （`entries()` の `max_entries=100` に引きずられていないこと）

## 報告

`archives/agents/TODO-143/verifier-report.md` に、実行したコマンドと
その結果、見つけた問題を書く。返事は 5 行以内。
