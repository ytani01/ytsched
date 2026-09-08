# TODO-197 の分担

main が Codex 側の設定と入力変換を実装する。確認と実装を分けるため
verifier に動作検証、reviewer に入力変換と設定のレビューを依頼する。
Claude の設定・スクリプトは読み取りと呼び出しだけとする。

- verifier: JSON/TOML、コマンド保護の許可・拒否、一時ファイルの整形と除外
- reviewer: patch の追加・更新・移動・削除、対象範囲、Claude 未変更

報告はこのディレクトリの `verifier-report.md` と `reviewer-report.md`。
