# TODO-039 reviewer 報告

## 結論

確信度の高い指摘は無し。依頼書で挙げられていた懸念点（`gap` の計算、
`transform` の競合、`scale` の閾値、登録のしかた、`manifest.json` の
`scope`）を一つずつ確かめたが、いずれも設計として妥当だった。詳細は下記。

## 確認した点と、問題が無いと判断した理由

- **`transform` の競合。** `my.css` を全文見たが、`transform` を使っている
  既存ルール（`.my-gage-text`・`.longtext-sw-label`・`.my-spinner`）は
  いずれも `#menu_bar` / `#menu` とは無関係のセレクタで、対象要素に
  `transform` を当てているものは無い。`main.html` / `edit.html` にも
  `style="transform:…"` の直書きは無い。競合は無い
- **`gap` の計算式。** `window.innerHeight - vv.height - vv.offsetTop` は
  iOS Safari でキーボードの高さを求める際によく使われる式で、
  `Math.max(0, …)` で負の値を切り捨てている。アドレスバーの出入りで
  `vv.height` が `window.innerHeight` を超える方向にずれても、この
  クランプで見た目には影響しない（バーが不要に持ち上がることはない）
- **登録のしかた。** `my.js` は `<head>` で `defer` 無しに同期読み込みされ、
  `body` より前に実行される。その時点で `window` の `load` はまだ
  発火していないので、`addEventListener("load", …)` は確実に間に合う。
  ページ遷移のたびにスクリプトが 1 回だけ評価されるので、二重登録も
  起きない
- **`manifest.json` の `start_url` / `scope`。** 依頼書の内容どおりで、
  `webapp.py` の `DEF_URL_PREFIX = "/ytsched"` と `static_url_prefix`
  の組み合わせで `../` が `/ytsched/` に解決されることを確認した。
  インストール後に開くのは `start_url` であり、ブラウザでたまたま
  末尾スラッシュ無しの URL を見ていたことは関係しない

## 確信度が低いもの（参考）

- **`my.js` の `followKeyboard()` のコメントと挙動が少しずれている。**
  「ピンチで拡大している間 (`scale > 1`) は何もしない」とあるが、実際の
  コードは `offset = 0` にして `translateY(0px)` を書き込むため、
  もし拡大する前にキーボードが出ていてバーが持ち上がっていた場合、
  拡大した瞬間にバーがキーボードの後ろへ戻る（「何もしない」なら前の
  位置を保つはず）。実機でしか挙動を確かめられない組み合わせ
  （拡大 × キーボード表示）なので確信度は低いが、コメントの文言と
  実装の意図が食い違っている点だけは読んで分かる
- 依頼書にある「`vv.scale` が `undefined` の環境で丸ごと止まる」件は、
  仕様上 `scale` は `visualViewport` と同時に導入されたプロパティで、
  対応ブラウザで `undefined` になる実例は見当たらなかった。理論上の
  懸念にとどまると判断した
