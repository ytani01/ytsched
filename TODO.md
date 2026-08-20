# TODO

**残っている項目: TODO-007〜TODO-010、TODO-012、TODO-015、TODO-016。**
これまでに 9 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-017` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

進める順序は依存関係で決めてある（TODO-006 が済んだので、TODO-007 に
進める）。着手する項目は利用者が指定する。

---

## TODO-007. loguru への移行

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] `my_logger.py` を廃止
- [ ] `tmr` と同じ `__log = getLogger(__qualname__)` 規約に揃える
- [ ] `SchedDataEnt.__init__` の `self.__class__._mylog` 上書きをやめる
      （インスタンス 1 個の `debug=True` がクラス全体のロガーを
      差し替えてしまう。TODO-005 から回した）

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

## TODO-015. ruff の整形・書き換え系の指摘を解消

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] `UP031`（printf 書式 → f-string、35 件）
- [ ] `DTZ011` / `DTZ005`（`date.today()` などに tz が無い、14 件）
- [ ] `FLY002`（テスト内の `'\t'.join([...])`、13 件）
- [ ] `D419`（空の docstring、10 件）
- [ ] `RUF012`（mutable-class-default、5 件）
- [ ] `EXE001`（shebang-not-executable、4 件）— TODO-008
      （`uv tool install` 方式）で起動方法を決めたあとに扱う
- [ ] `SIM102` / `C408` / `PERF402` / `PLC0206` / `SIM118`（残り 6 件）
- [ ] `uv run ruff check --fix --extend-select I src tests` が通ることを
      確認する

TODO-004（lint・型チェックと mise タスク）で `mise run lint` を実行した際、
`ruff check` が 97 件のエラーで止まった。うち `RUF013`
（implicit-optional）はいずれも TODO-006（型ヒントの整備）の範囲なので
ここでは扱わない。`EXE001` は起動スクリプトの扱いが決まる TODO-008 の
あとに回す。

---

## TODO-016. `date` が空の POST と、存在しない `sde_id` の扱い

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier

- [ ] `date` が空のまま非 ToDo の予定を追加したときの扱いを決めて直す
- [ ] 存在しない `sde_id` を渡されたときの扱いを決めて直す

`date` を空にして、ToDo ではない予定を `cmd=add` で POST すると、
`exec_update()` が `date = None` のまま `add_sde(None, sde)` を呼ぶため、
**予定が `ToDo.cgi` に書かれる**。`edit.html` の日付欄は必ず埋まるが、
`type="date"` の入力は手で空にできるので到達する。

`edit_handler.py:95` の `sde = sdf.get_sde(sde_id)` も、存在しない
`sde_id` を渡されると `None` を返し、`edit.html:5` の `sde.date` で落ちる。

どちらも TODO-006 より前からある挙動。TODO-006（型ヒントの整備）で
`get_sde()` の戻り値が `SchedDataEnt | None` になった際、
`main_handler.py` の guard で **失敗が黙って 200 で返る**ようになったため、
暫定で `warning` を 1 行足してある。根本の対処はここで決める。

（TODO-006 の reviewer の指摘 1-1 と 2-2 から。
`archives/agents/TODO-006/reviewer-report.md` に詳しい）

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-006.** 型ヒントの整備](archives/todo/TODO-006.%20型ヒントの整備.md)
- [**TODO-004.** lint・型チェックと mise タスク](archives/todo/TODO-004.%20lint・型チェックと%20mise%20タスク.md)
- [**TODO-014.** サブエージェントの報告ファイル名](archives/todo/TODO-014.%20サブエージェントの報告ファイル名.md)
- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
