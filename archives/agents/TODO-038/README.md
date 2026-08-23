# TODO-038 の分担

HTML・CSS のリファクタリング。詳しくは
[TODO-038 のファイル](../../todo/TODO-038.%20HTML・CSS%20のリファクタリング.md)。

## 誰にどこを担当させたか

| 担当 | 依頼書 | 報告 |
|---|---|---|
| implementer（1 段目・片付け） | [request-1](implementer-request-1.md) | [report-1](implementer-report-1.md) |
| implementer（2 段目・`style` → CSS） | [request-2](implementer-request-2.md) | [report-2](implementer-report-2.md) |
| implementer（3 段目・クラス名の付け直し） | [request-3](implementer-request-3.md) | **無し**（[main の覚書](main-note-step3.md)） |
| verifier | [request](verifier-request.md) | [report](verifier-report.md) |
| reviewer | [request](reviewer-request.md) | [report](reviewer-report.md) |
| wording | [request](wording-request.md) | [report](wording-report.md) |

## その分担にした理由

### implementer を分けた

複数のファイル（テンプレート 4 つ・CSS・JS）にまたがり、消すもの・
書き換えるもの・名前を付け直すものが混ざる規模なので、main では抱えない。

### 3 段に分けた

**1 回でやると、見た目が変わったときに原因を切り分けられない。**
消す作業（1 段目）と、`style` を CSS へ寄せる作業（2 段目）を混ぜると、
差が出たときにどちらのせいか分からなくなる。段ごとに画素単位の比較を
挟めるようにした。

3 段目は当初の見込みに無かった。2 段目で `.my-fs-xx-small`
`.my-lh-12` のような**値をそのまま名前にしたクラス**が 61 か所入り、
利用者から「定義する意味は？」と問われたのがきっかけ。
`style` を CSS へ寄せる利点は（1）インライン `style` を無くす、
（2）同じ役割の箇所を 1 か所で変えられるようにする —— の 2 つで、
**(2) は役割で名付けたときだけ効く**。そこを直す段を足した。

### reviewer を入れた

`~/.claude/CLAUDE.md` の基準（**挙動や分岐が変わる項目には入れる**）に沿う。
`const detail_h` → `let`（横向きで TypeError が出ていた）と、
`doPost({{ url_prefix }}, …)` への引用符の追加の 2 件で挙動が変わる。
テストは本文の語と `id="date-…"` しか見ておらず、崩れは捕まえない。

### verifier を厚く使った

確かめ方がスクリーンショットの比較になるので、**試せる手順がある**
（`~/.claude/CLAUDE.md` の基準）。さらに 3 段目の implementer が
検証に入る直前に API エラーで落ち、**3 段目だけ実装者側の確認が
一切取れていない**ため、そこを名指しで厚く見てもらった。

### wording を立てた

`.md` が入るコミットなので、`CLAUDE.md`（ytsched）の決まりどおり。
対象は依頼書・報告・archives の全部。

## 3 段目の implementer が落ちた件

実装を終えたあと、検証に入る直前に API エラーで落ちた。
**実装をやり直させてはいない。** 作業ツリーと退避を `diff -u` で
1 か所ずつ照らし合わせ、依頼どおり全部入っていることを main が確かめた
（[main-note-step3.md](main-note-step3.md)）。検証はもともと verifier の
担当なので、そのまま verifier へ回した。

## 検証が一度中断した件

verifier が画素単位の比較の途中でセッションごと止まり、一時ディレクトリも
消えたので、**最初からやり直した**。やり直しの間に利用者が別件
（サブエージェントのモデル変更）をコミットして `HEAD` が動いたため、
比べる相手は `HEAD` ではなく **コミット `cca8269` で固定する**よう
main から指示し直した。

そのコミット `74a480a` には、TODO-038 で `git rm` した
`pagetop.css` と `my_cookie.js` の削除も巻き込まれている
（ステージに残っていた）。利用者の判断でそのままにした。
