# TODO-056 verifier 報告

## 1. 素の状態で通ること

```sh
mise run test
```

○ 442 件すべて通過（`tests/test_browser.py` の 3 件を含む）。fmt / typecheck
（basedpyright・mypy）も 0 件で通った。

## 2. 退行をわざと戻したときに落ちること

### TODO-049（`scrollToId()` のブロックの順番）

`el == null` を見るブロックと `body_h <= win_h` を見るブロックを
入れ替えて `uv run pytest tests/test_browser.py -v` を実行。

○ `test_home_button_moves_the_view` が
`playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout
10000ms exceeded.`（`#date-2026-08-26` が visible にならない）で落ちた。
他の 2 件は通過。確認後 `\cp` で退避しておいた元ファイルへ戻し、
`git diff` が空であることを確認した。

### TODO-063（`moveToMonday()` の月曜の求め方）

`const days = (1 - wday) + (direction > 0 ? 7 : -7);` を
`c01013e^` の形（`direction > 0` なら `8 - wday`、それ以外は
`1 - wday`、0 のとき `-7`）へ戻して同じく実行。

○ `test_back_button_moves_a_week` が
`playwright._impl._errors.TimeoutError: Timeout 10000ms exceeded.`
（`navigated to ".../?date=2026-08-24&sde_align=top"` のまま、期待する
前の週の月曜へ進まない）で落ちた。`test_forward_button_moves_a_week` は
通過（依頼どおり、退行の対象は「前」のみ）。確認後 `git checkout --` で
元へ戻し、`git status --short` で差分が無いことを確認した。

戻したあとに `uv run pytest tests/test_browser.py -v` を再実行し、
3 件とも PASS することを確認した。

## 3. 走らせ方が文書どおりに再現できること

○ `docs/Developer.md`・`tests/README.md` の記述どおりに
`mise run test`、`uv run pytest tests/test_browser.py -v` で再現できた。
`/usr/bin/chromium` が存在し、3 件とも skip されず実行された。

## 4. 気になった点

- 実データ: `server` fixture は `tmp_path / "data"` のみ使っており、
  `~/ytsched/data` への読み書きは無し（コード上も実行結果からも確認）。
- 不安定になりそうな箇所: 見当たらず。`_free_port()` で port を毎回
  取り直しており、`BOOT_TIMEOUT`（20 秒）・`wait_for_selector` /
  `wait_for_url`（10 秒）の待ちも妥当に見える。3 回連続で走らせても
  安定して通った。
- `server` fixture 内 `except urllib.error.URLError, TimeoutError,
  ConnectionError:` は一見 Python 2 の構文に見えるが、`except` の後ろは
  括弧なしタプルとして評価されるため Python 3 でも有効で、3 つとも
  正しく捕まえる（`except ValueError, TypeError:` で実際に検証済み）。
  実害は無いが、`except (A, B, C):` と書いたほうが読み手に誤解を
  与えない、という程度の所感（判断は main に委ねる）。

## まとめ

TODO-049・TODO-063 どちらの退行も、狙ったテストが確実に落ちることを
確認した。コードは変更していない（すべて確認後に復元・差分無しを確認済み）。
