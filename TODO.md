# TODO

**残っている項目: TODO-009、TODO-010、TODO-012、TODO-015、TODO-016。**
これまでに 11 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-017` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

進める順序は依存関係で決めてある（TODO-008 が済んだので、TODO-009 に
進める）。着手する項目は利用者が指定する。

---

## TODO-009. README の更新

見込み: main = Sonnet 5 / effort low、担当 = writer + verifier

- [ ] 「Install: TBD」を書く（`uv tool install` の手順と、
      systemd --user のユニット例。中身は TODO-008 で決まる）
- [ ] 「使用環境」を Python 3.14 / uv に直す
- [ ] 「課題・問題点」の文面を整える

`verifier` には、README に書いたコマンドが実際に動くかを確かめさせる。

**「課題・問題点」の 2 点（検索機能の改良、期間・繰り返し予定）は、
どちらも今も未解決なので内容は変えないと決めた**（2026-08-20）。
文面を整えるだけにする。

---

## TODO-010. CLAUDE.md の作成

見込み: main = Opus 5 / effort medium、担当 = verifier

- [ ] 移行後の構成・コマンド・設計の勘所をまとめる

移行が一通り済んでから書く。全体を把握している main が書き、
`verifier` に「書いた内容が実物と合っているか」を確かめさせる。

---

## TODO-012. 不正な正規表現を入れられたときの扱い

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier

- [ ] 不正な正規表現のときは、フィルタ・検索を無視して全件表示にする
- [ ] 壊れていることを画面に短く知らせる

`filter_str` / `search_str` は利用者の入力をそのまま `re.search` に
渡している。`re.error` を捕まえたあと `continue` しているため、
**打ち掛けの正規表現（`(` だけ、など）を入れた瞬間に全件が消える**
（警告はログにしか出ない）。安全側に倒して「フィルタを無視して全件出す」
挙動に変え、画面にも一言出すと決めた（2026-08-20）。

**`base.html` の `{% autoescape None %}` は現状維持（切ったまま）と
決めた**（2026-08-20）。単一ユーザで、リバースプロキシで認証する前提。
自分が書いたものが自分に見えるだけなので実害が無い。
なお、エスケープを切っている理由とされていた「`detail` の `<br />` を
通すため」は、今はもう成り立っていない（`detail` は読み込み時に
`htmlstr2text()` で改行へ戻され、表示は CSS の `white-space: pre-wrap` が
担っている）。それでも、全テンプレートの `{{ }}` を洗い直す手間に
見合わないので戻さない。

---

## TODO-015. ruff の整形・書き換え系の指摘を解消

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] `UP031`（printf 書式 → f-string、35 件）
- [ ] `DTZ011` / `DTZ005`（`date.today()` などに tz が無い、14 件）
      — 規則ごと除外する
- [ ] `FLY002`（テスト内の `'\t'.join([...])`、13 件）
- [ ] `D419`（空の docstring、10 件）
- [ ] `RUF012`（mutable-class-default、5 件）
- [ ] `EXE001`（shebang-not-executable、4 件）— シェバンを消す
- [ ] `SIM102` / `C408` / `PERF402` / `PLC0206` / `SIM118`（残り 6 件）
- [ ] `uv run ruff check --fix --extend-select I src tests` が通ることを
      確認する

TODO-004（lint・型チェックと mise タスク）で `mise run lint` を実行した際、
`ruff check` が 97 件のエラーで止まった。うち `RUF013`
（implicit-optional）は TODO-006（型ヒントの整備）で、`UP031` の 1 件は
TODO-007（loguru への移行）で消えている。

2026-08-20 に決めたこと。

- **`DTZ011` / `DTZ005` は規則ごと除外する。** 手帳代わりのソフトで、
  日付はすべて手元のローカル時刻。14 箇所に tz を付けて回るのは
  ノイズにしかならない。**除外は `pyproject.toml` の
  `[tool.ruff.lint]` に書く**（コマンドラインに書くと、素の
  `uv run ruff check` やエディタの LSP では出たままになるため）。
  TODO-004 で決めた「`pyproject.toml` に `[tool.ruff]` を持たない」
  流儀からは、ここだけ外れる
- **`EXE001` はシェバンを消す。** `handler.py` などは単体で実行しない
  モジュールで、相対 import を使っているので直接実行しても動かない。
  入口は `uv tool install` で入る `ytsched`（TODO-008）

---

## TODO-016. `date` が空の POST と、存在しない `sde_id` の扱い

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier

- [ ] `date` が空の非 ToDo は、今日の予定として保存する
- [ ] 存在しない `sde_id` には 404 を返す（編集画面・更新経路とも）
- [ ] TODO-006 で暫定に足した warning を見直す

`date` を空にして、ToDo ではない予定を `cmd=add` で POST すると、
`exec_update()` が `date = None` のまま `add_sde(None, sde)` を呼ぶため、
**予定が `ToDo.cgi` に書かれる**。`edit.html` の日付欄は必ず埋まるが、
`type="date"` の入力は手で空にできるので到達する。

`edit_handler.py:95` の `sde = sdf.get_sde(sde_id)` も、存在しない
`sde_id` を渡されると `None` を返し、`edit.html:5` の `sde.date` で落ちる。

どちらも TODO-006 より前からある挙動。TODO-006（型ヒントの整備）で
`get_sde()` の戻り値が `SchedDataEnt | None` になった際、
`main_handler.py` の guard で **失敗が黙って 200 で返る**ようになったため、
暫定で `warning` を 1 行足してある。

（TODO-006 の reviewer の指摘 1-1 と 2-2 から。
`archives/agents/TODO-006/reviewer-report.md` に詳しい）

2026-08-20 に決めたこと。

- **`date` が空の非 ToDo は、今日の予定として保存する。**
  `SchedDataEnt` は既に「`date` が `None` なら今日」としているのに、
  `cmd_add()` だけが `add_sde(None, ...)` を呼んでいて食い違っている。
  書き込み先を `new_sde.date` に合わせる
- **存在しない `sde_id` には 404 を返す。** 今は編集画面が 500、
  更新経路は黙って 200 という、ばらつきがある

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-008.** uv tool install 方式へ](archives/todo/TODO-008.%20uv%20tool%20install%20方式へ.md)
- [**TODO-007.** loguru への移行](archives/todo/TODO-007.%20loguru%20への移行.md)
- [**TODO-006.** 型ヒントの整備](archives/todo/TODO-006.%20型ヒントの整備.md)
- [**TODO-004.** lint・型チェックと mise タスク](archives/todo/TODO-004.%20lint・型チェックと%20mise%20タスク.md)
- [**TODO-014.** サブエージェントの報告ファイル名](archives/todo/TODO-014.%20サブエージェントの報告ファイル名.md)
- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
