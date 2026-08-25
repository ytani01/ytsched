# TODO-049 の分担

## 誰に何をさせたか

| 担当 | 何を |
|------|------|
| main | 着手時の判断 2 つを利用者と決め、変更前のキャプチャを撮り、依頼書を書き、報告を受けて判断する |
| implementer | 週の範囲への変更、`--days` の削除、ゲージの週単位化、`my.js` の掃除、テストの直し |
| verifier | テスト・lint・型チェックと、実際に起動しての週送り・今週へ戻る・検索の確認、変更後のキャプチャ |
| reviewer | 変更したコードの質を見る |
| wording | このコミットに入る `.md` から、前例の無い語を挙げる |

依頼書は [request-implementer.md](request-implementer.md)・
[request-reviewer.md](request-reviewer.md)・[request-verifier.md](request-verifier.md)。
implementer には 3 回渡した（[2 回目](request-implementer-2.md)は reviewer の
指摘、[3 回目](request-implementer-3.md)は利用者が見つけた退行）。

報告は [implementer-report.md](implementer-report.md)・
[implementer-report-2.md](implementer-report-2.md)・
[implementer-report-3.md](implementer-report-3.md)・
[verifier-report.md](verifier-report.md)・[reviewer-report.md](reviewer-report.md)・
[wording-report.md](wording-report.md)。

## その分担にした理由

- **implementer を立てた。** Python（`main_handler.py`・`handler.py`・
  `webapp.py`・`__main__.py`）・JavaScript・テンプレート・CSS・テストの
  5 つにまたがる。`CLAUDE.md` の「複数のファイルにまたがる」に当てはまる
- **verifier を立てた。** 表示の形が変わるので、テストだけでは確かめ
  られない。週送り・今週へ戻る・検索のそれぞれで実際に画面を出し、
  ゲージの針が動くかを見る必要がある。TODO-009 の「README の手順を実際に
  再現する」と同じで、試せる手順があるときは分けると効く
- **reviewer を立てた。** `CLAUDE.md` の「挙動や分岐が変わる項目には
  入れる」に当てはまる。表示範囲の決め方そのものが変わり、`my.js` から
  スクロール追従が丸ごと落ちる。「消しすぎ」「消し足りない」はテストが
  通ることを見ても出てこない

## 着手時に決めたこと（`TODO.md` に書いていない 2 つ）

どちらも利用者に選んでもらった。

1. **`--days` は消す。** 週表示になると通常の表示に効かなくなり、残る
   用途は `date_range()` の余白計算だけ。そこは `SEARCH_MODE_MAX_DAYS`
   （1825）のほうが常に大きく、実質使われない。「渡せるのに効かない」
   オプションを残さないほうがよい
2. **ゲージの針は、前に見ていた週の位置から動かす。** `sessionStorage`
   に直前の週を持ち、読み込み時にまずその位置へ置いてから今の週へ動かす。
   `transition` を足すだけでは、週送りがページの読み直しなので針が動いて
   見えない（初期値が `auto` で補間が起きない）

## やってみて分かったこと

### reviewer は効いた

3 件の指摘のうち 1 件は実害のある経路だった。`dispGage()` の
`sessionStorage` が無防備で、例外が出ると `onloadHdr()` の
`body_h < win_h` 分岐で画面が白いまま止まる。**しかも「週表示にした
ことでこの分岐に入る頻度が上がっている」**というところまで見ていて、
これはテストが通ることを見ても出てこない種類の指摘だった。

依頼書で `sessionStorage` を名指しで懸念として渡していたが、
**発現条件を突き止めたのは reviewer のほう。**懸念を渡すだけでも
効くことが分かった。

### verifier は退行を取りこぼした

**ホームボタンの退行を、verifier は捕まえられなかった。**「今週へ
戻る（ホームボタン）」を確認項目に入れていたのに、**今週を表示した
状態から**押していたので、今日が DOM にあり通ってしまった。

原因は**依頼書の書き方**。「今週へ戻る」としか書かず、**どこから
戻るかを指定しなかった**。戻る・飛ぶ操作は、離れた位置から試さないと
意味が無い。

`.claude/agents/verifier.md` を直すことも考えたが、**今回は依頼書側の
問題なので直さないことにした**（`CLAUDE.md` の「定期的な見直しは
しない」に従う）。次の項目で同じ取りこぼしが出たら、そのとき定義を
見直す。

### テストで捕まえられない範囲がある

この退行は `AsyncHTTPTestCase` では原理的に捕まえられない
（JavaScript を実行しないため）。この穴は **TODO-056** として立てた。
