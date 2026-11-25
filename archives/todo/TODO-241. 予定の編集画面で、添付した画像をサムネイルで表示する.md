# TODO-241. 予定の編集画面で、添付した画像をサムネイルで表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / low）+ reviewer（Sonnet 5.5 / low）+ verifier（Haiku 5.5 / low） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Sonnet 5.5 / low）+ verifier（Sonnet 5.5 / low） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 31 | 5,098 | 17,677 | 1,056,928 | 68% |
| verifier-241（verifier） | Sonnet 5.5 | low | 28 | 4,209 | 32,321 | 350,160 | 24% |
| reviewer-241（reviewer） | Sonnet 5.5 | low | 12 | 1,562 | 23,941 | 98,597 | 8% |
| 合計 |  |  | 71 | 10,869 | 73,939 | 1,505,685 | 計 1,590,564 |

- 実装は数行で済んだので、implementer を使わず main が書いた（`CLAUDE.md` の TODO-085 の例外）
- verifier は、Playwright で撮った画像を見て判断する作業を含むので、Haiku 5.5 ではなく Sonnet 5.5 にした
- 項目を追加したときの wording-241（Sonnet 5.5 / low）は、始点のコミットより前に動いたので集計に入っていない

## きっかけ

利用者から「スケジュール編集画面で、添付画像はサムネイルを表示したい」と頼まれた。

## やったこと

- `src/ytsched/webroot/templates/edit.html`: 添付欄のリンクの中で、`attach_store.is_image(name)` が `True` のものだけ `<img loading="lazy">` をファイル名の前に出す。判定は `sde.html` と同じ
- `src/ytsched/webroot/static/css/my.css`: `.my-edit-attach-file img` を最大 6em 四方に抑える
- `tests/test_attach.py`: 編集画面で、PNG には `<img>` が出て、PDF には出ないことを足した
- 縮小した画像のファイルは作らず、元の画像をブラウザで縮めて表示する方式にした（利用者が選んだ）

## 確かめたこと

- `mise run lint`・`mise run typecheck`・`tests/test_attach.py` が通った
- `<img>` を消すと、また全部の添付に `<img>` を出すと、足したテストが失敗した
- 幅 1280px の画面で、400x300 の PNG が約 96x72px に縮んで表示され、PDF は名前だけ、「外す」のチェックボックスも崩れていなかった（`archives/agents/TODO-241/verifier_closed_1280.png`）
- reviewer の指摘「`alt` が `sde.html` と違って空」は確かめた。リンクの中にファイル名があり、読み上げで名前が二重にならないよう空のままにした

## 分担の振り返り

- reviewer は指摘無し（`alt` の違いだけを報告）。verifier も不具合無し。wording は、「真のもの」を「`True` を返すもの」にする案を出し、その案のとおりに直した
- 見込みとの違いは、implementer を使わなかったことと、verifier を Sonnet にしたこと。見た目の確認を入れるなら、見込みの段階で Sonnet と書くべきだった
- 次にテンプレートと CSS を数行変える項目では、main が実装し、reviewer（Sonnet / low）と verifier（Sonnet / low、見た目を撮る場合）で組む。`model-check.md` の判定は、どれも「適切」だった
