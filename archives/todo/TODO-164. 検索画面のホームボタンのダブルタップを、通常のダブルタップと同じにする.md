# TODO-164. 検索画面のホームボタンのダブルタップを、通常のダブルタップと同じにする

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier + reviewer |
| 実施 | Sonnet 5 / effort medium | main + verifier + reviewer |
| 消費 | output 56,433 / cache_creation 167,052 / 概算 $3.8 |
|      | main 89% + verifier 6% + reviewer 5%（料金の割合） |

## きっかけ

検索画面でホームボタンをダブルタップしても、通常表示のダブルタップと
同じ「強制的に読み直す」動作にならない、という報告があった。

調べると、検索画面ではホームボタンのシングルタップ自体が毎回ページの
読み直しを伴っていた（検索結果は日付範囲が限られていて、通常表示の
ように前後の週を先読みしていないため、画面内スクロールだけでは
目的の日に届かない）。今までは1回目のタップで即座に読み直しが始まる
ため、`homeButtonHdr()`（`main-page.js`）の `clickCount`（メモリ上の
値）がページの読み直しで消えてしまい、2回目のタップが来てもダブル
タップと判定できていなかった。実際には「シングルタップの読み直し」が
2回起きるだけで、通常表示の「ダブルタップで `sde_align=top` を付けて
強制的に読み直す」という分岐には実質到達できていなかった。

直し方は利用者と相談して2案を検討した。

- **sessionStorage 案。** TODO-123（フッターの ◀▶ ボタン）が使っている、
  直前のタップ時刻をページの読み直しをまたいで持ち越す仕組みを使う。
  シングルタップの反応速度は変わらない
- **遅延判定案（採用）。** 週間表示のホームボタンと同じように、1回目の
  タップでは即座に読み直さず、350ミリ秒待って2回目が来なければ
  シングルタップの動作をする。`clickCount` をメモリで持つだけで済み、
  sessionStorage は要らない。シングルタップの反応が最大350ミリ秒
  遅れるが、週間表示のホームボタンと同じ遅れ方なので問題ないと
  利用者が判断した

## やったこと

- `main-page.js` の `homeButtonHdr()` の先頭で `ytsched.search_str0`
  （検索画面かどうか）を見て早期 `return` する分岐を追加した。通常
  表示側（既存の `if (!clickCount)` の分岐）は変えていない
- 検索画面側は、1回目のタップで `clickCount` を立てて `setTimeout` で
  350ミリ秒待つ。その間に2回目のタップが来れば、即座に
  `ytsched.doGet(ytsched.url_prefix, { date: monday_str, sde_align: "top" })`
  （通常表示のダブルタップと同じ処理）を実行して `clickCount` を
  リセットする。350ミリ秒待っても2回目が来なければ、`setTimeout` の
  コールバックで従来のシングルタップの動作（`doPost` での読み直し、
  検索語を保持）を行う
  - コールバック内で `clickCount` が0（＝待っている間にダブルタップと
    判定されて処理済み）なら何もしない、という条件を入れて、まれに
    `doGet` の遷移が遅れて `setTimeout` が先に発火した場合の二重実行を
    防いだ
- デバッグ用の `console.log`（"single click" / "search_str0=..." など）
  は整理して削除した

## テスト

- `tests/test_browser.py` に2件追加
  - `test_home_button_single_tap_still_reloads_search_screen`:
    検索画面で1回だけタップしても、遅延後に今週の月曜へ読み直される
    ことを確認
  - `test_home_button_double_tap_reloads_search_screen_like_normal_view`:
    検索画面でダブルタップすると `sde_align=top` 付きで読み直される
    ことを確認
- 修正前のコードに対して `test_home_button_double_tap_reloads_search_screen_like_normal_view`
  を実行し、10秒のタイムアウトで落ちる（`date=...` のみで
  `sde_align=top` が付かない）ことを確かめてから、修正を戻した
- `uv run pytest`（610件）・`uv run ruff check`・`uv run ruff format --check`・
  `uv run basedpyright`: すべて通過（`archives/` 配下の既存
  未整形ファイルは対象外）
- verifier が `--datadir` に一時ディレクトリを指定してアプリを実際に
  起動し、動作を確認
- reviewer が分岐の競合・取りこぼしの有無、通常表示側への影響、
  TODO-123 の sessionStorage 方式とあえて別方式にしたことの妥当性を
  確認。実質的な指摘は無かった（シングルタップ側のテストが
  `sde_align` が付かないことまでは見ていない、という参考程度の所感が
  1件あったが、`get_argument` の仕様上バグにはつながらないため
  必須の指摘ではないとされた）
