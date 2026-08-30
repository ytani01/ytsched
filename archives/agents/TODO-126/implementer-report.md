# TODO-126 implementer 報告

## 変更したファイル

- 新規 `src/ytsched/holiday.py`: `fetch()`（取得）、`parse()`（解析）、
  `HolidayRegistrar`（登録、`Migrator` に倣った作り）。`is_duplicate()` は
  `SchedDataFile.sde` を見て日付・`title` の一致だけで判定（`type` は見ない）。
  指定年が CSV に無ければ警告して飛ばし、他の年は続ける
- 新規 `tests/test_holiday.py`: CP932 デコード・日付解析・年での絞り込み・
  CSV に無い年・重なりの判定（同題は飛ばす／別題は足す）・`--dry-run` で
  ファイルが増えないこと、の 7 本。ネットへは出ない
- 新規 `tests/data/syukujitsu-sample.csv`: CP932・CRLF で作成
  （依頼書どおりの 6 行 + 見出し）
- 変更 `src/ytsched/__main__.py`: `holiday` サブコマンドを `migrate` と同じ形で
  追加（`--datadir` / `--dry-run` / `--url` / `--debug`、年は
  `nargs=-1, required=True`）
- 変更 `docs/Developer.md`: 「個別コマンドで実行する場合」に
  `ytsched holiday` の例・オプション表・重なりの扱い・CSV に無い年の扱いを追加
- 変更 `tests/README.md`: `test_holiday.py` の行を追加

既存の読み書き・キャッシュ・画面のコードは触っていない。

## 自分で確かめたこと

- `uv run basedpyright` / `uv run mypy`（対象ファイル）: 0 errors
- `mise run lint`（fmt/typecheck/js 込み）: 全通過
- `uv run pytest tests -q`: 543 passed（既存分含め全体が通ることを確認）
- `uv run ytsched holiday --help`: 表示を確認
- 一時ディレクトリを `--datadir` に、`--url` に `file://.../tests/data/
  syukujitsu-sample.csv` を指定して `--dry-run` と本番を実際に実行。
  dry-run ではファイルが増えず、本番では `2026/01/01.jsonl` などが
  実際に書かれ、`type: 休日` / `title` が CSV のまま入ることを確認
  （2030 年は「データが無い年」として報告され、他の年は続いた）

## 判断したこと

- 依頼書に無い判断は特になし。依頼書・TODO.md の指示どおりに実装した
- `--url` に `file://` スキームを渡せる（`urllib.request` がそのまま扱う）
  ことを利用して、ネットに出ずに CLI 全体を手元で確かめた（テスト自体は
  `fetch()` を呼ばない方針のまま変更していない）

## 残さず全部直した

依頼の範囲はすべて実装済み。うまくいかなかった点はなし。
