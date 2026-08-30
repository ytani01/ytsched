# TODO-126 implementer への依頼

## 目的

`ytsched holiday {年}...` サブコマンドを足し、内閣府の CSV から日本の祝日を
取得してデータへ登録できるようにする。仕様は `TODO.md` の TODO-126 の節が
正で、**そちらを必ず読むこと**（背景・取得元・登録する形・重なりの扱い・
CLI の形・テストの方針が書いてある）。ここには、それに足す指示だけ書く。

## 対象範囲

新規: `src/ytsched/holiday.py`、`tests/test_holiday.py`、
`tests/data/syukujitsu-sample.csv`
変更: `src/ytsched/__main__.py`、`docs/Developer.md`、`tests/README.md`

**既存の読み書き・キャッシュ・画面のコードは触らない。**

## 実装の指示

- `holiday.py` は `migrate.py` の書き方に揃える。取得と解析を関数で分け、
  登録をクラス（`Migrator` に倣った名前）に持たせる
  - 取得: `urllib.request` で URL を読み、bytes を返す関数
  - 解析: bytes を受けて `list[tuple[datetime.date, str]]` を返す関数。
    CP932 でデコード、CRLF、1 行目は見出しなので捨てる、`YYYY/M/D,名称`。
    `csv` モジュールを使う。**壊れた行は警告を出して飛ばし、例外にしない**
    （`migrate.py` の方針と揃える）
  - 登録: `SchedData(topdir)` を使い、`add_sde()` で足して最後に 1 回
    `save()`。`--dry-run` のときは `save()` を呼ばない
- 重なりの判定は、その日の `SchedDataFile` の `sde` を見て
  **日付が同じかつ `title` が一致**するものがあれば飛ばす
  （`type` は見ない。TODO.md の「重なりの扱い」のとおり）
- 指定された年が CSV に無ければ、その年は警告を出して飛ばし、
  他の年の処理は続ける。**エラー終了にしない**
- 年を 1 つも渡さなければエラー（click の `required=True`）
- 結果の出力は `Migrator.main()` の `print` の形に揃える。
  足した件数・飛ばした件数、`--dry-run` のときは冒頭に dry run の断り
- ログは `mylog.py` のラッパ。クラス本体に
  `__log = getLogger(__qualname__)` を 1 つ
- CLI は `__main__.py` に `migrate` と同じ形で足す。`--datadir` の既定は
  `SchedDataFile.DEF_TOP_DIR`、`--dry-run`、`--url`、`--debug`

## テスト

`tests/test_holiday.py`。**ネットへ出ない**（取得の関数は呼ばない）。

- `tests/data/syukujitsu-sample.csv` を新規作成する。
  **CP932・CRLF・見出し行あり**の本物と同じバイト形式。中身は本物からの
  抜粋で、次の行を入れる（Python スクリプトで書き出すのが確実）:
  見出し `国民の祝日・休日月日,国民の祝日・休日名称`、
  `1955/1/1,元日`、`2026/1/1,元日`、`2026/5/3,憲法記念日`、
  `2026/5/6,休日`、`2027/1/1,元日`、`2027/3/22,休日`
- 見るもの:
  1. CP932 のデコード（`憲法記念日` などが読めること）
  2. `YYYY/M/D` の解析（`2026/1/1` → `datetime.date(2026, 1, 1)`）
  3. 指定年での絞り込み（2026 を指定したら 2026 の 3 件だけ）
  4. CSV に無い年（例: 2030）を指定したら、飛ばして他は続くこと
  5. 重なりの判定（同じ日付・同じ `title` は飛ばす。`title` が違えば足す）
  6. `--dry-run` でファイルが増えないこと
- 一時ディレクトリは pytest の `tmp_path`。`~/ytsched/data` は絶対に触らない

## 文書

- `docs/Developer.md` の「個別コマンドで実行する場合」に `ytsched holiday`
  の例を足し、オプション表・取得元 URL・重なりの扱い（同じ日付で `title`
  が一致すれば飛ばす）・CSV に無い年の扱いを簡潔に書く
- `tests/README.md` の一覧に `test_holiday.py` の行を足す

## 完了条件

- `mise run lint` と `uv run pytest tests` が通る
- `uv run ytsched holiday --help` が出る
- 一時ディレクトリを `--datadir` に指定して `--dry-run` と本番の両方を
  実際に走らせ、`.jsonl` が書かれることを自分で確かめる
  （**`~/ytsched/data` は使わない**）

## 報告

`archives/agents/TODO-126/implementer-report.md` に書く。60 行以内。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
