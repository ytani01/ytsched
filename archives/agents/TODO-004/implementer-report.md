# TODO-004 implementer 報告

lint・型チェックと mise タスクの整備。

## 変更・作成したファイル

- `pyproject.toml` — dev 依存に ruff / mypy / basedpyright を追加、
  `[tool.mypy]` `[[tool.mypy.overrides]]` `[tool.basedpyright]` を追加
- `mise.toml`（新規）— `upgradeapt` → `upgrademise` → `upgradeuv` /
  `upgradeproject` → `lint` → `test` → `build`
- `src/ytsched/*.py`（7 ファイル）、`tests/*.py`（5 ファイル）— `ruff format`
  と `ruff check --fix` による整形。中身の変更は下記 2 か所のみ
  - `src/ytsched/handler.py` `load_conf()` — `conf: dict[str, str] = {}`
  - `src/ytsched/ytsched.py` `SchedData.__init__` / `get_sdf()` —
    `_sdf_cache` に型注釈、`popitem()` の受け先を `sdf` → `_discarded`

## 1. 追加した dev 依存

`uv add --group dev ruff mypy basedpyright` で解決させた結果。

| パッケージ | 解決されたバージョン | pyproject の指定 |
| --- | --- | --- |
| basedpyright | 1.39.10 | `basedpyright>=1.39.10` |
| mypy | 2.3.1 | `mypy>=2.3.1` |
| ruff | 0.16.3 | `ruff>=0.16.3` |

tmr（`ruff>=0.14.14` / `mypy>=1.19.1` / `basedpyright>=1.37.3`）より
新しい版が入った。tmr 側の実際のインストールは ruff 0.16.1。

## 2. pyproject.toml に追加した設定

tmr の該当セクションをそのまま流用し、次の 2 点だけ ytsched 用に直した。

- `python_version` — ytsched の `requires-python = ">=3.14"` に合わせて
  `"3.14"`（tmr は 3.13）
- `[[tool.mypy.overrides]]` の `module` — `src/ytsched/` と `tests/` の
  import 文を実際に確認し、外部ライブラリは click と tornado
  （`tornado.web` / `ioloop` / `httpserver` / `httputil` / `testing`）、
  それに pytest だけだったので
  `"click,tornado,tornado.*,pytest,pytest.*"` とした。
  tmr の `blessed` / `loguru` は ytsched では使っていないので入れていない。

`[tool.basedpyright]` は tmr と同一（`typeCheckingMode = "standard"` ほか）。
tmr の 49 行目にあった行末の余分な空白だけ落とした。

`[tool.ruff]` は作っていない。tmr と同じく行長はコマンドラインの
`--line-length 78` で渡す流儀に揃えた。

## 3. mise.toml（tmr との差分）

構成・タスクの並び・`alias` / `depends` は tmr と同一。違いは次の 3 点。

1. コマンド名 `tmr` → `ytsched`
2. **各タスク末尾の動作確認を `uv run tmr -V` →
   `uv run ytsched --help` にした**（判断。理由は下記「単独で決めた判断」）
3. tmr の `upgradeproject` にあるコメント行
   `# uv pip install -U --group samples -e .` と、`lint` の各行末尾の
   `# samples` は、ytsched に samples ディレクトリが無いので落とした。
   末尾のコメントアウト済み `[tasks.testpypi]` も同じ理由で入れていない

対象ディレクトリは tmr と同じ `src tests`（ytsched も `src/` と `tests/` が
あるので、`src/ytsched` ではなく `src` を渡している）。

## 4. ruff format / ruff check の結果

`uv run ruff format --line-length 78 src tests`

- **13 ファイルが整形された**（`src/ytsched/` の 7 ファイルすべてと
  `tests/` の 5 ファイル、計 12 ファイル + 再実行分）。実際に git で
  変更が出たのは次の 12 ファイル
  - `src/ytsched/__init__.py`, `__main__.py`, `edit_handler.py`,
    `handler.py`, `main_handler.py`, `my_logger.py`, `webapp.py`,
    `ytsched.py`
  - `tests/helpers.py`, `test_handler.py`, `test_web.py`,
    `test_webapp.py`, `test_ytsched.py`
- 78 文字を超える行は 0 になった（`awk 'length > 78'` で確認）

`uv run ruff check --fix --extend-select I src tests`

- 14 件を自動修正（主に import の並べ替え `I001` と、
  未使用 import・未使用変数の削除）
- **97 件が残った。** 内訳（`--statistics`）:

  | 件数 | 規則 |
  | --- | --- |
  | 35 | `UP031` printf-string-formatting（`'%s' % x` → f-string） |
  | 13 | `DTZ011` call-date-today（`date.today()` に tz が無い） |
  | 13 | `FLY002` static-join-to-f-string（テスト内の `'\t'.join([...])`） |
  | 10 | `D419` empty-docstring（`""" """` だけの docstring） |
  | 10 | `RUF013` implicit-optional |
  | 5 | `RUF012` mutable-class-default |
  | 4 | `EXE001` shebang-not-executable |
  | 2 | `SIM102` collapsible-if |
  | 各 1 | `C408`, `DTZ005`, `PERF402`, `PLC0206`, `SIM118` |

  ファイル別では `ytsched.py` 34、`main_handler.py` 12、`test_web.py` 13、
  `test_ytsched.py` 10、`__main__.py` 8、`handler.py` 6、`webapp.py` 6、
  `edit_handler.py` 3、`helpers.py` 4、`my_logger.py` 1。

  これらは**いずれもリファクタリング（`UP031` の 35 件が最大）か
  TODO-006 の型の話（`RUF013`）**なので、今回の範囲外として直していない。
  詳細一覧は下の「直さず残したもの」を参照。

  なお ruff 0.16 は 0.14 より既定で選択される規則が大幅に広く、
  tmr 側でも同じコマンドで 8 件のエラーが出る（`RUF012` 4、`SIM117` 3、
  `SIM102` 1）。**tmr も現状 `mise run lint` は通らない。**

## 5. mypy / basedpyright の結果

### 直したもの（2 件）

| ファイル | 内容 |
| --- | --- |
| `src/ytsched/handler.py:75` | `conf = {}` → `conf: dict[str, str] = {}`（mypy `var-annotated`） |
| `src/ytsched/ytsched.py:617` | `self._sdf_cache` に `collections.OrderedDict[datetime.date, SchedDataFile]` の注釈（mypy `var-annotated`） |

`_sdf_cache` に注釈を付けたところ、`get_sdf()` のキャッシュ破棄ループで
`sdf = self._sdf_cache.popitem(last=False)` が
「tuple を SchedDataFile 型の変数に代入」と検出された。この `sdf` は
直後に `sdf = SchedDataFile(...)` で上書きされるだけで使われていない
（コメントアウトされたデバッグ出力が参照するのみ）ため、受け先を
`_discarded` にリネームした。ruff の `F841`（未使用変数）を避けるため
アンダースコア始まりにしてある。**動作は変わらない。**

### 残っているエラー

`uv run mypy src tests` → **35 件（5 ファイル）**
`uv run basedpyright src tests` → **28 errors, 2 warnings**

どれも TODO-006「型ヒントの整備」で扱う想定のものなので直していない。
以下、mypy の出力そのまま（basedpyright もほぼ同じ箇所を指す）。

#### `src/ytsched/ytsched.py`（mypy 17 件）

- 108: `date: datetime.date = None`（implicit Optional）
- 109, 110: `time_start` / `time_end` の既定値が `''` なのに型は
  `datetime.time` — **TODO-006 の本題**
- 299 (`set_date` の `d`), 348, 382, 645, 688, 713, 727: implicit Optional
- 357: `Name "__class__" is not defined` —
  `get_logger(__class__.__name__, ...)`。実行時には動くが mypy が
  対応していない。ロガー周りは TODO-007 で `my_logger.py` ごと
  廃止する予定なので触っていない
- 469, 476: `str` を `datetime.time` の変数に代入（109/110 と同根）
- 540, 557: `sde_id: str = None`
- 574: `return None` なのに戻り値型が `SchedDataEnt`
- 713: `sde: SchedDataEnt = None`

#### `src/ytsched/main_handler.py`（mypy 8 件）

- 218, 220: `str | None` の変数に `int` を代入 / `int()` に `str | None`
- 319: `timedelta()` に `str | None`
- 404: `int <= None` / `str >= int` の比較
- **458: `Syntax error in type annotation`** —
  `-> (datetime.date, str)` と書かれている。TODO-006 の項目そのもの
- 562: `str` 型の変数に `None` を代入

#### `src/ytsched/edit_handler.py`（mypy 1 件 / basedpyright 2 件）

- 77: `self.get_argument('...', False)` が tornado の `get_argument`
  のどのオーバーロードにも一致しない（`default` に `bool` を渡している）。
  tornado 側の型定義に合わせるには呼び方を変えることになるので保留

#### `src/ytsched/__main__.py`（mypy 1 件）

- 22: `Name "__class__" is not defined`（ytsched.py:357 と同じ）

#### `tests/test_ytsched.py`（mypy 8 件）

- 38: `SchedDataEnt(**dict[str, object])` の展開
- 250, 325, 513, 517, 709, 712（basedpyright は 220 も）: `None` を
  `date` / `str` の
  パラメーターに渡している。**これは本体側が implicit Optional を
  受け付けている前提のテストなので、本体を直せば消える**

basedpyright だけが出すもの:

- `ytsched.py:189, 191`: `'\t'.join()` に `list[Unknown | str | None]`
- `ytsched.py:309, 402`: `reportUnreachable` の warning
  （implicit Optional を `None` 非許容と解釈するため到達不能に見える。
  本体の型が直れば消える）

## 自分で確かめたこと

| 確認 | 結果 |
| --- | --- |
| `uv run pytest tests` | **161 passed**（整形の前後で変化なし） |
| 78 文字超の行 | `awk 'length > 78' src/ytsched/*.py tests/*.py` で 0 件 |
| `mise tasks` | `upgradeapt` / `upgrademise` / `upgradeuv` / `upgradeproject` / `lint` / `test` / `build` が並ぶ（`installmise` / `installuv` はユーザーのグローバル設定由来） |
| `mise run upgradeproject` | 正常終了（`uv sync` → `uv pip install` → `ytsched --help`） |
| `mise run lint` | **ruff check の 97 件でエラー終了**。basedpyright / mypy まで進まない |
| webapp の起動 | 一時ディレクトリを `--datadir` に指定して `--port 10099` で起動、`GET /ytsched/` が **200**。確認後プロセスを停止 |

## 単独で決めた判断

1. **mise タスクの動作確認を `uv run ytsched --help` にした。**
   tmr は各タスクの末尾で `uv run tmr -V` を実行しているが、ytsched の
   CLI には `-V` / `--version` が無い（`webapp` サブコマンドに
   `--version` があるだけで、これはサーバのバナー表示用オプション）。
   トップレベルに `-V` を足すのは機能追加で今回の範囲外なので、
   既にある `--help` で代用した。**`-V` を足すかどうかは main の判断。**
   足すなら mise.toml の 4 か所を書き換えることになる。
2. **`_sdf_cache` の型注釈は入れ、それに伴う変数名の衝突も直した。**
   「簡単な型注釈漏れ」の範囲と判断した。詳細は上記のとおり。
3. **`[tool.ruff]` セクションは作らなかった。** 依頼どおり tmr の流儀
   （コマンドラインで `--line-length 78`）に揃えた。ただしこの結果、
   ruff 0.16 の広い既定規則がそのまま効いていて `mise run lint` が
   通らない（下記）。
4. **`ruff check` に `--line-length` は渡していない。** tmr が
   `format` にだけ渡しているのに揃えた。今回の整形後は 78 文字超の行が
   無いので実害はない。

## main の判断が要ると思う点

- **`mise run lint` が通らない。** ruff check の 97 件で止まる。
  内訳の大半（`UP031` 35 件）はリファクタリングで、TODO-006（型）でも
  消えない。次のどれにするかは main の判断:
  - (a) そのまま残す（tmr も同じ状態）
  - (b) `pyproject.toml` に `[tool.ruff.lint]` を足して規則を絞る
    （tmr の流儀から外れる）
  - (c) 別の TODO 項目を立てて `UP031` などを潰す
- **CLI に `-V` / `--version` を足すか**（上記「判断」1）

## 直さずに残したもの（範囲外）

- `RUF013` implicit-optional 10 件、mypy の implicit Optional 系、
  `main_handler.py:458` の `-> (datetime.date, str)`、
  `time_start`/`time_end` の `''` — すべて **TODO-006** の範囲
- `__class__.__name__` を使ったロガー取得（`ytsched.py:357`,
  `__main__.py:22`）— **TODO-007**（`my_logger.py` の廃止）の範囲
- `EXE001` shebang-not-executable 4 件 — shebang を残すか消すかは
  **TODO-008**（`uv tool install` 方式）で起動方法を決めてからのほうがよい
- `UP031` / `FLY002` / `SIM102` / `D419` などの整形・書き換え系 —
  どの TODO にも属さない。上記「main の判断が要る点」に書いた
