# TODO-028 verifier の報告

依頼は implementer への依頼書（`archives/agents/TODO-028/implementer-request.md`）
と実装報告（同ディレクトリの `implementer-report.md`）、`TODO.md` の
「TODO-028」の節を読んだうえで確認した。

## mise run fmt / typecheck / lint / test

すべて `mise run upgradeproject` を走らせずに実行した。

- `mise run fmt` → `ruff format`: 21 files left unchanged / `ruff check`:
  All checks passed!
- `mise run typecheck` → `basedpyright`: 0 errors, 0 warnings, 0 notes /
  `mypy`: Success: no issues found in 18 source files
- `mise run lint`（fmt・typecheck を含む）→ 上と同じ、追加の指摘なし
- `mise run test` → `uv run pytest tests` **393 passed**（実装報告と一致）

いずれも○。

## テストが実際に効いているかの確認

実装報告に「わざと壊して確かめた」とある 2 件のうち、`sdf_exists()` を
常に `False` にする方を自分でも再現した（ソースは直さず、コード外から
`ytsched.ytsched.SchedData.sdf_exists` を monkeypatch して
`pytest.main()` を呼ぶ形）。

```
uv run python << 'EOF'
import ytsched.ytsched as ys
def fake(self, date=None):
    return False
ys.SchedData.sdf_exists = fake
import pytest
raise SystemExit(pytest.main(["tests/test_main_handler.py::TestLoadSchedScan", "-q"]))
EOF
```

結果: `TestLoadSchedScan` の 6 本中 **5 本が FAILED**（成功したのは
`test_search_mode_sched_is_same` の 1 本のみ）。実装報告の「5 本が落ちる」
と一致する。落ちなかった 1 本は「`sched` の中身が変わらない」ことだけを
見るテストで、`sdf_exists()` を常に `False` にしても `sched` の中身自体は
変わらない設計（`sdf = None` として空扱いで進む）なので、この 1 本が
通ること自体は不自然ではない。歯があることを確認できた。

`fix_todo_done()` の空白の件も、Python の対話実行で直接呼んで確認した
（下記）。ソースは変更していない。

```
fix_todo_done('2021-03-05', '', '', 'メモ') → detail = '〆2021/03/05\nメモ'
fix_todo_done('2021-03-05', '10:00', '', 'メモ') → detail = '〆2021/03/05 10:00\nメモ'
```

時刻が両方空のとき、末尾に余分な空白が付かないことを確認した（○）。

## アプリの起動確認

`--datadir` は一時ディレクトリ
（`/tmp/claude-649/.../scratchpad/todo028data`）を指定し、
`~/ytsched/data` には触れていない。

```
uv run ytsched webapp --datadir <一時dir> --port 18765
```

- `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18765/ytsched/`
  → **200**
- `filter_str=AB` を送る → `Conf.cgi` に `FilterStr\tab`
  （小文字で保存。○）
- 続けて `filter_str=`（空）を送る → `Conf.cgi` が `FilterStr`
  （値なしに書き換わり、絞り込みが解除される状態。○）
- サーバのログ（`server.log`）に例外・トレースバックは出ていない
- 終了後 `pgrep -f` で PID を確かめてから kill し、プロセスが残っていない
  ことを確認した

検索モードでファイルの無い日を実際にスキャンして結果が変わらないことは、
ブラウザ操作より上記のテスト再現（`TestLoadSchedScan` の
`test_search_mode_sched_is_same` が、`sdf_exists()` を壊した状態でも
唯一通り続ける）で代えて確認した。単体テスト自体（393 件中の該当分）も
通っている。

## 判断が要る点

特になし。依頼どおりの挙動を確認でき、不具合は見つからなかった。
