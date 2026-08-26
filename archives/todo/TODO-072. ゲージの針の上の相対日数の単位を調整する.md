# TODO-072. ゲージの針の上の相対日数の単位を調整する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |
| 消費 | output 21,527 / cache_creation 108,925 / 概算 $2.5 |
|      | main 91% + verifier 9%（料金の割合） |

## きっかけ

ヘッダの横ゲージには、今週からどれだけ離れた週を見ているかを示す針が
あり、その上に差を出している（TODO-066）。この差が週数だけだったので、
遠い週を開くと `+157w` のような桁の大きい数字になり、どのくらい先なのか
とっさに読めなかった。ゲージの目盛りのほうは `1m`・`1y`・`10y` と
単位が変わる（TODO-059）のに、針の上だけ週数のままだった。

1 ヶ月からは月数、1 年からは年数に切り替える。

## やったこと

差の日数の大きさで、単位を切り替えるようにした。

| 差 | 出る文字 |
|---|---|
| 0 | `±0` |
| 1 ヶ月未満 | `+3w` |
| 1 ヶ月以上 1 年未満 | `+1.2m` |
| 1 年以上 | `+1.2y` |

月と年は小数点以下 1 桁。1 年 = 365.25 日、1 ヶ月 = 365.25 / 12 =
30.4375 日で計算する。この 2 つは `main_handler.py` に `DAYS_YEAR`・
`DAYS_MONTH` として既にあり（ゲージの目盛りが使っている）、そのまま
使えた。

境界は、月曜どうしの差なので 7 日刻みに飛ぶ。4 週（28 日）はまだ週数で、
5 週（35 日）から月数になる。52 週（364 日）はまだ月数（`+12.0m`）で、
53 週（371 日）から年数になる。

- `src/ytsched/main_handler.py` — `calc_week_diff()` を
  `calc_gage_label()` に置き換えた。週数を返す関数から、出す文字その
  ものを返す関数にした。`calc_week_diff()` は使われなくなったので消した
- `src/ytsched/webroot/static/js/my.js` — `weekDiffLabel(weeks)` を
  `gageDiffLabel(days)` に置き換え、`DAYS_MONTH` を足した
- `src/ytsched/webroot/templates/main.html` — `{% if week_diff %}` と
  書式指定をやめ、`{{ gage_label }}` を出すだけにした

### 書式をテンプレートから Python 側へ移した

これまでは、サーバ側が週数（`int`）を渡し、テンプレートが
`'%+dw' % week_diff` と書式を当て、今週のときだけ `±0` に分ける、と
いう作りだった。単位が 3 通りに増えると、この分岐がテンプレートの中で
膨らむ。書式を Python 側へ寄せ、テンプレートは受け取った文字を出す
だけにした。

### 同じ規則が 2 箇所にある

針の上の文字は、**読み込んだ直後の一度だけサーバが埋め、あとは
JavaScript が書き換える**（週送りでページを読み直さないため）。
区切りや丸め方が食い違うと、針が動く前後で文字が変わって見える。
両方の docstring から相手を名指しして、片方だけ直さないようにした。

## テスト

- `tests/test_main_handler.py` — `test_calc_week_diff()` を
  `test_calc_gage_label_rounds_to_monday()` に書き換え、単位の
  切り替えを見る `test_calc_gage_label_switches_unit()` を足した。
  境界（4w / 5w / 52w / 53w）を直接見ている
- `tests/test_web.py` — `test_unit_switches_to_months_and_years()` を
  足し、実際に返る HTML の中の文字を見る

**Python 側と JavaScript 側の出力を突き合わせた。** -30y〜+30y の
全週 3201 通りで一致（main と verifier がそれぞれ独立に確認）。
`%+.1f` と `toFixed(1)` は丸め方が違うことがあるが、差が 7 日刻みで
飛ぶこの範囲では分かれなかった。

verifier の報告は
[archives/agents/TODO-072/verifier-report.md](../agents/TODO-072/verifier-report.md)。
lint・455 件のテスト・ブラウザテスト 9 件・実アプリの起動確認まで通り、
指摘は無かった。分担の理由は
[archives/agents/TODO-072/README.md](../agents/TODO-072/README.md)。

## 気づいたこと

**`ruff format` をオプション無しで叩いてはいけない。** `mise.toml` の `fmt` は
`--line-length 78` を渡している。そのまま叩くと ruff の既定の 88 が使われ、
無関係な 16 ファイルが整形し直された（`git checkout` で戻した）。
混ぜたままコミットすると、次に `mise run fmt` を叩いたときに 78 へ
戻されて、88 と 78 の間を往復することになる。
