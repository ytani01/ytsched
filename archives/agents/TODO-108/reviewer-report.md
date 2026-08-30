# TODO-108 reviewer 報告

## 指摘

### 1. `data-search-str0` に二重引用符を含む検索文字列を安全に渡せない

- `src/ytsched/webroot/templates/main.html:9`
- `base.html` は `{% autoescape None %}` のため、`search_str` を属性値へ
  そのまま埋めると二重引用符で属性が途中で閉じる。例えば
  `search_str` が `foo"bar` のとき、ブラウザが読む
  `dataset.searchStr0` は `foo` になり、ホームボタンが検索状態かどうかを
  正しく判定できない。後続の属性も文字列次第で壊れる。
- 属性値に移した動的値をエスケープする方法を用意し、その入力を
  `tests/test_web.py` で確認する必要がある。現在のテストは通常の文字列と
  inline event handler の不在だけで、このケースを検出しない。

## 確認結果

- `swipe.js` は、実マウスイベントを capture で止め、`mouseup` 時に
  `data-action` 要素へ untrusted の `mousedown` を再送している。
  `mouseDownHdr()` が untrusted event を見送るため再帰せず、親要素の
  イベント委譲へ届く。ゲージ操作の既存ブラウザテストもこの経路を通る。
- それ以外に、操作の正しさ・`swipe.js` との競合・TODO-108 の範囲について
  確信度の高い指摘は無し。

## 再確認（修正後）

- 指摘 1 は解消済み。`main.html` の通常の自動エスケープで
  `data-search-str0` の二重引用符が文字参照として出力される。
  `TestMainHandler.test_search_str_in_data_attribute_is_escaped` が
  `foo"bar` を実際に描画し、復元値まで確認している。
- 現行のイベント委譲と `swipe.js` の再送経路、テンプレートの
  inline event handler 不在を差分で再確認した。ほかに確信度の高い問題は無し。
