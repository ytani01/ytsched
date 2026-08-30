# TODO-086 implementer 報告

## 変更

- `src/ytsched/trash.py` — `trash.jsonl` を ID で絞り込み、新しい順・上限付きで読む `TrashEntry` / `entries()` / `get()` を追加。
- `src/ytsched/trash_handler.py` — ゴミ箱の表示と、`sde_id` と `trashed_at` で選んだ 1 行を新規予定として復活する処理を追加。
- `src/ytsched/webapp.py`、`tests/helpers.py` — `/ytsched/trash` のルートを登録。
- `src/ytsched/webroot/templates/trash.html`、`main.html`、`edit.html`、`my.css`、`icons.svg` — ゴミ箱画面、一覧・編集画面の入口、`rotate-left` アイコンを追加。
- `docs/data-format.md`、`src/README.md` — ゴミ箱の読み出し・復活の仕様とモジュールを記載。
- `tests/test_trash.py`、`tests/test_web.py` — 絞り込み・新しい順・上限、同 ID の表示、復活後の新 ID・タイトル・PRG、既存データとゴミ箱を残すことを確認。

## 基本確認

- `uv run ruff format --check ...` — 成功。
- `uv run ruff check ...` — 成功。
- `uv run pytest tests/test_trash.py tests/test_web.py -q` — 137 passed。
- `git diff --check` — 成功。

## 判断

- `TrashMax` は未設定・数値でない・0 以下のとき既定値 100 とした。空の一覧になるより設定の誤りに強い既存設定と同じ扱い。
- ゴミ箱の壊れた行は警告して読み飛ばす。既存データの JSON Lines 読み出しと揃えた。

## 残したもの

- TODO-086 の範囲外の TODO.md とコミットは変更していない。
