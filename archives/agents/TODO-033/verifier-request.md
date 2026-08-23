# TODO-033 verifier への依頼

`WebServer.URL_PREFIX` → `DEF_URL_PREFIX` の追随漏れを直した。
**直ったかどうかを確かめてほしい。コードは直さないこと。**

**注意: この作業ツリーには TODO-027 の未コミットの変更も入っている。**
`git checkout` / `git restore` / `git stash` など、作業ツリーを戻す
コマンドは絶対に使わないこと。

## 読むもの

- `TODO.md` の `TODO-033` の節
- `archives/agents/TODO-033/implementer-request.md`
- `archives/agents/TODO-033/implementer-report.md`
- 変更そのものは `git diff`（**読むだけ**）

## 確かめてほしいこと

1. `uv run ruff format --check --line-length 78 src tests` /
   `uv run ruff check --extend-select I src tests` /
   `uv run basedpyright src tests` / `uv run mypy src tests` /
   `uv run pytest tests` を順に走らせ、**出力をそのまま報告する**。
   件数（何件通ったか）も書くこと
2. **`WebServer.URL_PREFIX` の参照が 1 つも残っていないか。**
   `git grep -n URL_PREFIX` で全部見て、残っているものが
   `DEF_URL_PREFIX` か、`tests/helpers.py` のモジュール変数
   `URL_PREFIX`（これは残してよい）かを仕分けする
3. **`src/README.md` の書き換えが、実物と合っているか。**
   `src/ytsched/webapp.py` と `src/ytsched/__main__.py` を読んで、
   既定値が `/ytsched` であること、`--url-prefix` で変えられることが
   README の記述と食い違っていないかを見る
4. **実装者が「TODO-033 の範囲外」として直さなかったもの**
   （`uv run ruff format --check` で `src/ytsched/__main__.py` だけが
   要整形。`2b4fcce` 由来）が本当に範囲外か。**あなたの見立てを書く**
5. **アプリが起動して動くか。** `--datadir` に一時ディレクトリを指定して
   起こし、既定の `/ytsched/` と、`--url-prefix` で別の値を指定した
   ときの両方に curl で当てて、200 が返ることを見る。終わったら止める

## 決まりごと

- **コードは直さない**
- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない。`--datadir` に必ず一時
  ディレクトリを指定する
- **アプリを起こすポートは 8892 を使う**（別の担当が同時に動いている）
- 報告は `archives/agents/TODO-033/verifier-report.md` に書く。
  返事は 5 行以内
