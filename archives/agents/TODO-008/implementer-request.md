# TODO-008 implementer への依頼

## 背景

`ytsched` を `uv tool install` で使う方式へ移行する。以前（2021 年）の
`install.sh` / `Ytsched.src`（venv を手動で作って `~/bin/Ytsched` を
生成する仕組み）はもう使わない。

すでに確認済みのこと（調査済みなので再確認不要）:

- `pyproject.toml` に `[project.scripts] ytsched = "ytsched.__main__:cli"`
  があり、`uv tool install` で `ytsched` コマンドが入る状態になっている。
- `src/ytsched/webapp.py` の `WebServer.DEF_WEBROOT` は
  `os.path.dirname(os.path.abspath(__file__))` を基準にパッケージ同梱の
  `webroot/` を指すようすでに実装されている（インストール先に依らず動く）。
- `WebServer.DEF_DATADIR` は `~/ytsched/data` を指す（TODO-008 で
  「データディレクトリは変えない」と決めた内容と一致）。

## やってほしいこと

### 1. `install.sh` と `Ytsched.src` の削除

リポジトリ直下の `install.sh` と `Ytsched.src` を `git rm` で削除する。
（`~/bin/Ytsched` という起動スクリプト方式は廃止すると決めている。
`uv tool install` で入る `ytsched webapp --datadir ~/ytsched/data` を
直接使う方式に変える。）

他に `install.sh` / `Ytsched.src` を参照している箇所がないか
（README、CLAUDE.md、CI 設定など）を `grep -rn` で確認し、あれば
一覧にして報告してほしい（README の書き換え自体は TODO-009 の担当なので
書き換えなくてよい。参照箇所の洗い出しだけでよい）。

### 2. systemd --user のユニット例の文面を作る

`~/ytsched/data` を使う前提で、`uv tool install` 後の `ytsched` を
`systemd --user` で常駐させるユニットファイルの例を **テキストとして**
作成する。**リポジトリにユニットファイルの実体は置かない**（ポートや
datadir が環境ごとに違うため、という理由がすでに TODO-008 に書かれている）。

作成した文面は、リポジトリに置かず、この依頼への回答ファイル
（後述の報告ファイル）にそのまま書いてほしい。README への転記は
別の項目（TODO-009）でやる。

ユニット例に含めてほしい要素:

- `[Unit]` / `[Service]` / `[Install]` の一般的な構成
- `ExecStart` は `uv tool install` でインストールされた `ytsched` の
  絶対パス（`~/.local/bin/ytsched` を想定。`uv tool install` の実際の
  インストール先を手順確認の中で確かめて、そのパスを使うこと）
  を使い、`webapp --datadir %h/ytsched/data` を渡す形にする
- `WantedBy=default.target`
- 実行例のコマンド（`systemctl --user enable --now ytsched.service` など）
  も添えること

### 3. `uv tool install` の手順を自分の手元で試す

以下を実際に実行して、動くところまで確認してほしい（コマンドと結果を
報告ファイルに残すこと）。

```
cd <このリポジトリのルート>
uv tool install .
which ytsched   # インストール先のパスを確認する（上のユニット例に使う）
ytsched --help
ytsched webapp --help
```

`ytsched webapp` を実際に起動して HTTP で応答することの確認は
verifier に任せてよい（ここでは `--help` 系の確認と、コマンドが
一通り通ることの確認だけでよい）。

## 報告してほしいこと

`archives/agents/TODO-008/implementer-report.md` に書くこと:

- `install.sh` / `Ytsched.src` を削除したこと（`git rm` の結果）
- 他に参照している箇所があったかどうか（あれば一覧）
- `uv tool install .` を実行した結果（`which ytsched` の出力を含む）
- systemd --user のユニット例（そのままファイルに書く）
- 判断に迷った点があれば書く

返事は「終わったか・報告ファイルのパス・判断が要る点」だけを 5 行以内で。
