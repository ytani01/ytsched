# TODO-058 reviewer 報告

依頼書・implementer-report・request-implementer・`TODO.md` の TODO-058 節を
読んだうえで、`git diff` を確認した。

## 見た観点ごとの結果

1. **`days2x_percent()` と `days2xPercent()` の一致。**
   `dd = 0.6`、`DAYS_GAGE_MAX = DAYS_YEAR * 30`、`50.0 * log10(...) /
   log10(DAYS_GAGE_MAX + dd)`、`min(x, 50.0)` での頭打ち、符号の付け方が
   Python・JavaScript で完全に同じ。どちらも `round()` を使っていない点も
   揃っている（旧 `days2y_offset` は `round()` していたが、新しい方は
   両言語とも丸めていない）。一致している

2. **検索モードで `gage_r` が存在しない経路。**
   `dispGage()` の先頭に `if (!elGageR0) return;` があり、`setGagePosition()`
   や `placeGageWithoutTransition()` は `dispGage()` 経由でしか呼ばれない
   （grep で確認）ので、`null` を触る経路は無い

3. **`sessionStorage` による補間（TODO-049）。**
   `placeGageWithoutTransition()` → `setGagePosition()` → 今回追加した
   `elGageR0.style.left` という流れがそのまま保たれていて、対象が
   `bottom` から `left` に変わっただけ。`.my-gage-r-no-transition` は
   クラス 1 つのままで、`.my-gage-r`（クラス 1 つ）とソース順で競合しない
   よう、CSS 側でも後ろに置かれている（TODO-049 のコメントも残っている）

4. **消し残し／消しすぎ。**
   `days2y_offset` / `days2yOffset` / `y_offset` / `gage_r_base` /
   `elGageRBase` / `my-osd-base` / `my-gage-text` / `centerY` は
   `src/` `tests/` `docs/` 全体を grep してヒット無し。逆に、
   `elGageR0 = document.getElementById("gage_r")` と `dispGage(...)` の
   呼び出しは依頼書どおり残っている。`GAGE` は `main_handler.py` の
   359 行目でテンプレートへ渡され続けている（配線を切っていない）

5. **`padding-left:22px` を消したことの影響。**
   他に `#main` へこの値を足す CSS が無いことを確認した。縦ゲージ用の
   余白だったので影響は無いはず

6. **コメント。** いずれも TODO-058 の参照と「なぜ」（頭打ちの理由、
   両端の 12px の余白の理由、`.my-gage-r-no-transition` の詳細度の理由）
   を書いていて、このリポジトリの書き方に合っている

## 気になったが確信度が低いもの

- `main_handler.py` の `GAGE` は `days2x_percent()` を呼ぶ前に
  `DAYS_GAGE_MAX` が定義されている必要があるが、これは関数呼び出し時点
  （モジュール読み込み時に `GAGE` を組み立てる行）での評価であり、
  `DAYS_GAGE_MAX` の代入は `GAGE` より前にあるので問題は無い。
  念のため確認しただけで、指摘ではない
- `.my-gage-bar { margin: 0 12px; }` と `#week_bar` 側の
  `.container-fluid`（`padding: 0 .75rem` 相当）が両方効いて、実際の
  余白がどう重なるかは目で見ないと分からない。実装者はキャプチャで
  確認済みと報告しており、見た目の微調整の域を出ないと判断し、
  指摘にはしなかった

## 総評

正しさ・設計・プロジェクトの決まりからの逸脱について、確信度の高い
問題は見つからなかった。
