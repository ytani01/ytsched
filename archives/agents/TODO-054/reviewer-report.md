# TODO-054 reviewer 報告

対象: `src/ytsched/webroot/static/js/my.js` 末尾のスワイプ処理
（`touchStartHdr` / `touchMoveHdr` / `touchEndHdr` / `touchCancelHdr`）、
`src/ytsched/webroot/templates/main.html` の登録部分。

## 確信度の高い指摘

無し。

境界条件（`SWIPE_MIN_X` 未満、縦優勢、800ms 超過、画面端 30px 以内、
入力欄上、2 本指）は一通り確認したが、`touchStart` → `touchEnd` の
組み立てにバグは見当たらなかった。`moveToMonday()` の向き
（`dx < 0` で `direction=1` = 次の週、`ArrowRight` と同じ向き）も
コメント「左へ払ったら次の週」と一致している。`window` への登録は
`stopPropagation()` を呼んでいる箇所が無いので、バブリングも問題ない。
`keyHdr` / `popstateHdr` と同じく `main.html` だけに登録されている点も
揃っている。ページ遷移は `doGet()` が `location.href` を書き換える
フルナビゲーションなので、`swipeStart` はページを離れると
そのまま破棄され、持ち越しの心配は無い。

## 確信度が中程度の指摘

- `my.js` 693〜700 行目、`touchMoveHdr` に付いた JSDoc が紛らわしい。

  ```js
  /**
   * 2 本目の指が触れたら見送る (TODO-054)。
   *
   * ``touchstart`` は指が増えるたびに呼ばれるので、1 本目で始めた
   * スワイプもここで取り消される。
   */
  const touchMoveHdr = (event) => {
      if ( event.touches.length !== 1 ) {
          swipeStart = null;
      }
  };
  ```

  コメントは「`touchstart` が指が増えるたびに呼ばれる」という
  `touchStartHdr` 側の話をしているのに、貼ってあるのは `touchmove` を
  受ける `touchMoveHdr`。実際、`touchStartHdr` は先頭で無条件に
  `swipeStart = null` としてから 1 本指以外を弾いているので、2 本目の
  指が触れた時点で `swipeStart` はすでに `null` になっている
  （JS はシングルスレッドなので、2 本目の `touchstart` が
  `touchMoveHdr` より先に必ず処理される）。つまり `touchMoveHdr` の
  この判定は、今の実装では実質到達しない防御コードで、コメントは
  自分の関数ではなく `touchStartHdr` の動きを説明している。実害は
  無いが、次に読む人が「`touchMoveHdr` がここで取り消している」と
  誤解しやすい。コメントを `touchStartHdr` 側の説明に合わせるか、
  「念のための二重チェック」だと明記するかの整理を勧める。

## 確信度の低い指摘（参考）

- `SWIPE_MAX_MSEC = 800` は、ゆっくり払うスワイプを取りこぼす方向に
  効く（誤検出よりは取りこぼしに倒している）。意図した配分かどうかは
  実機で試さないと分からないので、確信度は低い
- `SWIPE_EDGE_PX = 30` は iOS Safari の戻る/進むジェスチャの受付幅より
  狭い端末があるかもしれない（この幅は端末・OS バージョンで変わる）。
  実機で誤検出が出るかどうかは verifier の確認範囲だと思う
