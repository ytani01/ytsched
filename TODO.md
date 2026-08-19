# TODO

**残っている項目: TODO-004〜TODO-010、TODO-012。** これまでに 5 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-014` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

進める順序は依存関係で決めてある（TODO-003 が済んだので、TODO-005・
TODO-006 に進める）。着手する項目は利用者が指定する。

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

立てたときに挙げたもの:

- [ ] `SchedDataEnt.set_time()` を**丸ごと削除する**
      （`'02d' % t1[0]` は `%` 抜けで必ず TypeError。ただし
      `set_time()` は `src/` のどこからも呼ばれず、設定する `self.time` も
      読まれない死にコードなので、`'%02d'` に直しても何も改善しない。
      TODO-003 で分かった）
- [ ] `SchedDataEnt.__init__` の既定値 `date=datetime.date.today()`
      （import 時に 1 回だけ評価される）
- [ ] `main_handler.py` の `print('DAYS_YEAR=...')`（import 時に出る）
- [ ] `main_handler.py` の `if sde.date == datetime.date(2021, 3, 1):`（残骸）
- [ ] `handler.load_conf()` がタブの無い行で `ValueError`。**空行でも同じ**
      （`if line:` は `'\n'` を真と判定する）
- [ ] `HandlerBase.__init__` が `super().__init__()` を最後に呼んでいる
- [ ] `webapp.py` の `except Exception as ex: raise ex`
- [ ] 正常系のキャッシュミスを `warning` で出している
- [ ] `autoreload=True` が固定

TODO-003（テスト整備）で新たに見つかったもの:

- [ ] `handler.load_conf()` の `line.split('\t', maxsplit=2)` — 最大 3 個に
      分かれるので、**値にタブが含まれると `ValueError`**。`maxsplit=1` が正しい
- [ ] `SchedDataFile.save()` / `handler.save_conf()` / `handler.load_conf()` に
      `encoding=` が無い — ロケール依存になり、`LANG=C` では日本語の保存で
      落ちる。読む側（`load()`）は utf-8 → euc_jp を明示しており非対称
- [ ] `SchedDataFile.load()` が 1 行 7 項目を前提にしている — 項目が足りない
      行があると `IndexError`。壊れたデータファイルへの備えが無い
- [ ] `SchedData.get_sdf()` の破棄数が `int(cache_size * 0.1)` — `cache_size`
      が 10 未満だと 0 件になり、キャッシュが上限を超えて増え続ける
      （既定の 20000 では問題にならない）
- [ ] `SchedDataEnt.new_id()` の ID 衝突 — `str(time.time())` なので連続 2 回が
      同じ float を返すと重複する。今は `_mylog.debug()` が時間を稼いでいて
      通っているだけで、**TODO-007 でロガーを差し替えて速くなると衝突しうる**
- [ ] `MainHandler.get()` 先頭の `modified_sde_id = self.get_argument(
      'sde_id', '')` は直後に `None` で上書きされる（死んだコード）
- [ ] `MainHandler.get()` の `search_str` の処理が 2 回ある（109〜123 行と
      252〜267 行）。前半の結果は後半で上書きされるが、前半でも `set_conf()` が
      走るので `Conf.cgi` への書き込みが二度起きうる
- [ ] `htmlstr2text()` の変換表の `r'&amp;nbsp:'` — 末尾がセミコロンでなく
      コロンで、`&amp;nbsp;` の書き損じに見える

TODO-003 のテストが通る状態を保ったまま直す。
`Conf.cgi` の形式はタブ区切りのままと決めたので（TODO-011）、
`load_conf()` は形式を変えずに直す。

**直したら、TODO-003 で付けた `xfail` のマーカーを外すこと。**
`strict=True` にしてあるので、直すとテストが xpass で落ちて気づける。
`set_time()` を削除したら `test_set_time_is_dead_code` も一緒に消す。

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

- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
