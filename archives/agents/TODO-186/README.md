# TODO-186 の分担

`gauge.js` の `gaugeBarPointerMoveHdr` で、追従タイマーを張り直す条件を
「pointermove が来たか」から「移動先の週が変わったか」へ変えた項目。

- **implementer は立てていない。** 1 ファイル数行の条件式の変更なので、
  main が直接書いた
- **verifier**（[報告](verifier-report.md)）— テストの実行、修正前だと
  新しいテストが落ちることの確認、lint / typecheck
- **reviewer**（[報告](reviewer-report.md)）— 分岐が変わる項目なので入れた。
  とくに「先読みされていない週でタイマーが張られなかったあと張り直されない」
  経路の実害を見てもらった

項目そのものは
[archives/todo/TODO-186](../../todo/TODO-186.%20スマホでゲージをドラッグすると、指を止めても追従しない.md)。
