# TODO-036 verifier への依頼

TODO-036（`click_utils.py` の導入）の実装が上がった。**実際に動くかを、
実装者の報告を鵜呑みにせず自分で確かめてほしい。**

対象の変更（すべて未コミット）:

- `src/ytsched/click_utils.py`（新規）
- `src/ytsched/__main__.py`
- `src/ytsched/webapp.py`

背景は `TODO.md` の「TODO-036」の節と
`archives/agents/TODO-036/implementer-request.md` にある。
実装者の報告は `archives/agents/TODO-036/implementer-report.md`。

## 確かめること

**`--datadir` には必ず `mktemp -d` の一時ディレクトリを指定する**
（`~/ytsched/data` の実データを汚さないため）。

### 1. 決まった手順

`mise run fmt` → `mise run lint` → `mise run typecheck` → `mise run test`。
（`mise run upgradeproject` は**走らせない**）

### 2. CLI が実際に動くか

- `uv run ytsched --version` / `-V` / `-v` → 3 つともバージョンを出して終了するか
- `uv run ytsched --help` / `-h` / 引数なし → ヘルプが出るか
- `uv run ytsched webapp --help` / `migrate --help` / `x-data1 --help`
  → 3 つとも `-V, -v, --version` / `-d, --debug` / `-h, --help` が並ぶか
- `uv run ytsched webapp -V` → バージョンを出して終了するか
  （**サーバが起動してしまわないこと**）

### 3. `--debug` の合成（今回いちばん見てほしいところ）

グループ側の `--debug` をサブコマンドへ引き継ぐようにした。次の 4 通りで
DEBUG ログの出方を実際に見る:

- `ytsched --debug migrate --dry-run --datadir <tmp>` → **出る**
- `ytsched migrate -d --dry-run --datadir <tmp>` → 出る
- `ytsched --debug migrate -d --dry-run --datadir <tmp>` → 出る
- `ytsched migrate --dry-run --datadir <tmp>` → **出ない**

`webapp` でも同じ 4 通りを見て、`--debug` が `WebServer` まで届いているか
（tornado の `autoreload` / `debug` 設定）を確かめる。

### 4. webapp が起動して応答するか

`uv run ytsched webapp --datadir <tmp> --port <空きポート>` を起動し、
`curl` で 200 が返るか。ページに版が描画されているか（`WebServer` の
`version` 引数を消したので、テンプレート側が壊れていないかを見る）。

### 5. 文書に書かれた手順

`README.md` と `docs/Developer.md` に載っている `ytsched` のコマンド例が
そのまま通るか。通らないものがあれば、どれがどう通らないかを報告する。

## やらないこと

- **コードは直さない。** 見つけたことは報告するだけ。
- 直し方の提案は書いてよいが、実際に手を入れないこと。

## 報告

`archives/agents/TODO-036/verifier-report.md` に書く。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
