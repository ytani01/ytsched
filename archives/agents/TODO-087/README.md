# TODO-087 の分担

更新の実行（`cmd=add/fix/update/del`）を `MainHandler` から
`sched_update.py` へ出した項目。

## なぜこの分担にしたか

見込みの段階で implementer + verifier + reviewer と決めてあり、
そのまま実施した。

- **implementer を分けた。** 移動そのものは機械的だが、`main_handler.py`
  の 5 つのメソッドと新しいモジュール、テスト 2 本にまたがる。
  設計（何をどこへ移すか、`post()` を残すこと）は main が決めて
  [implementer-request.md](implementer-request.md) に書き、
  implementer はそのとおりに作るだけにした
- **verifier を立てた。** 更新の経路はテストが通っても安心できない。
  `add` / `fix` / `update` / `del` の 4 つと、**書き込みが起きる前に
  400 で断る**経路（TODO-027）を、実際にアプリを起動して叩かせた
- **reviewer を入れた。** 「挙動は変えない」が前提の移動なので、
  移す前のコードと突き合わせて差が無いことを確かめる担当が要る。
  TODO-083 と同じで、**変わっていないことを示すため**に入れた

## 依頼書と報告

- [implementer-request.md](implementer-request.md) /
  [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md) /
  [verifier-report.md](verifier-report.md)
- [reviewer-request.md](reviewer-request.md) /
  [reviewer-report.md](reviewer-report.md)
- [wording-report.md](wording-report.md) — これは**項目を立てたとき**の
  もので、TODO.md に書いた文章を見たもの

## 結果

- implementer — 依頼どおり。単独で決めた判断は無し。テストの docstring に
  残った古い言い回し（「`fix` は `cmd_del()` → `cmd_add()` で実装されて
  いる」）を、範囲外として直さず報告してきた
- verifier — 475 件通過、lint 4 種すべて通過。4 経路とも期待どおりの
  302 とデータの変化、不正な日付・時刻はどちらも 400 でファイルは
  作られず、ログに例外なし
- reviewer — 指摘無し。依頼した 7 点すべてを旧コードと突き合わせて確認
