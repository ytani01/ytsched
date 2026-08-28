# TODO-104. 月間ミニカレンダーの表示を切り替えるスイッチ

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 実施 | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 消費 | output 19,608 / cache_creation 326,245 / 概算 $4.1 |
|      | main 41% + implementer 35% + reviewer 12% + verifier 9% + wording 3%（料金の割合） |

分担は [archives/agents/TODO-104/](../agents/TODO-104/) にある。

## きっかけ

TODO-103 で日曜日の下に月間ミニカレンダー 2 ヶ月分を出したが、
常に出ていると週の予定を見るときに邪魔になることがある。
出したり消したりできるようにする。

## やったこと

- 設定は `conf.json` の `MonthCal`（`"1"` = 出す / `"0"` = 出さない、
  既定は出す）。他の設定と同じ `update_conf_arg()` の仕組みに載せ、
  `ConfArgs` の 5 つ目として返す。変換は `handler_util.str2month_cal()`
  で、`"1"` / `"0"` 以外は `ValueError`（不正な値を `conf.json` へ
  保存させない。TODO-027 と同じ扱い）。
- `mk_weeks()` に `month_cal` を渡し、出さないときは
  `mk_month_cals()` を呼ばない。**`load_month_cal()` の `stat()` が
  丸ごと省ける**（1 週あたり 2 ヶ月分 × 週パネルの数）。
- `main.html`: `.my-mini-cal-row` の中にスイッチを置いた。アイコンは
  既存の `#check-square` / `#square` を `month_cal` で切り替える。
  押すと `doPost()` で `date`（その週パネルの月曜）と反転した
  `month_cal` を送り、POST → GET で描き直す（TODO-050）。
  **消しているときもスイッチは残す**（残さないと戻せない）。
- `my.css`: 行を `position: relative` にして、スイッチだけ
  `position: absolute` で左上に重ねた。テーブルは
  `justify-content: center` のまま中央に残る。ミニカレンダーが
  無いときに行が潰れないよう `min-height` を持たせてある。
- 検索モードでは、今までどおりミニカレンダーもスイッチも出さない。

reviewer の指摘は無し。verifier から出たスイッチの大きさ（16px では
指で押しにくい）を受けて、アイコンを `my-icon-lg`（20px）にし、
`padding` で当たり判定を広げた（「当たり判定」は `my.css` の既存の
コメントで使っている語に揃えた）。

## テスト

- `mise run lint` / `mise run typecheck`: 緑。
- `uv run pytest`: 502 passed。TODO-103 のときと同じく
  `test_browser.py::test_tap_again_stops_auto_page_turn` が 1 件落ちるが、
  変更を `git stash` した状態でも落ちる既存のタイミング依存のテストで、
  今回の変更が原因ではないことを確かめた。
- 足したテストは 8 本。`str2month_cal()` の単体テスト 4 本と、
  週間表示の HTML（既定で出る、`month_cal=0` で消えてスイッチは残る、
  `conf.json` の `"MonthCal": "0"` で引数なしでも消える、切り替えが
  保存される）。検索モードでスイッチも出ないことは、既存のテストに
  足した。
- 一時 datadir でアプリを起動し、幅 412px で画面を確かめた。
  ON / OFF の切り替え、読み直しても消えたまま、`conf.json` の内容、
  週を送った先の週パネルでも効くこと、検索したときに出ないこと、
  横スクロールが出ないこと、`"MonthCal": "xyz"` のような不正な値でも
  既定（出す）で画面が出ること。
