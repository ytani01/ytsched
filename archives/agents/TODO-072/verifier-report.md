# TODO-072 verifier 報告

## 1. lint / pytest / ブラウザテスト

- `mise run lint` → fmt/ruff check/basedpyright/mypy すべて通過
  （26 files left unchanged / All checks passed / 0 errors / no issues）
- `uv run pytest tests -q` → 455 passed
- `uv run pytest tests/test_browser.py -q` → 9 passed
  （`test_gage_label_moves_with_the_needle` を含めすべて通過）

## 2. サーバ側と JavaScript 側の出力の一致

`calc_gage_label()`（Python）と `gageDiffLabel()`（JS, Node で実行）を
2024-01-01（月曜）基準に、-1600〜+1600 週（3201 通り、-30y〜+30y 相当）で
突き合わせた。**差分 0 件、全一致。**

```
node .../gage_label.js > js_out.tsv
uv run python -c '(略) calc_gage_label(...)' > py_out.tsv
diff py_out.tsv js_out.tsv   # → 0 行
```

## 3. 境界値

すべて仕様どおり。

- 28 日 (4w) → `+4w`
- 35 日 (5w) → `+1.1m`
- 364 日 (52w) → `+12.0m`
- 371 日 (53w) → `+1.0y`
- ±196〜±203 日付近も月表示で連続（`-6.7m`〜`+6.7m` 等）

## 4. 実アプリでの確認

`--datadir` に一時ディレクトリを指定して起動（port 18099）。

- `GET /` → 200、`gage_r_label` は `±0`
- `GET /?date=<+400日>` → `+1.1y`（テンプレート展開済み、`{{ }}` 残存なし）
- `GET /?date=<+40日>` → `+1.4m`
- サーバログに例外・トレースバックなし
- 確認後プロセスを kill 済み

## 5. `calc_week_diff` の残存参照

`grep -rn "calc_week_diff"` → ヒットなし。消し忘れなし。

## 判断が要る点

なし。指摘事項もなし。
