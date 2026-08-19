# TODO

**残っている項目: TODO-004、TODO-006〜TODO-010、TODO-012、TODO-014。**
これまでに 6 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-015` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

進める順序は依存関係で決めてある（TODO-005 が済んだので、TODO-006 に
進める）。着手する項目は利用者が指定する。

---

## TODO-004. lint・型チェックと mise タスク

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier

- [ ] ruff / mypy / basedpyright を dev 依存に追加
- [ ] `mise.toml`（`upgradeproject` → `lint` → `test` → `build`）
- [ ] 行長 78 で整形

`tmr` と同じ構成に揃える。

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

## TODO-014. サブエージェントの報告ファイル名

見込み: main = Sonnet 5 / effort medium、担当 = verifier

- [ ] `~/.claude/CLAUDE.md` の `report-<担当名>.md` の記述を直す
- [ ] `.claude/agents/*.md` 4 ファイルの同じ記述を直す
- [ ] `archives/agents/TODO-005/report-*.md` 3 ファイルを `git mv` で改名
- [ ] Claude Code を再起動して（実行するのは利用者）、`verifier` に
      **実際に新しい名前で報告ファイルを書かせて確かめる**

TODO-013 で `archives/agents/TODO-NNN/report-<担当名>.md` と決めたが、
**この名前ではサブエージェントが書けない**ことが TODO-005 で分かった。
implementer・verifier・reviewer の 3 通とも弾かれ、main が転記した。

原因はフックでも権限設定でもなく、**Claude Code 本体（v2.1.235）に
組み込まれたガード**。バイナリ内に次がある。

```
^(REPORT|SUMMARY|FINDINGS|ANALYSIS).*\.md$      ← 直前に i フラグ
tengu_subagent_md_report_blocked
Subagents should return findings as text, not write report files.
Include this content in your final response instead.
```

サブエージェントが Write ツールでこの名前のファイルを作ろうとすると
弾かれる。中身も置き場所も関係なく、**名前の先頭 4 語だけ**が条件。

**`report-<担当名>.md` → `<担当名>-report.md` にする**（利用者が決定）。
先頭が `report` でなければ通る。

Bash のヒアドキュメントで書けばガードを迂回できるが、意図的に置かれた
制限を回り込む形になり、将来の版で塞がれても気づけないので、やらない。

`.claude/agents/*.md` は**起動時にしか読まれない**ので、直したら再起動が
要る（実行するのは利用者）。TODO-013 と同じく、再起動後に実際に動かして
確かめるところまでやる。**名前を変えただけで通る保証は、書かせるまで無い。**

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
