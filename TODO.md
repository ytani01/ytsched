# TODO

**残っている項目: TODO-003〜TODO-010、TODO-012、TODO-013。** これまでに 3 件を決着させた。
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

## TODO-013. サブエージェントの常設定義と運用の見直し

見込み: main = Opus 5 / effort high、担当 = main のみ
（定義そのものを作る項目なので分担しない）

- [x] `.claude/agents/` に常設の定義を 4 つ置く
      （`implementer` / `verifier` / `reviewer` / `writer`）
- [x] `~/.claude/CLAUDE.md` の運用を直す
- [x] 残っている各項目の `見込み:` 行に担当を書く
- [ ] Claude Code を再起動し、定義が読まれることを確認する

TODO-002 をサブエージェントで実施して分かったことを反映する。
**実装と確認を別のエージェントに分けた効果が大きかった**ので、
これを常設の仕組みにする。優先順位は 品質 ＞ 利用者の手間削減 ＞
トークン削減。

常設にする理由は 3 つ。

1. **effort は定義ファイルの frontmatter でしか指定できない。**
   Agent ツールに渡せるのは model だけ
2. **分担の確認を「項目を立てるとき」に前倒しできる。**
   項目に担当を書いておけば、着手時に分担案を出して承認を待つ手順が要らない
3. プロジェクトの前提（データ形式、`tmr` に揃える、シェルのエイリアス）を
   定義に持たせれば、依頼のたびに書き写さなくて済む。書き写しの漏れも防げる

`CLAUDE.md` で直すのは次の 5 点。

- `.claude/agents/*.md` を archives へ**移さない**（使い回すため）。
  定義は git 管理下に残し、archives には分担と理由と報告を残す
- 「規模の大きい項目は編成する」→ **確認担当は規模によらず立てる。**
  実装担当を分けるかを規模で決める。決めるだけの項目は例外
- **`見込み:` `実施:` の行に、main のモデル・effort と担当を書く。**
  `見込み: main = Opus 5 / effort high、担当 = implementer + verifier` の形。
  担当のモデルと effort は定義ファイル側にあるので書かない
- 分担は**項目を立てるときに決める**。着手時の分担確認は不要にする
- **報告はファイル、返事は要点のみ**という指示を定型にする
  （置き場所は `archives/agents/TODO-NNN/`）

**決着済みの項目（`archives/todo/`）の `見込み:` `実施:` 行は書き換えない。**
そのときの記録なので、古い形式のまま残す。

`.claude/agents/` は Claude Code の起動時にしか読まれないので、
**置いたら再起動が要る。** 再起動するのは利用者。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
