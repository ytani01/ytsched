# TODO-186. スマホでゲージをドラッグすると、指を止めても追従しない

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ + verifier + reviewer |
| 実施 | Opus 5 / effort high | main のみ + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 7,816 | 48,395 | 64% |
| reviewer | Sonnet 5 | high | 5,771 | 47,856 | 24% |
| verifier | Sonnet 5 | medium | 1,191 | 30,354 | 12% |
| 合計 |  |  | 14,778 | 126,605 | 概算 $1.6 |

- どちらも定義（`.claude/agents/*.md`）のモデル・effort のまま。上書きなし
- 集計は `--since '2026-09-05 19:31:07'`（TODO-185 の feat コミットの時刻）で
  切った。立てたのが TODO-185 の作業中だったので、指定しないとそちらまで数に入る

## きっかけ

マウスでドラッグしたときは、手を止めると追従して画面が移るのに、
スマホのタップドラッグでは待っても追従しなかった。

`gaugeBarPointerMoveHdr` が最後に必ず `startGaugeBarFollowTimer()` を呼び、
そこで `clearTimeout()` してタイマーを張り直していたため（TODO-178）。
マウスは手を止めれば pointermove が止まるが、指は押さえたままでも微細な
揺れで pointermove が出続けるので、タイマーが張り直され続けて発火しない。

`mondayFromClientX()` は週へ丸めるので、数 px の揺れでは移動先の週は
変わっていないのに、タイマーだけがリセットされていた。

## やったこと

`src/ytsched/webroot/static/js/gauge.js` の `gaugeBarPointerMoveHdr` で、
上書きする前の `gaugeBarDragMonday` を `prev_monday` に取っておき、
**移動先の週が変わったときだけ** `startGaugeBarFollowTimer()` を呼ぶようにした。

針の `left` とラベルは、これまでどおり pointermove のたびに動かす。
待ち時間そのもの（TODO-185 の `GaugeFollowMsec`）は変えていない。

## テスト

`tests/test_browser.py` に `test_gauge_drag_follows_while_jittering` を足した。
pointerdown のあと ±0.6px の揺れを 50ms ごとに与え続け、それでも
`.my-week-cur` が移動先の週になることを見る。

- `uv run pytest tests/test_browser.py -k gauge` … 16 件すべて通過
- `gauge.js` だけ変更前へ戻すと、新しいテストが落ちることを確認した
- `mise run lint` / `mise run typecheck` … エラーなし

## 分担の振り返り

- **verifier** は 3 点（テスト実行・修正前で落ちること・lint/typecheck）を
  そのまま実行し、指摘は無し。ただし「修正前だと落ちる」の確認は、この項目で
  いちばん意味のある検証で、分けた価値はあった
- **reviewer** は確信度の高い指摘を出さなかったが、こちらが気にしていた
  「先読みされていない週でタイマーが張られなかったあと、張り直されなくなる」の
  実害を、週パネルが読み込み時に固定で動的に増えないことから否定した。
  分岐の変更なので入れた判断自体は変えない
- **見込みとの食い違いは無し。** 1 ファイル数行の変更なので implementer は立てず、
  main が直接書いた
- 次に同じ規模（1 ファイルの条件式を変えるだけ、テスト 1 件追加）をやるなら、
  同じ `main + verifier + reviewer` でよい。reviewer が料金の 24% を占めたが、
  分岐が変わる項目では省かない
