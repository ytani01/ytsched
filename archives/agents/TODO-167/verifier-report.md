# TODO-167 verifier 報告

## 1. lint / typecheck / test

- ○ `uv run ruff format --check` — src/tests/docs は整形済み。`archives/`
  配下 10 ファイルが unformatted と出るが、いずれも TODO-167 と無関係の
  既存ファイル（`archives/` は整形対象外の既知事項）
- ○ `uv run ruff check` — `All checks passed!`
- ○ `uv run basedpyright` — `0 errors, 0 warnings, 0 notes`
- ○ `uv run pytest -q --ignore=tests/test_browser.py` — 559 件成功
  （`test_browser.py` は時間がかかるため、implementer の報告済みの
  61 件成功を採用し再実行していない）

## 2. アプリの起動確認（`--datadir` は一時ディレクトリ）

`class="my-week-panel` の数（すべて HTTP 200、例外・トレースバックなし）:

| `LoadWeekPages` | 期待 | 実測 |
|---|---|---|
| 未設定（既定 4） | 9 | 9 |
| `"0"` | 1 | 1 |
| `"10"` | 21 | 21 |
| `"103"`（上限） | 207 | 207 |
| `"104"` | 9 | 9 |
| `"-1"` | 9 | 9 |
| `"abc"` | 9 | 9 |

範囲外・不正値の各ケースで WARNING が 1 行だけ出ることを確認:
`LoadWeekPages='104': LoadWeekPages must be in 0..103, not 104 .. ignored` など。
`Traceback` は各ログに 0 件。

## 3. `conf.json` が無いときの既定値作成

未設定 datadir で起動後、`conf.json` が作られ、9 キーすべて文字列:

```
SearchStr="" FilterStr="" ToDo_Days="1y" SearchN="5" MonthCal="1"
LoadWeekPages="4" LoadMonthPages="2" AutoTurnMsec="700" TrashMax="100"
```

依頼書の 9 キー・値と一致。

## 4. 既存 `conf.json` を上書きしないこと

`{"LoadWeekPages": "2"}` だけを書いた `conf.json` を置いて起動 →
HTTP 200、panel 数 5（`2*2+1`、正しく読めている）。起動後も
`conf.json` の中身は `{"LoadWeekPages": "2"}` のまま。**足りないキーは
足されない**（実装の選択どおり）。

## 5. 月間表示

`?view=month` で HTTP 200、`{{`/`{%` の生残りなし、例外・トレースバック
なし。`LoadMonthPages` に触れる変更は無く、リグレッションテストも全件
通過しているため、今までどおりと判断。

## 6. 残存確認

`grep -rn "LoadMonths\|months2weeks\|load_months\|DAYS_PER_MONTH" src/
tests/ docs/` — 0 件。`archives/` と `TODO.md`（main が編集）にのみ残存
（想定どおり）。

## 気になった点（判断は main へ）

依頼書の追記にあった「テストを緩めていないか」について、実際に緩んでいる
箇所がある。

- **`tests/test_main_handler.py` の `TestConfArgs` 系（`test_empty_search_
  str_is_saved` など、194〜263 行あたり）。** 元は
  `assert self.conf_data() == {"SearchStr": ""}` のように **辞書全体の
  完全一致**で、「そのキーだけが書かれ、他のキーは書かれていない」ことを
  確かめていた。TODO-167 で `conf.json` に常に既定 9 キーが入るように
  なったため、完全一致はできなくなったが、直し方は
  `assert self.conf_data()["SearchStr"] == ""` のように **見ているキー
  だけを取り出す形**になっており、「他の 8 キーが既定値のまま変わって
  いないか」は見なくなった。例えば `FilterStr` を保存する処理が誤って
  `SearchStr` も書き換えてしまうような不具合があっても、このテスト群は
  検出できない。既定 9 キーの辞書を組み立てて対象キーだけ上書きした
  完全一致に直せば、元の検出力を保てたはず（`test_save_conf_is_json`
  で実際に試したところ、保存後の JSON は決定的で完全一致が可能だった）
- **`tests/test_handler.py::test_save_conf_is_json`・
  `test_conf_is_not_locale_dependent`** も同様に、完全一致から
  `startswith`/`endswith`/該当キーだけの確認に緩めている。こちらも
  完全一致への書き直しは可能だった（実測: 該当ケースで書き出される
  JSON は `SearchStr` を先頭にした 9 キーの決定的な内容になる）
- 上記はいずれも「壊れたから最小限だけ直した」形になっており、
  依頼書の追記が懸念していた種類の緩め方に当たると考える。実害は
  今回の pytest 実行では顕在化していない（アプリの実起動確認 1〜6 は
  すべて期待どおり）が、将来の回帰を検出する力は元より弱くなっている

## 結論

起動確認・既定値作成・上書きしないこと・月間表示・残存 grep は
すべて期待どおりで、不具合は見つからなかった。テストの緩め方には
上記の懸念がある。

## 再確認（テストの完全一致への戻し）

implementer-report.md の「## 追記（テストの完全一致への戻し）」を確認した。

1. **完全一致に戻っていること・値がベタ書きでないこと** — ○
   `tests/test_main_handler.py` に追加された `expected_conf(**overrides)`
   は `dict(ConfFile.DEF_CONF)` を土台に、変わったキーだけ `update()`
   するだけで、値のベタ書きは無い（`ConfFile.DEF_CONF` の増減に
   自動で追随する）。`TestConfArgs` の全アサーションと
   `test_binder_update_conf_args_returns_and_saves_all_four` が
   `self.conf_data() == expected_conf(...)` の完全一致に戻っている。
   `tests/test_handler.py` の `test_save_conf_is_json`・
   `test_conf_is_not_locale_dependent` も `dict(ConfFile.DEF_CONF)` を
   土台に `SearchStr` だけ上書きし、`json.dumps(..., indent=2) + "\n"`
   との完全一致（書式込み）に戻っている。差分は
   `git diff tests/test_handler.py tests/test_main_handler.py` で確認済み
2. **巻き添え書き換わりの検出** — ○ 実際に確かめた。
   `src/ytsched/conf.py` の `ConfFile.set()` へ一時的に
   `self._conf["FilterStr"] = "INJECTED_BUG"` を差し込み（`set()` が
   呼ばれるたびに `FilterStr` を巻き添えで書き換えるバグを模した）、
   `uv run pytest -q
   tests/test_main_handler.py::TestConfArgs::test_search_str_is_saved_normalized`
   を実行 →
   `{'FilterStr': 'INJECTED_BUG'} != {'FilterStr': ''}` で **FAILED**
   （期待どおり検出）。確認後、バックアップから `conf.py` を復元し、
   同テストが再び PASSED になることと `git status --short` で
   意図しない差分が残っていないことを確認した
3. **`uv run pytest`（全件、`test_browser.py` 含む）** — ○
   `620 passed in 181.25s`
4. **`uv run ruff check src tests tools`** — ○ `All checks passed!`
   **`uv run basedpyright src tests tools`** — ○ `0 errors, 0 warnings, 0 notes`

不具合は見つからなかった。テストの緩みは解消されている。
