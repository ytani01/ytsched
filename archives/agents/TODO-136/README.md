# TODO-136 の分担

## 誰にどこを担当させたか

- **main**: 実装（`swipe.js`・`week.js`・`nav.js`）とブラウザテストの追加
  （`tests/test_browser.py`）、`mise run lint`・`uv run pytest tests`
  の実行
- **reviewer**: 実装済みのコードを読んでのレビュー（2 回）。1 回目で
  `moveActiveMonth()` の月境界の丸めに不具合を見つけ、main が直したので、
  2 回目で直った内容を再確認した
- **verifier**: 実際にアプリを起動し、ブラウザ（playwright）でミニ
  カレンダーの領域のスワイプ・ドラッグを実際に動かして確認

## その分担にした理由

TODO-136 は、既存の週送りのスワイプ・ドラッグ（`swipeDragTo()`/
`swipeFinish()`）に分岐を足す変更で、挙動・分岐が変わる項目に当たる
（`CLAUDE.md` の基準）。既存の週送り・検索モードのスワイプを壊さないか
判断が要るため、実装とは別に reviewer を立てた。verifier は通常どおり、
コードは直さず実機での動作確認に専念させた。

## 各担当の報告ファイル

- [reviewer-report.md](reviewer-report.md)（1 回目の指摘を含めて、2 回目の
  確認結果で上書き済み。1 回目の指摘の詳細は、このファイルの本文と
  `archives/todo/TODO-136. …md` の「やったこと」に残してある）
- [verifier-report.md](verifier-report.md)
