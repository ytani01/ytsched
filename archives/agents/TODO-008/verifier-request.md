# TODO-008 verifier への依頼

## 背景

`ytsched` を `uv tool install` 方式へ移す作業（TODO-008）を implementer が
終えた。実装は行っていない作業（コミットもしていない）ので、まだ
`git status` に変更が残っている。

実装の内容は `archives/agents/TODO-008/implementer-report.md` に書いて
ある。読んでから始めること。

## 確かめてほしいこと

### 1. `install.sh` / `Ytsched.src` の削除

`git status` で両ファイルが削除（`D`）としてステージされていることを
確認する。

### 2. `uv tool install` が実際に動くこと

以下を自分の手元で実行し、結果を確認する。**`--datadir` には必ず
一時ディレクトリを使うこと（`~/ytsched/data` は本物のデータなので
触らない）。**

```sh
cd /home/ytani/work/ytsched
uv tool install --reinstall .
which ytsched
ytsched --help
ytsched webapp --help
```

そのうえで、一時ディレクトリを datadir にして webapp を起動し、
HTTP で応答することを確認する。

```sh
TMPD=$(mktemp -d)
ytsched webapp --datadir "$TMPD" -p <空いているポート> &
sleep 1
curl -s -o /dev/null -w "code=%{http_code}\n" http://localhost:<ポート>/ytsched/
# 確認できたらプロセスを止める（kill）
```

`--webroot` の既定値が `uv tool install` のインストール先
（パッケージ同梱の `webroot/`）を指しており、正しく静的ファイル・
テンプレートが見つかっていることも確認する（`curl` が 200 を返せば
基本的に webroot も解決できている）。

### 3. systemd --user のユニット例の検証

`implementer-report.md` の「5. systemd --user のユニット例」に書かれた
ユニットファイルの内容を、一時ファイルに書き出して
`systemd-analyze --user verify <一時ファイル>` に通し、警告・エラーが
無いことを確認する。

**実際に `systemctl --user enable --now` はしないこと。**
ユーザーの systemd --user 環境に恒常的な変更を加えることになるため、
構文検証（`systemd-analyze --user verify`）だけにとどめる。

`ExecStart` のパス（`%h/.local/bin/ytsched`）が、2 で確認した
`which ytsched` の実際のパスと整合しているかも確認する。

## 報告してほしいこと

`archives/agents/TODO-008/verifier-report.md` に書くこと:

- 1〜3 それぞれの実行結果（コマンドと出力）
- 問題が見つかった場合はその内容（**直さず報告だけ**でよい）
- 全体として TODO-008 の 3 つのチェック項目
  （`install.sh`/`Ytsched.src` の廃止、`uv tool install` の手順確認、
  systemd ユニット例）が実際に機能しているかの結論

コードは直さないこと。返事は「終わったか・報告ファイルのパス・
判断が要る点」だけを 5 行以内で。
