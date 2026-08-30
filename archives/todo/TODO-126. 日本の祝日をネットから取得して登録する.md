# TODO-126. 日本の祝日をネットから取得して登録する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | implementer + verifier |
| 消費 | output 17,726 / cache_creation 162,591 / 概算 $2.4 |
|      | main 74% + implementer 20% + verifier 6%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-126](../agents/TODO-126/README.md) にある。

## きっかけ

祝日は毎年手で入れていた。実データには `type` が `休日` の予定が 670 件
あり、2026・2027 年分は既に入っている。これを CLI から入れられるようにした。

## やったこと

- `src/ytsched/holiday.py` を新規作成
  - `fetch()` — `urllib.request` で CSV を取得（bytes のまま返す）
  - `parse()` — CP932 でデコードし、`csv` モジュールで
    `(datetime.date, 名称)` のリストにする。1 行目の見出しは捨てる。
    壊れた行は警告を出して飛ばす（`migrate.py` の方針と揃えた）
  - `HolidayRegistrar` — 対象の年だけ `SchedData.add_sde()` で足し、
    最後に 1 回 `save()`。`--dry-run` では `save()` を呼ばない
- `src/ytsched/__main__.py` に `holiday` サブコマンドを追加
  （`--datadir` / `--dry-run` / `--url` / `--debug`、年は
  `nargs=-1, required=True`）
- `tests/test_holiday.py` と `tests/data/syukujitsu-sample.csv` を新規作成
- `docs/Developer.md` にコマンドの説明、`tests/README.md` にテストの行を追加

既存の読み書き・キャッシュ・画面のコードは触っていない。

## 決めたこと

- **取得元は内閣府の CSV**
  （`https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv`）。
  一次情報で、依存も増えない（`urllib.request` と `csv` で足りる）。
  holidays-jp API と `jpholiday` パッケージも見たが採らなかった
- **登録する形は CSV のまま。** `type` は `休日`、`title` は CSV の名称
  （`元日`、振替休日と国民の休日は `休日`）。既存データは表記が違う
  （`元旦`、`国民の祝日`）が、**変換表は持たない**。保守するほうが手間になる
- **重なりは、同じ日付で `title` も一致するときだけ飛ばす**（`type` は
  見ない）。したがって既に `元旦` が入っている 2026-01-01 に
  `ytsched holiday 2026` を走らせると `元日` が足される
- **CSV に無い年は「データが無い」と報告して飛ばし、他の年は続ける。**
  CSV の範囲は 1955 年から翌年分までで、指定された年が無いことがある
- **年を省いたらエラー。** 当年と翌年を勝手に補ったりはしない
- **`--url` に `file://` を渡せる**（`urllib.request` がそのまま扱う）ので、
  ネットに出ずに CLI 全体を手元で確かめられる。実装と確認の両方で使った

## テスト

`tests/test_holiday.py` は 7 本。**ネットへ出ない**（`fetch()` を呼ばず、
`tests/data/syukujitsu-sample.csv` を解析させる）。CP932 のデコード、
`YYYY/M/D` の解析、指定年での絞り込み、CSV に無い年、重なりの判定
（同題は飛ばす／別題は足す）、`--dry-run` でファイルが増えないこと。

verifier が確かめた結果:

- `mise run lint` — 通過
- `uv run pytest tests` — 543 passed
- `uv run ytsched holiday --help` が出ること、年なしで
  `Error: Missing argument 'YEARS...'`（exit code 2）になること
- 一時ディレクトリと `file://` の CSV で、`--dry-run` はファイルを作らず、
  本番では `2026/01/01.jsonl` などができ、中身が
  `"type": "休日"` / `"title": "元日"` / `time_start`・`time_end` が null
  であること。2 回目は 3 件とも飛ばされ、行数が増えないこと。
  `2026 2030` では 2030 が「データが無い年」と報告され、2026 は続くこと
- 本物のネットからの取得を `--dry-run` で 1 回だけ確認（`足した予定: 18`、
  例外なし）
