# TODO

**残っている項目: TODO-016。**
これまでに 15 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-017` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データ形式（タブ区切りテキスト）とデータディレクトリ
`~/ytsched/data` は、既存データとの互換のため変えない。

着手する項目は利用者が指定する。

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

- [**TODO-015.** ruff の整形・書き換え系の指摘を解消](archives/todo/TODO-015.%20ruff%20の整形・書き換え系の指摘を解消.md)
- [**TODO-012.** 不正な正規表現を入れられたときの扱い](archives/todo/TODO-012.%20不正な正規表現を入れられたときの扱い.md)
- [**TODO-010.** CLAUDE.md の作成](archives/todo/TODO-010.%20CLAUDE.md%20の作成.md)
- [**TODO-009.** README の更新](archives/todo/TODO-009.%20README%20の更新.md)
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
