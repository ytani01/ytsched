# TODO-015 implementer 報告

ruff の整形・書き換え系の指摘 84 件を解消した。動作は変えていない。

## 変更したファイル

- `pyproject.toml` — `[tool.ruff.lint]` を新設し、`ignore = ["DTZ005", "DTZ011"]`
- `src/ytsched/__main__.py` — UP031 / C408
- `src/ytsched/edit_handler.py` — EXE001 / D419
- `src/ytsched/handler.py` — EXE001 / UP031 / D419
- `src/ytsched/main_handler.py` — EXE001 / UP031 / RUF012 / SIM102 / PERF402
- `src/ytsched/webapp.py` — EXE001 / UP031
- `src/ytsched/ytsched.py` — UP031 / D419 / RUF012 / PLC0206 / SIM118 /
  FLY002（noqa）
- `tests/helpers.py` — UP031
- `tests/test_web.py` — UP031 / FLY002（noqa）
- `tests/test_ytsched.py` — UP031 / FLY002（noqa）

新規作成・削除したファイルは無い。

## 規則ごとの対応

### DTZ011 / DTZ005（14 件）— 規則ごと除外

`pyproject.toml` に次を足した。`ignore` だけを書いたので、既定の
`select` は変わらず、`mise.toml` の `--extend-select I` とも衝突しない
（`I001` が今も出ることは、わざと乱した一時ファイルで確かめた）。

```toml
[tool.ruff.lint]
# 手帳代わりのソフトで、日付はすべて手元のローカル時刻。
# tz を付けて回ってもノイズにしかならないので、規則ごと除外する
# (TODO-015)。
ignore = ["DTZ005", "DTZ011"]
```

素の `uv run ruff check src tests` でも出なくなっていることを確認した。

### EXE001（4 件）— シェバンを消す

`edit_handler.py` / `handler.py` / `main_handler.py` / `webapp.py` の
1 行目 `#!/usr/bin/env python3` を消した。2 行目以降の
`# (c) ... Yoichi Tanibayashi` はそのまま。

### UP031（33 件）— f-string へ

まず `ruff check --fix --unsafe-fixes --select UP031` で `.format()` に
し、続けて `--select UP032` で f-string にした。ruff が変換しきれなかった
（複数行の `.format()` になった）4 箇所は手で書き換えた。

- `main_handler.py` の締切文字列: 一時変数 `deadline_date` を置いて
  3 行の f-string に分割
- `ytsched.py` `search_str()`: 一時変数 `detail` を置いた
- `ytsched.py` `get_sortkey()`: `"%02d%02d%02d %s"` →
  `f"{...:02d}{...:02d}"` + `f"{...:02d} {...}"`。`%02d` と `:02d` は
  最小桁数の指定なので、4 桁の年でも結果は同じ
- `__main__.py` の `print("%s" % (...))`: 一時変数 `dataline` を置いて
  `print(f"{dataline}")`

78 桁を超えた f-string（`SchedDataFile.__str__`）は暗黙の連結で分割した。
`ruff format --line-length 78` 後に 78 桁超の行が無いことを
`awk 'length($0)>78'` で確認した。

### FLY002（13 件）— 全部そのまま残した（noqa）

**13 箇所すべて `# noqa: FLY002` を付けて、`"\t".join([...])` のまま
残した。** 理由:

- 13 箇所とも「タブ区切りの 1 行を、項目を縦に並べて組み立てる」形。
  データ形式そのものを表しており、縦の並びが項目の順序と個数を見せている
- f-string にすると
  `"id-t\t2021/03/01\t:-:\t□買い物\tノートを買う\t\t"` のようになり、
  末尾の空項目 2 つが `\t\t` に潰れて数えないと分からない。
  依頼にある「テストの意図が読みにくくならないこと」を優先した
- 短い 2 箇所（`test_load_short_line` 系、項目が 4 つしか無い行）も、
  「項目が足りない行」を試すテストなので項目数が見える形を保った。
  同じ意味のものを 2 通りの書き方に分けたくなかった

`src/ytsched/ytsched.py` の `mk_dataline()` も同じ理由で残した。
**依頼では「テスト内の」とあったが、production 側にも 1 箇所ある。**
ここは保存形式を組み立てる本体なので、なおさら縦並びを崩さないほうが
よいと判断した。

各ファイルの最初の該当箇所に、理由を 2 行のコメントで添えてある。

### D419（10 件）— 日本語で中身を書いた

10 箇所すべて、消さずに日本語の docstring を書いた。

- `edit_handler.post()` — 「POST も GET と同じ処理をする。」
- `handler.load_conf/save_conf/get_conf/set_conf` — `Conf.cgi` の読み書き
- `ytsched.is_todo/is_holiday/is_important/is_canceled/get_sortkey` —
  何で判定しているか（`type` の先頭 / `title` の先頭）を添えた

### RUF012（5 件）— `ClassVar` を付けた

`SchedDataEnt.TYPE_HOLYDAY` / `TITLE_PREFIX_IMPORTANT` /
`TITLE_PREFIX_CANCELED`、`SchedDataFile.ENCODE`、
`MainHandler.TODO_DAYS` に `ClassVar[...]` を付けた。

`field(default_factory=...)` は使っていない（dataclass ではないし、
インスタンスごとに別のオブジェクトになると挙動が変わる）。
これらは全部読み取り専用で使われている（`grep` で全参照を確認済み。
`in` 判定、`for` の反復、テンプレートへの受け渡し、`self.ENCODE[0]`
のみ）ので、`ClassVar` の注釈だけなら実行時の挙動は変わらない。

### 残り 6 件

- `C408` `__main__.py` — `dict(help_option_names=[...])` →
  `{"help_option_names": [...]}`
- `SIM102` + `PERF402` `main_handler.py` — 入れ子の `if` を
  `if not search_mode and date1 == datetime.date.today():` にまとめ、
  `for sde in todo_today_sde: out_sde.append(sde)` を
  `out_sde.extend(todo_today_sde)` にした
- `PLC0206` `ytsched.py` `htmlstr2text()` — `for k in resub_tbl:` +
  `resub_tbl[k]` を `for k, v in resub_tbl.items():` にした。
  すぐ上のコメントアウト行も `replace_tbl[k]` → `v` に合わせた
  （元から死んだコメントだが、変数名が食い違ったまま残るのを避けた）
- `SIM118` `ytsched.py` `get_keys()` — `.keys()` を外した

## 単独で決めた判断

1. **FLY002 は 13 件すべて noqa で残した**（上記のとおり）。
   production 側の 1 件も含む
2. **RUF012 は `ClassVar`。** 現状の挙動を保つ安全側
3. **`print(f"{dataline}")`（`__main__.py`）。** `print(dataline)` でも
   同じだが、依頼の「f-string に書き換える」に素直に従った
4. **`webapp.py` / `helpers.py` の URL パターンは ruff が出した
   `rf"{self.URL_PREFIX}"` のまま採用した。** `r` は不要だが、
   「ここは正規表現」という元の意図を残す。`self.URL_PREFIX` を
   そのまま書く形にもできるので、簡単にするなら main の判断で
5. **`pyproject.toml` の `ignore` は `["DTZ005", "DTZ011"]` の
   2 個だけ書いた**（`"DTZ"` とまとめない）。他の DTZ 規則まで
   黙らせないため

## 直さずに残したもの（範囲外）

- `SchedDataFile.PATH_FORMAT = "%s/%04s/%02s/%02s.cgi"` /
  `TODO_PATH_FORMAT = "%s/ToDo.cgi"` は printf 書式のまま。
  リテラルへの直接の `%` 適用ではないので UP031 は出ておらず、
  この項目の対象外と判断した
- `ytsched.py` `htmlstr2text()` の中のコメントアウトされた行は、
  変数名だけ合わせて残した（消すのは範囲外）
- `handler.py` などに残る `""" """` 以外の英語 docstring
  （`"""__str__"""` など）は触っていない

## 実行したコマンドと結果

```
uv run ruff check --extend-select I src tests   → All checks passed!
uv run ruff check src tests                     → All checks passed!
uv run ruff format --line-length 78 --check src tests
                                                → 14 files already formatted
uv run basedpyright src tests                   → 0 errors, 0 warnings, 0 notes
uv run mypy src tests                           → Success: no issues found in 14 source files
uv run pytest tests -q                          → 174 passed
awk 'length($0)>78' src/ytsched/*.py tests/*.py → 出力なし
```

動作確認（データディレクトリは一時ディレクトリ、ポートは 10186）:

- `uv run ytsched --help` / `ytsched webapp --help` — オプションの
  既定値の表示（`port number, default=10085` など）が f-string 化後も
  変わらないことを確認
- `uv run ytsched x-data1 2021 3 1 --datadir <tmp>` —
  `id-1<tab>2021/03/01<tab>...` と、変更前と同じ形で出力された
- `webapp` を一時ディレクトリで起動して curl:
  - `/ytsched/` → 200
  - `/ytsched/?date=2021-03-01` → 予定のタイトルが本文に出る
  - `/ytsched/?date=2021-03-01&search_str=ミーティング` → 検索がヒット
  - `/ytsched/edit?date=2021-03-01` → 200
  - `/ytsched/static/favicon.ico` → 200（URL ルーティングを
    `rf"..."` に変えた影響が無いことの確認）
  - 書かれた `Conf.cgi` が `SearchStr<TAB>ミーティング` とタブ区切りの
    ままであることを `cat -A` で確認
- 確認後、`pgrep` で PID を確かめてから kill した

## うまくいかなかったところ

特に無し。`ruff --fix --unsafe-fixes` が `.format()` を経由する
（UP031 → UP032 の 2 段）点だけ手間だった。
