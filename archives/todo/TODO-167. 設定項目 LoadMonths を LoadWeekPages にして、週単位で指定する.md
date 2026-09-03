# TODO-167. 設定項目 `LoadMonths` を `LoadWeekPages` にして、週単位で指定する

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 35,763 / cache_creation 342,453 / 概算 $6.5 |
|      | main 50% + implementer 38% + verifier 12%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-167/](../agents/TODO-167/README.md) にある。

## きっかけ

週間表示の先読み範囲は `LoadMonths`（既定 1、範囲 0〜24）で月単位に指定し、
`months2weeks()`（`round(months * 30 / 7)`）で週数へ換算していた。1 ヶ月と
書いても実際に増えるのは前後 4 週で、指定と挙動が対応しない。TODO-166 で
足した月間表示の `LoadMonthPages` は画面数で直接指定しているので、週間表示も
そちらに揃えた。

## やったこと

- **`LoadMonths` を `LoadWeekPages` にした**（既定 4、範囲 0〜103）。
  既定は現行の `LoadMonths=1`（前後 4 週）と同じ挙動、上限は
  `LoadMonths=24` に相当する週数。読み方は `LoadMonthPages` と同じ形
  （`MainBinder._get_conf_int()`、`DisplayArgs.load_week_pages`）
- **`months2weeks()` と `DAYS_PER_MONTH` を削除した。**
  `main_view.py` の定義、`main_handler.py` の再公開、
  `tests/test_web.py` のテスト群も併せて片付けた。`_mk_weeks()` の range は
  `range(-load_week_pages, load_week_pages + 1)` になった
- **旧 `LoadMonths` は読まない。** 後方互換のコードは入れていない。
  `conf.json` の書き換えは利用者がやる（単一ユーザー専用で、手で書く設定）
- **datadir に `conf.json` が無ければ、既定値を書いたものを作るようにした。**
  キー名が変わっても手本が手元にあるようにするため。書き出すのは
  `ConfFile._load()` が `FileNotFoundError` を捕まえたところで、中身は
  画面から自動保存されるキーも含めた全 9 キー（`ConfFile.DEF_CONF`）。
  書けなくても警告 1 行で、例外は外へ出さない（`save_if_dirty()` と同じ）
- `ytsched.py` の `DEF_CACHE_SIZE` の根拠のコメントを `LoadWeekPages` 基準に
  書き直した。**日数は変わらない**（上限 103 週 → 前後 207 週 → 1449 日 +
  ToDo 1 で 1450）ので、値 2000 はそのまま
- 文書（`docs/User.md`・`src/README.md`）を直した

`DEF_CONF` は `conf.py` に素の dict として持たせた。`conf.py` は
`main_binder.py`／`trash_handler.py` から使われる側なので、既定値を
そちらから import すると循環参照になりうる。代わりに、**dict の値が
各クラスの既定と一致していることを見るテスト**を足してある
（テスト側からは両方 import できる）。

## テスト

- `tests/test_web.py` の `LoadMonths` テスト群を `LoadWeekPages` 用に
  書き直した。期待値は `DEF_LOAD_WEEK_PAGES * 2 + 1` を直接数える形。
  範囲外は `"104"`
- `tests/test_browser.py` の `LoadMonths: "2"` を、同じ週数になる
  `LoadWeekPages: "9"` に置き換えた
- `conf.json` が無いときに既定値のファイルができることのテストと、
  `ConfFile.DEF_CONF` が `MainBinder`／`TrashHandler` の既定と一致することの
  テストを足した
- verifier が実際に起動して、`class="my-week-panel` の数を数えた。
  未設定 9 /`"0"` 1 /`"10"` 21 /`"103"` 207 /`"104"`・`"-1"`・`"abc"` は
  9 と警告 1 行。`conf.json` が無い datadir で 9 キーが文字列で作られること、
  既にあるファイルは上書きしないこと（足りないキーも足さない）も確認した
- `ruff check` / `basedpyright` / `pytest`（620 件）が通る

## 気をつけた点

- **`conf.json` を常に作るようにしたら、既存テストが壊れた。**
  「ファイルが無いこと」「特定のキーしか書かれていないこと」を辞書全体の
  完全一致で見ていた `tests/test_handler.py`・`tests/test_main_handler.py`
  が軒並み落ちた。implementer は最初、これを「見ているキーだけ取り出す」形に
  緩めて通したが、verifier が「他のキーが巻き添えで書き換わる不具合を
  検出できなくなっている」と指摘。`ConfFile.DEF_CONF` を土台に、変わった
  キーだけ上書きした期待値を組み立てる形（`expected_conf(**overrides)`）で
  完全一致へ戻した。verifier が `ConfFile.set()` へわざとバグを差し込んで、
  テストが実際に落ちることまで確かめている
- **`ruff format` は Markdown の中の ```` ```python ```` ブロックも整形する。**
  implementer が対象パスを指定せず `uv run ruff format` を叩いたため、
  `archives/` 以下の報告ファイル 9 件と `archives/agents/TODO-060/probe.py`
  が書き換わった（戻した）。`mise run fmt` は `src tests tools` に絞って
  あるので、そのタスク経由では起きない。`pyproject.toml` 側で除外する件は
  TODO-168 にした
