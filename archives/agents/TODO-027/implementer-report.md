# TODO-027 implementer の報告

不正な入力（数字・日付として読めない値）で 500 にせず、既定値へ落として
警告を出すようにした。不正な値は `Conf.cgi` へ保存しない。

## 変えたファイル

### `src/ytsched/main_handler.py`

- `convert_value[T]()` を追加。文字列を `convert`（`int` /
  `datetime.date.fromisoformat`）に通し、`ValueError` なら警告を 1 行出して
  `None` を返す。警告の形は既存に揃えて
  `f"{name}={value!a}: {ex} .. ignored"`（`ytsched.py` の
  `dict_time()` と同じ書き方）
- `get_conf_arg()` を `get_conf_arg[T]()` にして、`convert:
  Callable[[str], T]` を必須のキーワード引数に、`default` を `T` にした。
  引数の値が変換できなければ **`set_conf()` を呼ばずに** 次へ落ち、
  `Conf.cgi` の値も変換できなければ `default` を返す
- 呼び出し 4 か所に `convert=` を足した（`search_str`/`filter_str` は
  `str`、`search_n`/`todo_days` は `int`）。`int(...)` で包んでいた 2 か所と
  `str(DEF_*)` は不要になったので消した
- `get_date()` の `cur_day` / `date` を `convert_value()` 経由にした
- `ymd2date()` を追加。`year`/`month`/`day` を `datetime.date` にする。
  数字にならない値も `month=13` / `day=32` のような範囲外も、警告を出して
  `None` を返す。`get_date()` はそれを「指定が無かった」のと同じに扱う

`Callable` は `collections.abc` から import した。ジェネリックは
PEP 695 の書き方（`def get_conf_arg[T](...)`）。3.14 なのでそのまま使える。
`TypeVar` を別に宣言するより短く、basedpyright / mypy とも通った。

### `tests/test_web.py`

- `date_id()` をモジュールに追加（`test_main_handler.py` にあったものを
  移した。両方から使うため）
- `TestInvalidArgs` を追加（18 件）。`search_n` / `todo_days` /
  `date` / `cur_day` / `year`+`month`+`day` それぞれについて、
  200 で開けること、既定値で描かれること、`Conf.cgi` に残らないこと、
  一度踏んでも次の素の GET が開けること、`Conf.cgi` に既に不正な値が
  入っていても既定値へ落ちることを見ている

### `tests/test_main_handler.py`

- `date_id()` の定義を消し、`test_web` から import するようにした
- ゴールデンマスターテスト `test_empty_search_n_is_an_error` を
  `test_empty_search_n_is_not_saved` に書き直した（500 → 200、
  `Conf.cgi` に空で残る → 作られない）。これが今回の変更で落ちた唯一の
  既存テスト
- `test_empty_search_n_does_not_break_next_request` と
  `test_empty_todo_days_is_ignored` は、結果は変わらないが説明が
  合わなくなったので docstring だけ直した

## 自分で確かめたこと

- `mise` のタスクと同じコマンドを個別に叩いた（`upgradeproject` は
  走らせていない）。
  - `uv run ruff format --line-length 78 src tests` → 変更なし
  - `uv run ruff check --extend-select I src tests` → All checks passed
  - `uv run basedpyright src tests` → 0 errors
  - `uv run mypy src tests` → Success
  - `uv run pytest tests` → **348 passed**（変更前は 330）
- 一時ディレクトリ（scratchpad）を `--datadir` に指定してアプリを起こし、
  TODO-024 の表と同じ入力を curl で叩き直した。**8 通りすべて 1 回目も
  そのあとの素の GET も 200 で、`Conf.cgi` は作られなかった**。

  | 入力 | 1 回目 | そのあとの素の GET | `Conf.cgi` |
  |---|---|---|---|
  | `search_n=`（空） | 200 | 200 | 作られない |
  | `search_n=abc` | 200 | 200 | 作られない |
  | `todo_days=abc` | 200 | 200 | 作られない |
  | `year=abc` / `month=13` / `day=32` | 200 | 200 | 作られない |
  | `date=abc` / `cur_day=abc` | 200 | 200 | 作られない |

- `Conf.cgi` に `SearchN abc` / `ToDo_Days abc` を手で書いた状態から
  トップページを開いて 200、件数は `value="5" selected`、ToDo の期間は
  `value="365" selected`（どちらも既定値）になることを確かめた
- 正しい値（`search_n=10`・`todo_days=7`）は今までどおり保存され、
  そのあと `search_n=abc&todo_days=abc` を叩いても `Conf.cgi` が
  書き換わらないことを確かめた
- 警告ログが出ていることを実際のログで確かめた。例:
  - `year='2021', month='13', day='1': month must be in 1..12, not 13 .. ignored`
  - `SearchN='abc': invalid literal for int() with base 10: 'abc' .. ignored`
- 確かめ終わったあと、起動したサーバは止めた

## 単独で決めた判断

1. **不正な引数の落とし先を「指定が無かったのと同じ」にした**（要確認）。
   依頼書は「`search_n` は `DEF_SEARCH_N`」と書いてあるが、そのまま読むと
   「`Conf.cgi` に正しい値が保存されていても、引数に打ち間違いがあったら
   既定値に戻す」ことになる。`date` について依頼書が挙げている
   「指定が無かったのと同じ扱い」と揃え、**引数 → `Conf.cgi` → 既定値**の
   順に落ちるようにした。`Conf.cgi` に何も無ければ結果は `DEF_SEARCH_N`
   なので、依頼書の文面とはこの一点だけ違う。理由は 3 つ:
   - 打ち間違いで保存済みの設定が消えるほうが驚きが大きい
   - 依頼書が `date` に挙げた規則と同じ形になる
   - `Conf.cgi` を飛ばして既定値へ行くには分岐を足すことになり、
     まれな場合のためにコードが増える

   この挙動は `test_invalid_search_n_keeps_saved_search_n` で固定した。
   **`DEF_SEARCH_N` へ直行させるほうがよければ、そのテストと
   `get_conf_arg()` の後半 3 行を直せば切り替えられる。**
2. **`convert` を必須のキーワード引数にした**（既定値を付けなかった）。
   4 か所とも明示させたほうが、次に足すときに検証を忘れにくい。
3. **`date_id()` を `test_web.py` へ移した。** 新しいテストと
   `test_main_handler.py` の両方から使うため。`test_main_handler.py` が
   `test_web.py` を import する向きは元からあるので、逆向きにはしていない。
4. **UI には知らせを出していない。** 不正な正規表現（TODO-012）は
   「フィルタの正規表現…」と画面に出るが、依頼書にあるのは警告ログだけ
   なので、テンプレートは触っていない。

## 直さずに残したもの

- **`src/README.md` に、この扱いを書く段落を足していない。** 「フィルタ・
  検索文字列の扱い」の隣に「数字・日付の引数の扱い」を書くと収まりが
  よいが、依頼書の範囲外なので手を出していない。今の README には
  「不正な数字で 500 になる」とは書かれていないので、**書かなくても
  文書が間違いになることはない**。足すかどうかは main の判断（足すなら
  `wording` が要る）。
- **`get_date_arg()` / `get_time_arg()`（編集フォームの POST 側）は
  そのまま。** `date=abc` を POST すると今も `ValueError` で 500 になる。
  TODO-024 の表にも依頼書の 5 か所にも入っていないので触っていない。
  ブラウザからは `<input type="date">` 経由なので普通は起きない。
- **`empty_is_given` の食い違いは揃えていない**（依頼書のとおり。
  TODO-028 の範囲）。
- **`Conf.cgi` に不正な値が残っている間は、リクエストのたびに同じ警告が
  出る。** 読むたびに落とすので当然だが、正しい値を一度指定するまで
  ログに出続ける。消し込みまではしていない（保存の側を直したので、
  今後この状態にはならない）。
- `search_n=0` や `search_n=-1` のような「数字だが妥当でない」値は
  変換に成功するので、今までどおりそのまま使われる（打ち切り条件
  `search_count >= search_n` が最初から成立するだけで、500 にも
  無限ループにもならない）。TODO-024 の一覧にも無いので触っていない。

## うまくいかなかったところ

特になし。テストは一度、`Conf.cgi` に `SearchStr` も一緒に書かれるのを
見落として落ちたが、その場で直した。
