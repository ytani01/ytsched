# TODO-210. SchedDataFile.save() の .bak をハードリンクで作り、本体が無い時間をなくす

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Haiku 4.5、定型の実行） |
| 実施 | Sonnet 5.5 / 記載なし | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Haiku 4.5） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | 記載なし | 36 | 9,330 | 17,358 | 1,451,371 | 57% |
| reviewer | Opus 5.5 | high | 32 | 2,288 | 45,127 | 530,404 | 22% |
| verifier | Haiku 4.5 | 記載なし | 154 | 1,901 | 36,545 | 495,696 | 21% |
| 合計 |  |  | 222 | 13,519 | 99,030 | 2,477,471 | 計 2,590,242 |

- main は `/model` で Sonnet 5.5 に切り替わっていた（見込みは Opus 5.5）。
  effort は記録に残らないので「記載なし」
- verifier は定義が sonnet / medium。定型の実行なので Haiku 4.5 に上書きした。
  Haiku は effort に対応しない
- 集計は立てたコミットから現在時刻まで。決着の作業の分は含まない。
  サブエージェントの分は少なめに出る

## きっかけ

TODO-207 で `.bak` を「一時ファイルへ書き終えてから元のファイルを移す」形に
したが、移してから `replace()` するまでの間は本体が無く、この間に落ちると
その日は空に見える（reviewer の指摘。実害は未確認）。利用者がハードリンクで
`.bak` を作る案を採用した。

## やったこと

- `src/ytsched/ytsched.py`: `SchedDataFile.__make_backup()` を足した。
  一時名で本体のハードリンクを作り、それを `.bak` へ `replace()` する。
  `save()` はそのあとで一時ファイルを本体へ `replace()` する。本体を移さない
  ので、本体が無い時間も `.bak` が無い時間もない
- `os.link()` か `.bak` への `replace()` が `OSError` になったときは、
  一時名のリンクを消して `shutil.move()` に戻る（debug ログを出す）
- `tests/test_ytsched.py` に 3 件: 本体の差し替えで失敗しても本体と `.bak` が
  残る、`os.link` が使えないとき `.bak` へ移す、リンクは作れたが `.bak` への
  差し替えで失敗したとき一時名のリンクを残さない
- `docs/data-format.md` の「バックアップ」の節と、
  `docs/obsidian-format-review.md` の「保存」の行を実装に合わせた

## 確かめたこと

- `uv run pytest -q` 712 件通過、`ruff format --check`・`ruff check`・
  `basedpyright`・`mypy` 通過（verifier）
- 一時ディレクトリで 2 回保存し、`.bak` と本体は別 inode（`st_ino` 442383 と
  442384）、どちらも `st_nlink` は 1、`.` 始まりの一時ファイルは残らない
  （verifier）
- テストの強さ: `os.link` を使わない旧版に戻すと本体差し替えのテストが落ちる
  （reviewer）。一時名のリンクを消す `unlink` 行を消すと 3 件目が落ちる
  （main が確認）

## 残ること

`os.link()` と `.bak` への `replace()` の間で SIGKILL や `KeyboardInterrupt`
が入ると、一時名のリンク `.<ファイル名>.bak.<uuid>` がゴミとして残る。
本体は無事で、データの走査（glob）にも当たらない。実害は未確認なので、
対応しない。

## 分担の振り返り

- **reviewer**: テストで捕まえられない行（`unlink`）、fallback のログが無い
  こと、fallback の条件と文書の書き方のずれ、SIGKILL で残るゴミを見つけた。
  前 2 つは直した。「作業ツリーを変えずに、行を消したコピーで試す」を依頼に
  入れたことが、テストの穴を見つけることにつながった
- **verifier**: 問題は見つからなかった。inode と `st_nlink` の実測値が報告に
  載っていた。報告の「ハードリンク未使用」は、差し替え後の最終状態を読んだ
  ものなので、読み間違いではないが紛らわしい
- 見込みとの食い違い: main が Sonnet 5.5 になった。品質に影響は出なかった
- 次に同じ規模なら同じ組み方でよい。reviewer の依頼には、最初から
  「追加したテストが守っている行を 1 行ずつ消して落ちるか」を入れておく
  （今回は main が確認した分が後から出た）
