# TODO-137 の分担

## 誰にどこを担当させたか

- **main**: 仕様の確認（利用者への 6 点の質問）、設計の指定
  （[implementer-request.md](implementer-request.md)）、報告の確認、
  文書と archives の仕上げ、コミット
- **implementer**: 設計どおりの実装。Python（`main_binder.py` /
  `main_view.py` / `sched_load.py`）・テンプレート（`month.html` /
  `mini_cal.html` の新規と `main.html` の分岐）・JavaScript
  （`month.js` の新規と既存 5 か所の分岐）・CSS・テスト・文書
- **verifier**: `mise run lint` と `uv run pytest tests` の確認、
  一時ディレクトリで起動したアプリを playwright で実際に操作しての
  動作確認（週間 ⇄ 月間の往復、6 ヶ月移動の先読み、既存機能の
  リグレッション）
- **reviewer**: 実装済みのコードを読んでのレビュー

## その分担にした理由

Python・テンプレート・JavaScript・CSS・テスト・文書にまたがる項目で、
実装がひとまとまりで要るため、実装を別の担当に分けた
（`~/.claude/CLAUDE.md` の「複数のファイルにまたがる、実装とテストと
文書がまとまって要る」）。

表示モードという**新しい分岐が増える**変更なので、reviewer も入れた
（「挙動や分岐が変わる項目には入れる」）。既存の週送り・検索モード・
ミニカレンダーのスワイプ（TODO-136）・自動ページ送り（TODO-084）を
壊していないかの判断が要るため。

verifier は、実際に**試せる手順がある**（ブラウザで操作できる）ので
通常どおり立てた。verifier と reviewer は見るものが重ならないので
同時に走らせた。

## 各担当の依頼・報告ファイル

- [implementer-request.md](implementer-request.md)（main が書いた設計の指定）
- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)
