# TODO-103 の分担

## 誰にどこを

| 担当 | 範囲 | 依頼 | 報告 |
|---|---|---|---|
| implementer | サーバ側（`sched_load.py` / `main_handler.py`）・テンプレート・CSS・テスト・`src/README.md` | [implementer-request.md](implementer-request.md) | [implementer-report.md](implementer-report.md) |
| verifier | lint・型・`pytest`・アプリ起動と画面の確認 | [verifier-request.md](verifier-request.md) | [verifier-report.md](verifier-report.md) |
| reviewer | 変更したコードの質（境界・キャッシュ・テンプレート・テスト） | [reviewer-request.md](reviewer-request.md) | [reviewer-report.md](reviewer-report.md) |
| wording | コミットに入る `.md` の前例の無い語 | — | [wording-report.md](wording-report.md) |
| main | 設計を決める。reviewer の指摘を受けた修正（`sdf_has_sde()`） | — | — |

## この分担にした理由

- サーバ側・テンプレート・CSS・テスト・文書がまとまって要る新機能で、
  `~/.claude/CLAUDE.md` の「複数のファイルにまたがる」「実装とテストと
  文書がまとまって要る」の両方に当たるので、実装を implementer に分けた。
- 新しい分岐（検索モードでは出さない）と新しいデータの組み立てが入るので
  reviewer を入れた（TODO-017 の「挙動や分岐が変わる項目には入れる」）。
- 見た目を変える項目で、テストでは崩れやタップの効きを拾えないため、
  verifier に実際の画面で確かめてもらった。
- `.md` が入るコミットなので wording を立てた。

## main が決めたこと

- 予定の有無は**ファイルを開かずに**見る。日ごとに 1 ファイルなので、
  月 1 枚のカレンダーで 31 回の `stat()` で済む。フィルタ・検索・ToDo は
  反映しない（軽さを優先した）。
- 日付のタップは新しい関数を作らず、既存の `scrollToDate()`（`nav.js`）に
  載せた。DOM にある週なら読み直さずに移り、外なら `doGet()` に倒れる
  という分岐が、そのまま使える。
- 同じ月が複数の週パネルから要るので、`SchedLoader` のインスタンスに
  キャッシュを持たせた（`SchedLoader` はリクエストごとに作られる）。

## reviewer の指摘への対応

- **「予定を全部削除しても、空のファイルが残るのでドットが消えない」**
  → 直した。`SchedData.sdf_has_sde()` を足し、キャッシュに載っていれば
  `sde` の数を、載っていなければファイルの大きさを見るようにした
  （ファイルは開かない）。修正は main が入れ、verifier に追加で確認させた。
- テストの docstring が実際に見ている埋めセルとずれていた件も直した。
- `in_month` の判定で年も見ている理由付けが正確でない（月だけでも
  壊れない）という指摘は、実害が無いのでコードはそのままにした。
