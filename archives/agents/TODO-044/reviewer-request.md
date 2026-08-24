# TODO-044 reviewer への依頼

`TODO.md` の TODO-044 の節と、
`archives/agents/TODO-044/implementer-report.md` を読んでから始めること。

## 見てほしいもの

`tools/token-usage.py` の変更（`git diff` で出る）。

**数え方そのものを変えた項目**なので、テストが通ることは正しさの
根拠にならない。特に次を見てほしい。

- **`collect()` の重複の除き方。** 同じ `(requestId, message.id)` の
  行から各項目の最大値を採る形になっているか。`messages` を 1 のまま
  にしている扱いは妥当か。key が `(None, None)` になる行（`requestId`
  が無い行）が混ざったときに、別々のリクエストを 1 件にまとめて
  しまわないか
- **料金の計算。** `cache_creation` に 1.25 倍、`cache_read` に 0.1 倍を
  掛けているか。`input`（キャッシュに載らなかった入力）も数えているか。
  `output` に出力単価を使っているか。1M で割る位置は正しいか
- **`price_for()` の前方一致。** `claude-opus-5` と `claude-opus-4-8`
  のように前方が重なる名前で誤って引かないか。表に無い名前の扱い
- **`fmt_shares()` と `sum_by()` を料金基準にしたこと。** 料金が 0 の
  ときに割り算で落ちないか
- 既存の書き方（`Usage` の使い方、ログ、docstring）から外れていないか

## 決まりごと

- **コードを直さない。** 見つけたことは報告に書き、直すかどうかは
  main が判断する
- 指摘には**ファイル名と行**を付ける。**どういう入力でどう間違うか**を
  書く（「気になる」だけでは判断できない）
- 報告は `archives/agents/TODO-044/reviewer-report.md`。返事は 5 行以内
