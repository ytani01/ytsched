# TODO-111 wording 報告

## 前例の無い語

| 語 | 出てくる箇所 | HEAD の前例 | 見立て |
|---|---|---:|---|
| `header_date` | `src/README.md`: 週移動の図、TODO archive: 20 行目、reviewer 報告: 14・29・33 行目 | 0 件 | 今回追加した HTML 要素の ID。一般語ではないが、実装上必要な識別子である。 |
| `footer_date` | `src/README.md`: 週移動の図、TODO archive: 20・25 行目、reviewer 報告: 14・29・33 行目 | 0 件 | 今回追加した HTML 要素の ID。一般語ではないが、実装上必要な識別子である。 |
| `week_move_updates_date_inputs` | verifier 報告: 17 行目 | 0 件 | 今回追加した pytest のテスト名で、内容をそのまま表している。 |
| `week_move_does_not_reload_the_page` | verifier 報告: 17 行目 | 0 件 | 既存テストの識別子。一般語ではないが、実行コマンドに必要である。 |
| `long_search_result_loads_without_javascript_error` | reviewer 報告: 19 行目、verifier 報告: 17 行目 | 0 件 | 今回追加した pytest のテスト名で、内容をそのまま表している。 |
| 「対象ブラウザテスト」 | TODO archive: 32 行目、README: 4 行目、verifier 報告: 5 行目 | 0 件 | 対象を限定する普通の言い方で、造語には見えない。 |
| 「長い検索結果」 | TODO archive: 26 行目 | 0 件 | 普通の説明で、造語には見えない。 |
| 「タイミング競合」 | TODO archive: 37 行目 | 0 件 | 意味は推測できるが、一般には「タイミングに依存する不安定なテスト」や「競合状態」などとも書く。今回の現象を正確に表すかは main の判断が要る。 |
| 「再レビュー」 | TODO archive: 38 行目、reviewer 報告: 1 行目 | 0 件 | 一般に通用する言い方で、造語には見えない。 |
| 「日付参照」 | TODO archive: 24 行目 | 0 件 | 「日付を参照する箇所」を短くした表現。意味は通るが、圧縮した言い方ではある。 |
| 「両入力欄」 | reviewer 報告: 35 行目 | 0 件 | 「両方の日付入力欄」を短くした普通の表現で、造語には見えない。 |
| 「ID 分離」 | reviewer 報告: 39 行目 | 0 件 | 「ID の分離」を短くした表現。意味は通るが、文中では助詞を補うほうが自然にも見える。 |
| 「参照と同期」 | reviewer 報告: 39 行目 | 0 件 | 二つの変更内容をまとめた普通の表現で、造語には見えない。 |
| 「レビュー対象外」 | reviewer 報告: 42 行目 | 0 件 | 一般的な開発上の表現で、造語には見えない。 |
| `deselected` | verifier 報告: 5 行目 | 0 件 | pytest の標準出力に使われる用語で、そのままで問題ない。 |
| 「全 pytest」 | verifier 報告: 11・21 行目 | 0 件 | pytest 全件の実行を指す短い表現。意味は通るが、「pytest 全件」などとも書ける。 |
| 「週への遷移」 | verifier 報告: 26 行目 | 0 件 | 一般的な UI の説明で、造語には見えない。 |
| 「全体確認」 | verifier 報告: 31 行目 | 0 件 | 全テストによる確認をまとめた普通の言い方で、造語には見えない。 |

## 読んだファイル

- `TODO.md`
- `src/README.md`
- `archives/todo/TODO-111. フッターの日付が週切り替えに連動しないのを直す.md`
- `archives/agents/TODO-111/README.md`
- `archives/agents/TODO-111/reviewer-report.md`
- `archives/agents/TODO-111/verifier-report.md`
- `archives/agents/TODO-111/wording-report.md`

前例の無い語は 18 語。報告書で新たに使った呼び名には、上記以外の前例なしは
見つからなかった。
