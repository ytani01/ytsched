# TODO-103 reviewer への依頼

TODO-103（月間ミニカレンダー）の変更を見る。**コードは直さない。**
見つけたことは報告するだけで、直すかどうかは main が決める。

先に読むもの:

- `archives/agents/TODO-103/implementer-request.md`（決めた設計）
- `archives/agents/TODO-103/implementer-report.md`（やったこと）
- `git diff`（`src/` と `tests/`）

## 見てほしいところ

- `SchedLoader.load_month_cal()` の境界（月初・月末の曜日、年またぎ、
  うるう年、`in_month` の判定）
- キャッシュ（`_month_cal_cache`）の持ち方。`SchedLoader` の寿命と
  合っているか、古い内容を返す道が無いか
- 予定の有無を `sdf_exists()` だけで見ていることの副作用
  （空のデータファイルが残っている日など）
- `main.html` のミニカレンダー部分。テンプレートで `datetime` を使って
  週の範囲を判定しているところ、`onmousedown` の付け方が既存の日付セル
  の流儀に合っているか
- CSS の詳細度・既存クラスとの干渉
- テストが実際に意味のあることを見ているか。抜けている境界は無いか
- 週パネルごとに 2 ヶ月分のテーブルが増える（既定で 18 個）ことの影響

## 報告

`archives/agents/TODO-103/reviewer-report.md` に書く。指摘は
「どこ・何が問題か・どうなると困るか」を、重いものから並べる。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内で。
