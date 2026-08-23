# TODO-032 verifier への依頼

`Conf.cgi`（タブ区切り）を `conf.json`（JSON）にする変更が、作業ツリーに
入っている（未コミット）。**実際に動くかを確かめてほしい。**

実装の依頼書は `implementer-request.md`。決まっていることは `TODO.md` の
TODO-032 の節にある。

**実装者はセッションの上限で途中終了した**（「アプリを起動して確かめる」
直前）。lint・型チェック・テストは main が走らせて通ることを確認済み
（`uv run ruff format --line-length 78 --check src tests tools` /
`ruff check .` / `basedpyright` / `mypy` / `pytest` = 411 passed）。
**同じものをもう一度走らせるだけで終えないこと。** 主眼は、テストでは
見ていない実際の動作。

## 確かめてほしいこと

1. **移行ツールが実データの形で動くか。** 一時ディレクトリに旧形式の
   `Conf.cgi`（タブ区切り。euc_jp の値を含むもの）と、予定の `.cgi` を
   何本か置いて `uv run ytsched migrate --datadir <一時ディレクトリ>` を
   走らせる。`conf.json` の中身、元の `Conf.cgi` が残ること、出力の
   「設定ファイル」の行、`--dry-run` で書かれないことを見る。
   `tests/data/old_format/` をコピーして使ってよい。
2. **移行したあと、アプリが設定を読むか。** `uv run ytsched webapp`
   （オプションは `--help` で確認）を一時ディレクトリに対して起動し、
   `curl` で画面を取る。移行した `ToDo_Days` などが効いているか。
   **`--datadir` には必ず一時ディレクトリを渡すこと**（`~/ytsched/data`
   を汚さない）。
3. **画面から設定を変えると `conf.json` が更新されるか。**
   `filter_str` や `search_n` を渡して、ファイルの中身が JSON のまま
   書き換わることを見る。
4. **壊れた `conf.json` でも画面が出るか。** わざと壊した JSON、
   トップレベルが配列の JSON、値が数値の JSON を置いて、500 にならず
   画面が出ること（警告は出てよい）。
5. **旧 `Conf.cgi` が残っていても読みに行かないこと**（後方互換は
   残さないと決めている）。

## やらないこと

- **コードは直さない。** 見つけたことは報告するだけ。直すかどうかは
  main が決める。
- `mise run upgradeproject` は走らせない。

## 報告

`archives/agents/TODO-032/verifier-report.md` に書く。返事は
「終わったか・報告のパス・判断が要る点」の 5 行以内。
