# TODO-238. テストの説明文書の一覧に、載っていない 3 つのテストを足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書）+ reviewer（Sonnet 5.5 / medium）+ verifier（Haiku 5.5 / low） |
| 実施 | Opus 5.5 / effort medium | main（文書）+ reviewer（Sonnet 5.5 / medium）+ verifier（Haiku 5.5 / low） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 34 | 4,202 | 35,832 | 829,183 | 77% |
| reviewer-238（reviewer） | Sonnet 5.5 | medium | 16 | 1,960 | 29,583 | 157,106 | 17% |
| verifier-238（verifier） | Haiku 5.5 | low | 6 | 1,188 | 23,743 | 43,531 | 6% |
| 合計 |  |  | 56 | 7,350 | 89,158 | 1,029,820 | 計 1,126,384 |

- verifier は定義のモデルを Haiku 5.5 に上書きした（突き合わせるだけの定型の確認のため）
- 集計は `--since '2026-11-25 06:00:00'`（項目を立ててから作業を始めるまでに TODO-239 の追加と TODO-237 の完了を挟んだため）

## きっかけ

TODO-237 の作業中に implementer が、`tests/README.md` の一覧に `test_fix_id.py`・`test_notify.py`・`test_trash.py` が無いことを見つけた（`archives/agents/TODO-237/implementer-report.md`）。

## やったこと

- `tests/README.md` の「各ファイルの役割」に 3 つを足した。`test_trash.py` は `test_attach.py` の後、`test_fix_id.py` は `test_migrate.py` の後、`test_notify.py` は `test_holiday.py` の後に置いた
- README には TODO 番号を書かない決まりがあり、hook が止めたので、番号は書いていない

## 確かめたこと

- reviewer: 説明の誤り・言い過ぎは無し（`archives/agents/TODO-238/reviewer-report.md`）。「検討」として挙がった抜け（`test_notify.py` の memo・detail・ToDo の範囲、`test_trash.py` の版の扱い・パーミッション）は、一覧は要約なので書き足さないと main が判断した（確かめた）
- verifier: 一覧と `tests/*.py` が 16 件ずつ過不足なく一致（`archives/agents/TODO-238/verifier-report.md`）

## 分担の振り返り

- reviewer は誤りを見つけず、要約から漏れた観点を挙げた。verifier は食い違いを見つけなかった
- 見込みと食い違いは無かった
- 次に同じ規模（一覧に数行を足すだけ）なら、verifier の突き合わせは main が `ls` と `rg` で 1 回済ませられる。ただし、ファイルを変える項目では verifier を省かない決まりなので、Haiku 5.5 / low のまま置く。reviewer の依頼で「抜けは要約なので挙げなくてよい」と書けば、報告が短くなる
