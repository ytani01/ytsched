# TODO-086. ゴミ箱について UI 追加

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | GPT-5 / effort high | implementer + verifier + reviewer |

分担と各担当の報告は
[archives/agents/TODO-086](../agents/TODO-086/README.md) にある。

## きっかけ

TODO-085 で削除・編集前の予定を `trash.jsonl` へ追記するようにしたが、
読み出しと復活する手段はまだなかった。

## やったこと

- `/ytsched/trash` にゴミ箱画面を追加した。一覧画面のハンバーガーメニューと
  編集画面の「元に戻す」から同じ画面を開ける
- 同じ `sde_id` の候補をまとめ、削除日時、日付・時刻・種別・タイトル・場所・
  詳細を見比べて、それぞれを選べるようにした
- `TrashMax`（既定 100）件を新しい順に表示する。`sde_id` を指定した入口では、
  その ID に絞る
- 復活は選んだゴミ箱行を残したまま、対象日の新規予定として追加する。新しい ID
  を発行し、タイトルの先頭に `(復活)` を付け、対象日の週へリダイレクトする
- 同じ ID を短時間に複数回削除しても復活対象を区別できるよう、`trashed_at` を
  ISO 8601 のマイクロ秒精度で記録するようにした
- データ形式とソース構成の文書を更新した

## テスト

- `uv run ruff format --check src/ytsched/trash.py tests/test_trash.py`
- `uv run ruff check src/ytsched/trash.py tests/test_trash.py`
- `uv run pytest tests/test_trash.py tests/test_web.py -q` — 138 passed
- `uv run pytest tests -q` — 529 passed
- verifier による一時データディレクトリでの起動・`/ytsched/trash` の HTTP 200・
  テンプレート展開を確認
- reviewer が復活対象の一意性を確認し、修正後に指摘なし
