# TODO-085. ゴミ箱の導入

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 18,085 / cache_creation 195,610 / 概算 $2.6 |
|      | main 53% + implementer 31% + verifier 17%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-085](../agents/TODO-085/README.md) にある。

## きっかけ

予定を削除すると、その内容はどこにも残らなかった。編集も内部では
「削除してから追加」なので、編集前の内容が同じように消えていた。
消したものを後から取り戻せるように、消える内容を残す先を作る。

復活させる UI は TODO-086 の範囲で、この項目では**書き込みだけ**を入れた。

## 決めたこと

着手前に利用者と決めた。

- ゴミ箱はデータディレクトリ直下の `trash.jsonl`。日付では分けない
- **追記のみ。** `SchedDataFile.save()`（全件書き直し＋`.bak` への退避）
  とは別の仕組みにする。書き直さないので、失敗しても既にある行は消えない
- 1 行の形は、`SchedDataEnt.to_dict()` の内容の先頭に、消した日時
  `trashed_at`（ISO 8601・秒まで。例: `"2026-08-30T14:23:05"`）を足したもの。
  キー名を他と同じ小文字スネークケースにし、値を文字列にしたのは、
  TODO-086 で同じ ID の候補を見比べるときに人が読めるようにするため
- 追記する場所は **`SchedData.del_sde()` の中**。削除（`del`）も編集
  （`fix`/`update`）も `SchedUpdater.cmd_del()` → `SchedData.del_sde()` を
  通るので、ここ 1 か所で両方をカバーでき、入れ忘れの経路が開かない。
  `SchedUpdater` 側に置く案もあったが、後から `del_sde()` を別の経路で
  呼んだときにゴミ箱を素通りするので採らなかった
- 追記は `save()` まで待たずにその場で行う。ゴミ箱は追記のみなので、
  余分に残る方向の失敗（このあと更新が失敗しても行は残る）の害が小さい

## やったこと

- `src/ytsched/trash.py` を新しく作り、`TrashFile` を置いた。`topdir` を
  受け取り、`add(sde)` で 1 行追記するだけ。親ディレクトリが無ければ作る。
  `SchedDataEnt` を実行時に import すると `ytsched.py` と循環するので、
  `TYPE_CHECKING` の下に置き、`from __future__ import annotations` を付けた
  （このリポジトリでは初出）
- `SchedData.__init__()` で `TrashFile` を 1 つ持ち、`del_sde()` が
  `sdf.del_sde()` を呼ぶ**前**に `sdf.get_sde(sde_id)` で対象を取って
  追記する。見つからなければ何もしない
- `docs/data-format.md` に「ゴミ箱（TODO-085）」の節を足した。
  `src/README.md` のモジュール一覧にも `trash.py` を足した

## テスト

`tests/test_trash.py` を新しく作った（7 件）。`TrashFile` 単体（1 行の形・
キーの並び・親ディレクトリ作成・`~` の展開）と、`SchedData.del_sde()`
経由（削除で 1 行増える／未知の ID では触らない／2 回消すと 2 行になり
順序が保たれる／`SchedUpdater` で fix を再現して編集前の内容が入る）。

verifier が `fmt` / `typecheck` / `lint` / `test`（525 件 pass）に加えて、
一時ディレクトリを `--datadir` に指定してアプリを起動し、HTTP で追加・
削除・編集・ToDo の削除を行って `trash.jsonl` の中身を確かめた。追加だけ
ではファイルが作られないこと、編集で入るのが**編集前**の内容であること、
行が積み上がって既存の行が消えないこと、`trash.jsonl.bak` が作られない
こと、日本語がエスケープされないことを確認。不具合は見つからなかった。
