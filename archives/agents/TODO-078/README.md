# TODO-078 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 14,491 / cache_creation 254,091 / 概算 $8.1 |
|      | main 70% + implementer 22% + reviewer 4% + verifier 3%（料金の割合） |

## なぜこの分担にしたか

Python 側を消してブラウザ側へ寄せる項目で、**サーバのテストで見ていた
観点が消える**。ファイルも `main_handler.py`・`my.js`・`main.html`・
テスト 4 つにまたがるので、実装を分けた（implementer）。

見た目が変わりうる項目なので verifier に**変更前後の画面の突き合わせ**を
任せ、reviewer には「**消したテストの観点が本当に移っているか**」を
消す前のファイルと突き合わせて見てもらった。テストが通ることを見ても、
観点が減ったことは分からない。

## 報告

- [implementer-report.md](implementer-report.md) — 実装
- [verifier-report.md](verifier-report.md) — 不具合なし。変更前後の
  キャプチャが**完全に一致**（main が md5 でも確認した）
- [reviewer-report.md](reviewer-report.md) — 指摘なし。消した 10 本の
  観点がブラウザ側へ 1 対 1 で移っていること、期待値
  （`-1w`=46.21%）が変更前の式と合うことを手計算で確かめている

## 残したこと

verifier はスワイプとゲージのタップを実際には操作していない
（キーボードの週送りで代替した）。ゲージのタップは
`tests/test_browser.py::test_gauge_bar_click_moves_to_the_tapped_week`
が通っているので、そちらで見られている。

## 消費について

TODO-077 は同じ分担で $43.8 かかったが、この項目は $8.1 で済んだ。
差は項目の重さではなく、**main が担当の完了を待つ間にポーリングした
回数**（TODO-077 は main が 533 メッセージ、こちらは 49）。
担当の完了は通知で届くので、待つ間は何も叩かないこと。
