# TODO-003. pytest によるテスト整備

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

## きっかけ

テストが 1 つも無かった。TODO-005（明らかなバグの修正）と TODO-006（型ヒントの
整備）で `src/ytsched/` を広く直すので、**その前に現状の挙動を固定する**。

難しいのは「現状を固定する」と「バグを固定しない」を同時にやること。
TODO-005 で直すバグを「正しい挙動」としてテストに書いてしまうと、直したときに
テストが落ちて**直すのをやめる方向に引っ張られる**。これを見るために
`reviewer` を編成に入れた。

## やったこと

### テストの構成

`tests/` に 5 ファイル、テスト項目は 146 件（140 passed / 6 xfailed）。

| ファイル | 内容 |
|---|---|
| `tests/helpers.py` | `make_app()`（`webapp.py` と同じ設定の `Application` を `datadir` だけ差し替えて作る）、`make_handler()`（リクエストを送らずに handler を作る） |
| `tests/test_ytsched.py` | `htmlstr2text()` / `text2htmlstr()`、`SchedDataEnt`、`SchedDataFile`、`SchedData` |
| `tests/test_handler.py` | `Conf.cgi` の読み書き、`days2y_offset()`、import 時の標準出力 |
| `tests/test_web.py` | `tornado.testing.AsyncHTTPTestCase` による `MainHandler` / `EditHandler` |
| `tests/test_webapp.py` | `WebServer` の組み立て、webroot の同梱 |

`pyproject.toml` には dev 依存として `pytest>=9.0.2` と `pytest-cov>=7.0.0` を
足しただけ。`[tool.pytest.ini_options]` は `tmr` と同じくコメントのままにした
（有効にすると毎回カバレッジ計測が走って遅くなり、`-k` で 1 件だけ流したい
ときに邪魔になる）。

**`src/ytsched/` は 1 行も変えていない。** この項目はテストを足すだけ。

### 既知のバグは xfail で印を付けた

TODO-005 に挙がっているバグは、**あるべき挙動を assert したうえで**
`@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)` を付けた（6 件）。
`strict=True` にしたのは、TODO-005 で直したときに xpass で落ちて
「マーカーを外せ」と気づけるようにするため。

TODO-005 のうち 3 件（`datetime.date(2021, 3, 1)` の残骸、`super().__init__()`
の呼び順、`except Exception as ex: raise ex`）は外から見える挙動が無いので
テストを書いていない。

`date=datetime.date.today()` の既定値だけは strict xfail にできなかった。
「`SchedDataEnt().date` が今日になる」は、**モジュールを読み込んだ日が今日で
ある限り今でも通ってしまう**ため。代わりに `inspect.signature()` で
シグネチャの既定値の型を見る形にした。`None` 番兵でも他の形でも通るので、
直し方を縛らない。

### `reviewer` が見つけたもの

`implementer` も `verifier` も気づかなかった指摘が 4 件出た。うち 3 件を
この項目の内で直した。

1. **空振りする assert 2 件**（`test_filter_str` / `test_search_str`）—
   `main.html` は `filter_str` / `search_str` を入力欄に
   `value="{{ ... }}"` でそのまま出し、`base.html` が
   `{% autoescape None %}` なので、渡した語は必ず本文に現れる。
   `assert '歯医者' in body` は**絞り込みが全件を消す壊れ方をしても通る**。
   → 絞り込む語（`病院` = 場所）と表示を確かめる語（`歯医者` = 件名）を
   分ける形に直した
2. **`test_set_time_none` が死にコードを xfail 無しで固定していた** —
   `set_time()` は `src/` のどこからも呼ばれず、設定する `self.time` も
   読まれない。`'%02d'` に直しても何も改善しない。
   → **利用者と相談し、TODO-005 では `set_time()` を丸ごと削除**と決めた。
   テストは `test_set_time_is_dead_code` 1 つにまとめ、削除したら
   `hasattr` の assert が落ちて「このテストも消せ」と分かる形にした
3. **`detail` の往復が `rstrip('\n')` で覆われていた** — 保存 → 読み直しで
   末尾に `\n` が 1 つ増える現状を吸収していて、「往復で一致する」と
   読めてしまう。→ 直値にしてコメントを付けた
4. **`test_load_conf_line_without_tab` が空行とタブ無し行を同時に見ていた** —
   先に空行で落ちるので docstring とずれる。→ 2 つに分けた
   （TODO-005 では両方の対処が要る）

`new_id()` の ID 衝突（`str(time.time())` なので連続 2 回が同じ float を
返すと重複する。今は `_mylog.debug()` が時間を稼いでいて通っているだけで、
**TODO-007 でロガーを差し替えると衝突しうる**）は TODO-005 へ回した。

### TODO-005 に 8 件を追記した

テストを書く過程で、TODO-005 の一覧に無いバグが 8 件見つかった。
利用者と相談し、**新しい項目を立てずに TODO-005 へ追記**した。同じ
「明らかなバグの修正」なので分ける理由が無い。

特に効きそうなのは 2 つ。

- `handler.load_conf()` の `line.split('\t', maxsplit=2)` — 最大 3 個に
  分かれるので、**値にタブが含まれると `ValueError`**。`maxsplit=1` が正しい
- `SchedDataFile.save()` / `save_conf()` / `load_conf()` に `encoding=` が
  無い — ロケール依存で、`LANG=C` では日本語の保存で落ちる。読む側
  （`load()`）は utf-8 → euc_jp を明示しているので、**書く側だけ非対称**

## テスト

`verifier` が実測した（`archives/agents/TODO-003/report-verifier.md`）。

| 確認 | 結果 |
|---|---|
| `uv sync` | ○ pytest 9.1.1 / pytest-cov 7.1.0 |
| `uv run pytest` | ○ 140 passed / 6 xfailed（約 2.4 秒） |
| `uv run pytest --runxfail` | ○ 6 件が狙った理由で落ちる（`ValueError` ×2、`DAYS_YEAR=` の出力、`autoreload=True`、既定値が `datetime.date`、`warning` の呼び出し） |
| カバレッジ | ○ 全体 87%（`handler.py` 100 / `ytsched.py` 97 / `main_handler.py` 92 / `edit_handler.py` 95 / `webapp.py` 82 / `__main__.py` 0） |
| `~/ytsched` 非汚染 | ○ 実行前後とも存在しないまま（テストは `tmp_path` のみ） |
| 2 回連続実行 | ○ 同じ内訳。状態の持ち越し無し |
| アプリ起動 | ○ `GET /ytsched/` が 200、テンプレート展開済み、例外無し |

**空振り assert の直しは、壊し方を作って両方向から確かめた。**
`implementer` は `SchedDataEnt.search_str()` を、`verifier` は
`main_handler` 内の `re.search()` を差し替えて、「絞り込みが全件を消す」
「何も除外しない」の 2 通りの壊れ方を作った。**別々の壊し方で、どちらも
`test_filter_str` / `test_search_str` が両方向で落ちる**ことを確認している
（直す前は、この 2 件は両方とも通ってしまっていた）。

`src/ytsched/__main__.py`（CLI）はテストが無く、カバレッジ 0% のまま。
この項目の範囲外とした。

## 編成

[archives/agents/TODO-003/](../agents/TODO-003/) に、分担とその理由、
各担当の報告を残した。TODO-013 で置いた常設の定義を初めてそのまま使った回で、
項目を立てたときに担当を決めてあったので、着手時に分担案を出して承認を待つ
手順は要らなかった。

`reviewer` を入れたのがこの項目の肝。`verifier` の「動くか」だけでは、
**通ってしまうテスト**は見つからない。
