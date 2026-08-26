# TODO-056 verifier への依頼

## 何を確かめてほしいか

`tests/test_browser.py` を足した（ブラウザを動かすテスト）。
**このテストが本当に退行を捕まえるか**を、自分の手で確かめてほしい。

### 1. 素の状態で通ること

```sh
mise run test
```

（`tests/test_browser.py` の 3 件を含めて全部通るはず）

### 2. 退行をわざと戻したときに落ちること

**ここが本題。** 落ちないテストでは意味が無い。
`src/ytsched/webroot/static/js/my.js` を一時的に書き換えて確かめ、
**確かめ終わったら必ず元に戻すこと**（`git checkout` でよい）。

- **TODO-049 の退行**: `scrollToId()` の中で、`el == null` を見る
  ブロックと、`body_h <= win_h` を見るブロックの**順番を入れ替える**
  （`body_h` のほうを先にする）。
  → `test_home_button_moves_the_view` が落ちるはず
- **TODO-063 の退行**: `moveToMonday()` の
  `const days = (1 - wday) + (direction > 0 ? 7 : -7);` を、
  `c01013e` の変更前の形（`git show c01013e^:src/ytsched/webroot/static/js/my.js`
  で見られる）に戻す。
  → `test_back_button_moves_a_week` が落ちるはず

### 3. 走らせ方が文書どおりに再現できること

`docs/Developer.md` の「テストの走らせ方」と `tests/README.md` の
「ブラウザを動かすテスト」を読んで、書いてあるとおりにできるか。

### 4. 気になった点

- 実データ（`~/ytsched/data`）に触れていないか
- テストが不安定になりそうな箇所（待ち方、port の取り方など）

## 決まっていること（蒸し返さなくてよい）

- playwright は dev 依存に入れる（`mise run test` で一緒に走る）
- ブラウザはシステムの `/usr/bin/chromium`。無ければ skip
- 範囲は TODO-049 の退行 1 件 ＋ 週送り

## 報告

`archives/agents/TODO-056/verifier-report.md` に書くこと。
**コードは直さない。** 見つけたことは報告だけする。
返事は 5 行以内で。
