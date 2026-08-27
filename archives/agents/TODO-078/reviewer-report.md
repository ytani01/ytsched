# TODO-078 reviewer 報告

## 結論

指摘無し。依頼書の 5 点を順に確認したが、確信度の高い問題は見つからなかった。

## 確認した内容

1. **観点が減っていないか**
   - `test_handler.py` の `test_days2x_percent_*` 5 本 →
     `test_browser.py` の同名 5 本（`page.evaluate()` で
     `days2xPercent()` を直に呼ぶ形）に 1 対 1 で移っている。
   - `test_main_handler.py` の `calc_gauge_label` の 2 本 →
     `test_browser.py` の `test_gauge_diff_label_reflects_the_week_offset`
     / `test_gauge_diff_label_switches_unit` に移っている
     （丸め・週/月/年の切り替わりの境界値も含めて同じ入力を使っている）。
   - `test_web.py` の 3 本のうち、`test_this_week_shows_plus_minus_zero`
     は既存の `test_gauge_label_is_plus_minus_zero_in_this_week`
     （移設前から `test_browser.py` にあった）と重複するので削除は妥当。
     残り 2 本（`test_week_diff_is_displayed` /
     `test_unit_switches_to_months_and_years`）は上記の
     `test_gauge_diff_label_*` に観点ごと移っている。
   - 目盛りの位置（`-1w`/`+1w`、14 個）を見るテストも新規に追加されている。
   - 観点の欠落は見当たらない。

2. **`-1w`=46.21%、`+1w`=53.79% の期待値**
   - `days2x_percent(-7)` を手計算（`DAYS_GAUGE_K=10`,
     `DAYS_GAUGE_MAX=365.25*30`）すると `x_percent ≈ 3.79`。
     `50±3.79` は `46.21`/`53.79` と一致する。変更前の式のままで
     合っている。

3. **`dispGaugeMarks()` の呼び出し位置**
   - `main.html` の `onloadHdr()` 内、`elGaugeR0` を取得した直後・
     `body_h < win_h` の分岐より **前** に 1 回だけ呼んでいる。
     早期 return する経路・しない経路のどちらもこの行を通過するので、
     二重に呼ばれることはない。
   - `setActiveWeek()`（週送り、DOM 内だけの移動）は `dispGauge()` を
     呼ぶだけで `dispGaugeMarks()` は呼ばない。目盛りは日付に依存しない
     ので再描画が不要という設計と整合している。
   - ページ遷移は `doGet()`/`doPost()` とも `location.href` 変更か
     フォーム送信によるフルリロードで、bfcache 復元時は `pageshow`
     ハンドラがスピナーだけを処理し `onloadHdr()` を再度呼ばないため、
     目盛りが重複して追加される経路も見当たらなかった。

4. **`my.js` のコメント**
   - 「二重に持っていた」表現は残っておらず、「以前は
     `main_handler.py` にもあったが、二重持ちをやめて JavaScript 側
     だけに寄せた (TODO-078)」に書き直されている。

5. **`CLAUDE.md` の決まりからの逸脱**
   - `--datadir` を一時ディレクトリにして起動確認、`upgradeproject` は
     未実行、と報告に明記されており、決まりに沿っている。

## その他

- `math` の import 削除は妥当（`main_handler.py` に他の `math.` 呼び出しは無い）。
- `days2x_percent` / `calc_gauge_label` / `DAYS_YEAR` などへの参照は、
  `docs/design-review.md`（アーカイブ相当の文書）以外に残っていない。
- `ruff check` は該当ファイルすべて通った。
