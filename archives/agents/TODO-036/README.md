# TODO-036 の担当

見込み: implementer + verifier + wording
実施: implementer + verifier + reviewer + **wording**

## 分担をこうした理由

- **implementer を分けた。** 変更が `click_utils.py`（新規）・`__main__.py`・
  `webapp.py` の 3 ファイルにまたがり、CLI の実挙動の確認まで要ったため。
  「複数のファイルにまたがる」の目安に当たる
- **verifier を分けた。** `~/.claude/CLAUDE.md` のとおり、コードを変える項目
  では確認を必ず別の担当にする。今回は試せる手順（`--version` / `--help` /
  `--debug` の 4 通り、`webapp` の起動と curl、文書のコマンド例）がまとまって
  あったので、書式の確認だけで済む類いではなかった
- **reviewer を後から足した。** 見込みには入れていなかったが、実装が上がって
  みると CLI の挙動が変わっていた（`--version` の経路、グループ側の
  `--debug` の合成）。`CLAUDE.md` の「挙動や分岐が変わる項目には入れる」に
  当たると判断した
- **wording は 2 回立てた。** 立てるコミット（`TODO.md` と依頼書）と、
  実装コミット（archives・`src/README.md`・報告ファイル）でそれぞれ

## 報告

- [implementer への依頼](implementer-request.md) /
  [報告](implementer-report.md)
- [verifier への依頼](verifier-request.md) / [報告](verifier-report.md)
- [reviewer への依頼](reviewer-request.md) / [報告](reviewer-report.md)
- [wording の報告](wording-report.md)

## 振り返り

- **reviewer を入れた判断は当たった。** 動作を壊す欠陥は出なかったが、
  `src/README.md` のモジュール一覧に `click_utils.py` が抜けている追随漏れと、
  `mylog.loggerInit()` の docstring「1 度だけ呼ぶ」が実態と合わなくなった
  ことは、テストが通ることを見ても出てこない
- **implementer が自分で決めた追加（`cli` への `loggerInit()`）から、
  紛らわしい挙動が見つかった。** 報告に「依頼書に無い追加なので、不要なら
  消してよい」と書かせていたので、main が実際に動かして
  `ytsched --debug migrate` が効かないことを確かめ、利用者に判断を仰げた。
  単独で決めたことを報告させる形が効いた例
