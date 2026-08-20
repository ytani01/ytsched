# TODO-009. README の更新

見込み: main = Sonnet 5 / effort low、担当 = writer + verifier
実施: main = Sonnet 5 / effort low、担当 = writer + verifier

## きっかけ

TODO-008 で `install.sh` / `Ytsched.src` を廃止し、`uv tool install` で
入る `ytsched` コマンドに一本化した。README の「Install」節は
「TBD」のままで、TODO-008 で決めた systemd --user のユニット例も
まだ README には転記していなかった。また「使用環境」節は
「言語: Python3」のままで、`pyproject.toml` の `requires-python =
">=3.14"` と合っていなかった。

「課題・問題点」節（検索機能の改良、期間・繰り返しスケジュール）は、
どちらも今も未解決なので**内容は変えないと決めた**（2026-08-20）。
文面（誤字・体裁）を整えるだけにした。

## やったこと

- 「使用環境」のサーバ言語を「Python3」から「Python 3.14 以上（uv で
  インストール）」に修正した。
- 「Install」節に、`archives/todo/TODO-008. uv tool install 方式へ.md`
  の内容を README の文体に合わせて書き直して追加した。
  - `git clone` → `uv tool install .` によるインストール手順、更新は
    `uv tool install --reinstall .` または `uv tool upgrade ytsched`
  - systemd --user のユニット例（`~/.config/systemd/user/ytsched.service`、
    `ExecStart=%h/.local/bin/ytsched webapp --datadir %h/ytsched/data
    --port 10085`）と、有効化・状態確認・ログ確認・停止のコマンド
  - ログインしていない間も動かし続けたい場合の
    `sudo loginctl enable-linger $USER`
- 「課題・問題点」は、誤字（「手書きき」→「手書きの手帳と」など）の
  訂正と句点の統一のみ行い、論点は変えていない。

## テスト

verifier が実装者（writer）の報告を自分の手元で再現し、問題は見つから
なかった（`archives/agents/TODO-009/verifier-report.md`）。

| 確認 | 結果 |
| --- | --- |
| `uv tool install .`（develop ブランチのリポジトリから） | 成功。`~/.local/bin/ytsched` が入る |
| `ytsched --help` / `ytsched webapp --help` | 正常表示。`--datadir` 既定値も README と整合 |
| `uv tool install --reinstall .` | 成功 |
| `ytsched webapp --datadir <一時dir> --port 12345` の起動 | `curl` で 200、例外・トレースバック無し |
| `systemd-analyze --user verify`（README のユニット例） | exit=0、警告・エラー無し |
| `ExecStart` の `%h/.local/bin/ytsched` と実際の `which ytsched` | 一致 |
| `requires-python = ">=3.14"` と README「使用環境」節 | 整合 |
| 「課題・問題点」の差分 | 誤字訂正・句点統一のみ、論点は不変 |

確認は一時ディレクトリ・一時ポートで行い、実データ
（`~/ytsched/data`）や実際の `systemctl --user enable` には触れて
いない。

分担の理由と各担当の報告は
[archives/agents/TODO-009/](../agents/TODO-009/) にある。
