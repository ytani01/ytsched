# TODO-218. ミニカレンダーの前後の月の日にも、土日祝の色を付ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 70 | 11,136 | 28,836 | 2,640,767 | 74% |
| verifier | Sonnet 5.5 | medium | 36 | 261 | 40,089 | 513,026 | 15% |
| reviewer | Opus 5.5 | high | 22 | 1,313 | 42,645 | 336,773 | 11% |
| 合計 |  |  | 128 | 12,710 | 111,570 | 3,490,566 | 計 3,614,974 |

- reviewer・verifier は定義のモデル（opus / sonnet）と effort のまま

## きっかけ

2027/05 のミニカレンダーで、前の月の 4/29（休日を登録済み）が赤くならないと
利用者から報告があった。`mini_cal.html` が曜日・休日のクラスを `d.in_month` の
ときだけ足していたため（TODO-129 で決め、TODO-134 でも残した方針）。利用者と
相談して、その月の日と同じ色にすることにした。着手前に、休日の予定は背景色で
分かるのでドットを出さない、という依頼も加わった。

## やったこと

- `src/ytsched/webroot/templates/mini_cal.html`: 土日祝のクラスを付ける条件から
  `d.in_month` を外した。前後の月の日との区別は文字色（`.my-mini-cal-day-out`）だけ
- `src/ytsched/sched_load.py`: `load_month_cal()` で、休日の予定を除いた一覧から
  `has_sched` / `has_important` を判定するようにした。`is_holiday` は今までどおり
- テスト: `tests/test_web.py` に前後の月の休日のセルの class を見るテストを足し、
  埋めセルの class を見る既存のテストを土曜のクラス込みに直した。
  `tests/test_main_handler.py` に、休日だけの日はドットなし・他の予定もある日は
  ドットあり・重要の印は休日では付けない、を見るテストを足した

## 確かめたこと

- lint・型チェック・テスト 722 件が通った
- 足したテストは、変更を戻すと落ちる（reviewer と main で確認）
- Playwright で、前後の月の休日・土・日のセルが、その月側の同じ日と同じ背景色に
  なり、休日だけの日にドットが出ないことを実測した（`archives/agents/TODO-218/`）

## 分担の振り返り

- reviewer は、`has_important` の変更を見ているテストが無いことを見つけた
  （main がテストを足した）。verifier は食い違いを見つけなかった
- 見込みどおりで、食い違いは無かった
- 次に同じ規模（テンプレートの条件 1 つと判定 1 つ）なら同じ組み方でよい。
  verifier の実測はドットと色の読み出しだけなので、Sonnet より下げる余地はあるが、
  Playwright の起動まで任せるので Sonnet のままにする
