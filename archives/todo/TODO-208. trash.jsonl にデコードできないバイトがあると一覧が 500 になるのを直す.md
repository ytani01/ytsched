# TODO-208. trash.jsonl にデコードできないバイトがあると一覧が 500 になるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Sonnet 5.5 / 記載なし | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | 記載なし | 54 | 9,262 | 62,099 | 1,717,408 | 82% |
| reviewer | Opus 5.5 | high | 20 | 2,128 | 41,006 | 290,503 | 15% |
| verifier | Sonnet 5.5 | medium | 6 | 68 | 22,699 | 41,476 | 3% |
| 合計 |  |  | 80 | 11,458 | 125,804 | 2,049,387 | 計 2,186,729 |

- main は `/model` で Sonnet 5.5 に切り替わっていた（見込みは Opus 5.5）。
  effort は記録に残らないので「記載なし」
- reviewer・verifier は定義のまま（reviewer は opus / high、verifier は
  sonnet / medium）
- 集計は直前の項目（TODO-210）のコミットから、決着の手前まで。
  サブエージェントの分は少なめに出る
- 分担は `archives/agents/TODO-208/README.md`

## きっかけ

`TrashFile` が `trash.jsonl` をテキストモードで開いていて、デコードは
`try` の外（`for line in f`）で起きる。デコードできないバイトが 1 つあると
`UnicodeDecodeError` になる。`count()` は `MainHandler.get()` が毎回呼ぶので、
一覧画面ごと 500 になった。

## やったこと

- `src/ytsched/trash.py`: `entries()`・`count()`・`delete_many()` を、バイトで
  読んで行ごとにデコードする形へ変えた（`SchedDataFile` と同じ）。
  `UnicodeDecodeError` は `ValueError` の仲間なので、`entries()` と
  `delete_many()` は既存の `except` で捕まる。`count()` には `ValueError` を足した
- `delete_many()` は壊れた行を元のバイトのまま残す。そのため `_write_lines()` も
  バイトで書く形にした
- `tests/test_trash.py` に 2 件、`tests/test_web.py` に 1 件（一覧・ゴミ箱画面・
  一括削除）を足した
- `docs/data-format.md` のゴミ箱の節と `src/README.md` に、壊れた行の扱いを追記した

## 確かめたこと

- テストを変更前の `trash.py` に戻すと、新しい 3 件が落ちる（main と reviewer が
  それぞれ確認）
- `mise run lint` / `typecheck` / `test`（715 件）が通る
- 一時ディレクトリの `trash.jsonl` に `\xff` を含む行を入れて実アプリを起動し、
  `/ytsched/` と `/ytsched/trash` がどちらも HTTP 200（verifier）

## 残ること

- `\r` だけで区切られたファイルは、変更前は行に分けて読めたが、今は 1 行として
  扱われ全件が飛ばされる（データは消えない）。手で編集しないかぎり起きず、
  `SchedDataFile` と同じ振る舞いなので、そのままにした（reviewer の報告）

## 分担の振り返り

- reviewer: 確信度の高い指摘は無し。`src/README.md` の言い回し（「デコードできない
  行だけ」が、飛ばす行を限定するように読める）と、`\r` の差を報告した。前者は
  直した。後者は上の「残ること」
- verifier: 実測値（24 件・30 件が通過、実アプリで 200 が 2 つ）を載せて報告した。
  指摘は無し
- 見込みとの食い違い: main が Opus 5.5 でなく Sonnet 5.5 だった。それでも
  実装は 3 か所の小さな変更で、レビューで正しさの問題は出なかった
- 次に同じ規模（1 ファイルの読み込み方の変更 + テスト）をやるなら、この編成の
  ままでよい。reviewer への依頼に「元に戻すと落ちるか」を書いておくと、
  main が先に確かめた分を重ねて確認できる。verifier は定型の実行と実アプリ 1 回
  なので Haiku でも足りたが、実アプリの起動確認は迷いやすいので Sonnet のままにした
