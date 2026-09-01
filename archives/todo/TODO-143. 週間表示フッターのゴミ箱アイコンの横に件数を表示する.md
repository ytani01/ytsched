# TODO-143. 週間表示フッターのゴミ箱アイコンの横に件数を表示する

|        | main                  | 担当                    |
| ------ | --------------------- | ----------------------- |
| 見込み | Opus 5 / effort high  | implementer + verifier  |
| 実施   | Opus 5 / effort high  | implementer + verifier  |
| 消費   | output 9,750 / cache_creation 86,097 / 概算 $1.1 | |
|        | main 50% + implementer 35% + verifier 15%（料金の割合） | |

分担の理由、依頼、報告は
[archives/agents/TODO-143/README.md](../agents/TODO-143/README.md) にある。

## きっかけ

週間表示のフッターにはゴミ箱アイコンがあるだけで、中身があるかどうかが
画面から分からなかった。アイコンの横に件数を出す。

0 件のときも「0」を出す（数字が消えると位置が動くため。利用者が選択）。

## やったこと

- `TrashFile.count()` を足した。ファイルが無ければ 0。壊れた行は
  `entries()` と同じ考え方で飛ばす。ただし `SchedDataEnt.from_dict()`
  までは呼ばず、JSON として読めるかと `trashed_at` が文字列かだけを見る。
  `entries()` は `max_entries=100` で頭打ちになるので件数には使えない
- `MainHandler.get()` の `render()` に `trash_count` を渡した
- `main.html` のフッターで、ゴミ箱アイコンの右に `({{ trash_count }})`
  を出した。見た目は同じフッターの `cache_size` の表示に揃え、既存の
  クラスだけを使って CSS は増やしていない

## テスト

- implementer: `tests/test_trash.py` に `count()` のテストを 4 件追加
  （ファイル無し、複数件、壊れた行が混ざる、100 件を超える）
- implementer: `tests/test_web.py` に週間表示の件数表示のテストを 2 件追加
  （0 件のとき、2 件のとき）
- implementer: `uv run pytest` — 589 件通過。`ruff format` /
  `ruff check` / `basedpyright` / `mypy` — 通過
- verifier: `uv run pytest` — 589 件通過。`ruff format --check` /
  `ruff check` / `basedpyright` / `mypy` — 通過
- verifier: `--datadir` に一時ディレクトリを指定してアプリを起動し、
  curl で HTML を取得。0 件で `(0)`、105 件で `(105)` を確認
  （`max_entries=100` に引きずられていない）
