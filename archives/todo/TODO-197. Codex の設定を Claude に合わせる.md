# TODO-197. Codex の設定を Claude に合わせる

| | main | 担当 |
| --- | --- | --- |
| 見込み | GPT-6 Astra / effort は実行環境から確認できず | main + verifier + reviewer |
| 実施 | GPT-6 Astra / effort は実行環境から確認できず | main + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
| --- | --- | --- | --- | --- | --- |
| main | GPT-6 Astra | 実行値は未確認 | 未測定 | 未測定 | 未測定 |
| verifier | GPT-5.6 Luna | medium | 未測定 | 未測定 | 未測定 |
| reviewer | GPT-5.6 Sol | high | 未測定 | 未測定 | 未測定 |

Codex の担当起動時のモデル・effort を記録した。Claude の集計スクリプトは
Claude のログを対象とするため、Codex の実績には使わない。
変更後の既定 effort `medium` は、実行中の main の値を示すものではない。

## きっかけ

利用者から Claude の設定に合わせ、Claude の設定ファイルは書き換えない
との依頼。Codex は既に Claude の指示・担当定義を読む構成だったが、
フックと実際に読み込む担当設定が不足していた。

## やったこと

- `~/.codex/AGENTS.md` に共通の Claude 指示を読む指定を追加した。
- `~/.codex/config.toml` の思考量を `low` から `medium` にした。
- `~/.codex/hooks.json` に共通のコマンド保護と CodeGraph の prompt hook を
  追加した。セッション開始フックは既存設定を残した。
- `.codex/hooks.json` に ytsched 固有のコマンド保護と編集後の整形を設定した。
  Claude のスクリプトは変更せず呼び出し、Codex の patch から各対象パスを
  渡す処理だけを `.codex/hooks/fmt-patch.py` に追加した。
- `.codex/agents/` に6担当を登録した。グローバル定義に無かった
  `runner`・`writer` を加え、文章作成になっていた `wording` を初出語確認に
  合わせた。各担当の手順は既存の Claude 定義を読む。
- Claude 固有のモデル名・UI・プラグインは移植しない。Codex の既存の
  ローカルコマンド承認設定も維持した。

ユーザー全体の3ファイルはリポジトリ外で、このコミットには含まれない。
今回 Claude 側への編集は行っていない。リポジトリの Claude ファイルの
差分は無く、ユーザー全体側の既存差分はレビュー報告に区別して記録した。

## テスト

- JSON/TOML の読み込み、6担当の名前と参照先を確認した。
- 共通・ytsched 固有のガードへコマンド文字列を渡し、許可と拒否を確認した。
  危険なコマンド自体は実行していない。
- 未整形の一時 Python・JavaScript を実際に整形し、終了コード 0。
  `py_compile` と `node --check` も終了コード 0。
- 複数ファイル、移動先、削除、Claude・archives・プロジェクト外の除外を確認した。
- Ruff の整形確認・lint、`git diff --check` が通った。
- reviewer の指摘は無し。

フックの信頼登録と Codex 本体からの起動、新セッションでの6担当反映は
未確認。利用者が `/hooks` で追加・変更した定義を確認して信頼する必要がある。
手順と仕様の参照先は [.codex/README.md](../../.codex/README.md) にある。

## 分担の振り返り

- verifier はガードの許可・拒否、入力変換、実際の整形を確認した。
  初回は既存の整形済みファイルを使用していたため、main が未整形の
  一時ファイルによる再確認を依頼した。既存ソースに差分は残っていない。
- reviewer は入力変換・対象範囲・設定を確認し、指摘は無かった。
- 担当編成は見込みどおり。調査中に実際の担当登録の不足を見つけ、
  6担当の設定確認を追加した。
- 次回も実装・検証・レビューを分け、整形の検証では最初から未整形の
  一時ファイルと期待値を指定する。

詳細: [分担と報告](../agents/TODO-197/README.md)
