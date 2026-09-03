# TODO-181 verifier への依頼

## 目的

`tests/test_browser.py` の `_double_tap_home_in_search()` で、1 回目の
読み直しが `interval_msec` に間に合わないときに `assert` で落としていたのを、
`pytest.skip()`（理由に実測した時間を入れる）へ変えた。機械が混んでいると
検索画面の読み直しが想定（180〜360 ミリ秒）を超えて 500〜600 ミリ秒に
届き、`test_home_button_double_tap_by_touch_returns_to_the_top_screen`
などがリグレッションと紛らわしい形で落ちていた（TODO-180 の確認時に毎回
2 件ほど）。

確かめたいのは次の 3 点。

1. 通常（機械が空いている）ときは、これまでどおりダブルタップのテストが
   走って通ること。skip 側へ逃げていないこと
2. 読み直しが `interval_msec` を超えたときは、`AssertionError` ではなく
   `pytest.skip`（メッセージが「機械が混雑:」で始まる）になること
3. lint が通ること

## 対象

`tests/test_browser.py` の `_double_tap_home_in_search()` のみ。develop の
HEAD からの差分は下記（テストコード 1 か所 ＋ docstring）。

```diff
     elapsed = (time.monotonic() - start) * 1000
-    assert elapsed < interval_msec, (
-        f"1 回目の読み直しに {elapsed:.0f} ミリ秒かかり、"
-        f"{interval_msec} ミリ秒後の 2 回目を置けない"
-    )
+    if elapsed >= interval_msec:
+        pytest.skip(
+            f"機械が混雑: 1 回目の読み直しに {elapsed:.0f} ミリ秒かかり、"
+            f"{interval_msec} ミリ秒後の 2 回目を置けない"
+        )
     page.wait_for_timeout(interval_msec - elapsed)
     tap(page)
```

呼び出し側（`interval_msec` を渡す 3 テスト）は変えていない。
`interval_msec` が `None` の経路（間を置かず 2 回）も変えていない。

## 確認してほしいこと

1. `mise run lint` が通ること
2. `uv run pytest tests/test_browser.py -k "double_tap or home_button"` を
   **3 回**走らせ、結果を報告する（passed / skipped / failed の件数）。
   - ダブルタップ系が **failed になっていないこと**。とくに
     `_double_tap_home_in_search` 由来の
     「…ミリ秒かかり、… 2 回目を置けない」という `AssertionError` が
     出ていないこと
   - skipped が出た場合は、その理由（`-rs` を付ける）が
     「機械が混雑:」で始まっていること。0 件でもよい
3. **skip の分岐が実際に効くこと**を、スクラッチで確かめる。
   リポジトリのファイルは変更しないこと。手順の一例:
   - スクラッチ用ディレクトリ
     （`/tmp/claude-649/-home-ytani-work-ytsched/6e301425-7bb8-4753-b1f1-e1cac81e22c6/scratchpad`）に
     小さな Python スクリプトを置き、`tests/test_browser.py` から
     `_double_tap_home_in_search` を import する
   - `page` と `tap` はスタブにする。`tap` は何もしない。
     `page.wait_for_function` / `page.wait_for_selector` /
     `page.wait_for_timeout` も何もしない。`wait_for_selector` の中で
     `time.sleep(0.05)` して読み直しに時間がかかる状況を作る
     （`_mark` はモジュール関数なので、`page.evaluate` をスタブすれば足りる）
   - `interval_msec=10` で呼ぶと `pytest.skip` 由来の例外
     （`_pytest.outcomes.Skipped`）が送出され、`str(exc)` が
     「機械が混雑:」で始まること
   - `interval_msec=100000` で呼ぶと skip されず、最後まで進むこと
     （`tap` が 2 回呼ばれる）
   スタブが組みにくければ、`_double_tap_home_in_search` の当該ロジック
   （`elapsed` 計算 → `if elapsed >= interval_msec: pytest.skip(...)`）
   だけを取り出した最小再現でもよい。どちらにしたかを報告に書く
4. 気づいた懸念があれば挙げる。とくに「読み直しが恒常的に遅くなる
   リグレッションが起きたとき、fail ではなく skip で見逃す余地」について
   （TODO-165 の reviewer 指摘 3 が、まさにこの点を挙げていた）

## 決まり

- **コードは直さない。** 見つけたことは報告するだけ。直すかどうかは
  管理者が判断する
- リポジトリのソース・テスト・設定ファイルには書き込まない
  （Bash のリダイレクトや heredoc も含む）。スクラッチは
  上記の一時ディレクトリを使う
- `git commit` / `git tag` / `TODO.md` の編集はしない
- 報告は `archives/agents/TODO-181/verifier-report.md` に書く
- **返事は 5 行以内**（終わったか・報告ファイルのパス・判断が要る点）
