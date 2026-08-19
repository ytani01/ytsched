# TODO

**残っている項目: TODO-003〜TODO-010、TODO-012。** これまでに 4 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-014` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

進める順序は依存関係で決めてある（TODO-003 → TODO-005・TODO-006）。
着手する項目は利用者が指定する。

---

## TODO-003. pytest によるテスト整備

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

- [ ] `tests/` を作る
- [ ] `SchedDataEnt` / `SchedDataFile` / `SchedData` のユニットテスト
- [ ] handler のテスト（`tornado.testing`）
- [ ] `pytest-cov`

テストが 1 つも無い。**現状の挙動を固定してから** TODO-005・TODO-006 の
修正に進む。`reviewer` を入れるのは、テストが現状の挙動を正しく写して
いるか（バグごと固定していないか）を見るため。

---

## TODO-004. lint・型チェックと mise タスク

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] ruff / mypy / basedpyright を dev 依存に追加
- [ ] `mise.toml`（`upgradeproject` → `lint` → `test` → `build`）
- [ ] 行長 78 で整形

`tmr` と同じ構成に揃える。

---

## TODO-005. 明らかなバグの修正

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

- [ ] `SchedDataEnt.set_time()` の `'02d' % t1[0]`（`%` 抜けで必ず TypeError）
- [ ] `SchedDataEnt.__init__` の既定値 `date=datetime.date.today()`
      （import 時に 1 回だけ評価される）
- [ ] `main_handler.py` の `print('DAYS_YEAR=...')`（import 時に出る）
- [ ] `main_handler.py` の `if sde.date == datetime.date(2021, 3, 1):`（残骸）
- [ ] `handler.load_conf()` がタブの無い行で `ValueError`
- [ ] `HandlerBase.__init__` が `super().__init__()` を最後に呼んでいる
- [ ] `webapp.py` の `except Exception as ex: raise ex`
- [ ] 正常系のキャッシュミスを `warning` で出している
- [ ] `autoreload=True` が固定

TODO-003 のテストが通る状態を保ったまま直す。
`Conf.cgi` の形式はタブ区切りのままと決めたので（TODO-011）、
`load_conf()` は形式を変えずに直す。

---

## TODO-006. 型ヒントの整備

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

- [ ] `time_start: datetime.time = ''` → `datetime.time | None`
- [ ] `-> (datetime.date, str)` → `tuple[datetime.date, str]`
- [ ] mypy / basedpyright が通るまで直す

空文字列を `datetime.time` として扱っている箇所が広い。

---

## TODO-007. loguru への移行

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] `my_logger.py` を廃止
- [ ] `tmr` と同じ `__log = getLogger(__qualname__)` 規約に揃える

---

## TODO-008. uv tool install 方式へ

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] `install.sh` と `Ytsched.src` を廃止
- [ ] 起動スクリプトの扱いを決める
- [ ] `uv tool install` での手順を確認

データディレクトリは `~/ytsched/data` のまま。

---

## TODO-009. README の更新

見込み: main = Sonnet 5 / effort low、担当 = writer + verifier

- [ ] 「Install: TBD」を書く
- [ ] 「使用環境」を Python 3.14 / uv に直す
- [ ] 「課題・問題点」を見直す

`verifier` には、README に書いたコマンドが実際に動くかを確かめさせる。

---

## TODO-010. CLAUDE.md の作成

見込み: main = Opus 5 / effort medium、担当 = verifier

- [ ] 移行後の構成・コマンド・設計の勘所をまとめる

移行が一通り済んでから書く。全体を把握している main が書き、
`verifier` に「書いた内容が実物と合っているか」を確かめさせる。

---

## TODO-012. `autoescape None` と正規表現入力の扱い（判断）

見込み: main = Opus 5 / effort medium、担当 = main のみ

- [ ] どこまで対処するか決める

`base.html` が `{% autoescape None %}` で全体のエスケープを切っている
（`detail` の `<br />` を通すため）。`filter_str` / `search_str` は
利用者の入力をそのまま `re.search` に渡している（不正な正規表現は
warning で握り潰している）。単一ユーザかつリバースプロキシで認証する
前提なので、どこまでやるかを先に決める。**決めるだけの項目。**

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
