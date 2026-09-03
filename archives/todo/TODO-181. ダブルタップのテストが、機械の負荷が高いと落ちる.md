# TODO-181. ダブルタップのテストが、機械の負荷が高いと落ちる

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Sonnet 5 / effort medium | main + verifier |
| 消費 | output 23,588 / cache_creation 93,905 / 概算 $0.9 |
|      | main 87% + verifier 13%（料金の割合） |

分担の理由と報告は [archives/agents/TODO-181/](../agents/TODO-181/README.md)。

## きっかけ

TODO-180 の確認でフルスイートを走らせると、毎回 2 件ほど落ちた。落ちる
顔ぶれは実行のたびに変わり、単独で走らせるとどれも通る。TODO-180 の
ときは裏で別の作業が動いていた。ゲージの変更とは関係が無い。

落ちるのは `tests/test_browser.py` の `_double_tap_home_in_search()` の

```
assert elapsed < interval_msec  # 1 回目の読み直しに 674 ミリ秒かかり、
                                # 600 ミリ秒後の 2 回目を置けない
```

で、検索画面の読み直し（この開発機で 180〜360 ミリ秒の想定）が、機械が
混んでいると 500〜600 ミリ秒を超える。

`interval_msec` を渡すダブルタップのテスト
（`test_home_button_double_tap_by_touch_returns_to_the_top_screen[500]` /
`[600]` ほか）は、読み直しが終わってから 1 回目の `interval_msec` ミリ秒後に
2 回目を置く。読み直しがその窓に間に合わないと、2 回目を狙って置けない。

## 決めたこと

**混雑時だけ、実測した時間を理由に付けて skip する。** 以前は落として
いた。選択肢は「そのままにする」「間隔を実測から決める」「落ちたときだけ
測り直す」の 3 つで、利用者が skip 方式（「そのままにする」の変種）を選んだ。

- 記憶やメモではなく、テスト自身に判定させる。他機で走らせても効くし、
  赤い失敗を見た人が毎回 TODO を辿らずに済む
- 通常（読み直しが `interval_msec` 未満）はこれまでどおり `wait_for_timeout`
  で 2 回目を置き、ダブルタップの間隔をそのまま検証する
- 混雑時は skipped 件数と理由（`-rs`）に出る。無条件の
  `@pytest.mark.skip`（黙って消える）とは別物

### 残る懸念（TODO-165 の reviewer 指摘 3）

TODO-165 で skip にしなかったのは、「読み直しが遅くて 2 回目が窓に
入らない」という、TODO-164 が直そうとした失敗そのものを緑にしてしまう、
という指摘があったから。今回の条件付き skip でも、検索画面の読み直しが
**恒常的に**遅くなるリグレッションが起きたときは、fail ではなく skip で
見逃す余地が残る。緩和は「無条件の silent skip ではなく、理由付きで
skipped 件数に出す」ところまで。恒常的に skip が出るようになったら、
読み直しの速度自体を疑うこと。

## やったこと

- `_double_tap_home_in_search()` の
  `assert elapsed < interval_msec, ...` を
  `if elapsed >= interval_msec: pytest.skip("機械が混雑: …")` に変えた。
  理由の文言に実測した `elapsed` と `interval_msec` を入れる
- docstring の「読み直しが間に合わないときは skip せずに落とす」を、
  条件付き skip の説明に書き直した

## テスト

verifier が担当（[報告](../agents/TODO-181/verifier-report.md)）。

- `mise run lint` 通過（ruff format / ruff check / eslint /
  basedpyright 0 errors / mypy 40 files）
- `uv run pytest tests/test_browser.py -k "double_tap or home_button" -rs`
  を 3 回。いずれも 13 passed / 0 skipped / 0 failed。
  `_double_tap_home_in_search` 由来の AssertionError は出ない。
  この開発機は今回空いていたので skipped は 0 件（想定どおり）
- skip の分岐をスクラッチで確認（リポジトリのファイルは変更せず、
  `_double_tap_home_in_search` を import してスタブで呼ぶ）。
  `interval_msec=10` で `pytest.skip` 由来の `Skipped` が送出され、
  理由が「機械が混雑:」で始まり、2 回目の `tap` は呼ばれない。
  `interval_msec=100000` では skip されず最後まで進み `tap` が 2 回
- 呼び出し側と `interval_msec is None` の経路は変更なし
