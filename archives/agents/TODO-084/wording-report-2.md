# TODO-084 wording 報告（実装後、その 2）

対象: TODO-084 のコミットに入る `.md` 全部（`TODO.md`・`src/README.md`・
`tests/README.md`・`archives/todo/TODO-084. フッターの ◀▶ をダブルタップして
自動ページ送り.md`・`archives/agents/TODO-084/` 下の `.md` 9 本）。

**`wording-report.md`（項目を立てたときの分）で既に「前例なし」として
挙がった「自動ページ送り」「長押し」「キューに溜める」「pointerdown」
「pointerup」は、今回の判断で採用済みのため対象外。** 以下は今回の実装で
新たに増えた文書から拾った語。

## 前例が無い語（件数の少ない順）

| 語 | 出てくる箇所 | `git grep -cF` (HEAD) | 見立て |
| --- | --- | --- | --- |
| クロージャ | `request-reviewer.md`「クロージャを渡す形が `handler_util` の…」、`implementer-report.md`「渡すクロージャ（`min_value`/`max_value` を閉じ込めた `convert()`）」、`reviewer-report.md`「クロージャを `convert_value()` に渡す形も」、`request-writer.md`、`archives/todo/TODO-084…md` | **0 件（前例なし）** | プログラミングの一般的な専門用語（関数閉包）で、造語ではない。ただしこのリポジトリでは初出 |
| 浮いた書き方 | `reviewer-report.md`「浮いた書き方ではない」（クロージャを渡す形が `convert_value()` の使い方として妥当かの評価） | **0 件（前例なし）** | 「その場しのぎで筋が通っていない書き方」という意味で読めるが、この言い回し自体はここが初出。一般に通用するかは判断できない |
| 見送り対象 | `implementer-report.md`「`touchStartHdr()` / `mouseDownHdr()` の見送り対象に `[data-page-turn]` を追加」、`archives/todo/TODO-084…md`「`touchStartHdr()` / `mouseDownHdr()` の見送り対象」 | **0 件（前例なし）** | 「見送る」自体は前例多数（11 件）だが、「見送り対象」という名詞化した形はここが初出。普通の日本語で違和感は無い |
| ポーリング待ち | `reviewer-report.md`「`page.wait_for_function(..., timeout=…)` か「止めたあと変わらないこと」のポーリング待ちで判定しており」 | **0 件（前例なし）** | 一般的な IT 用語（poll）のカタカナ表記＋「待ち」。一般に通用しそうだが、このリポジトリでは初出 |
| 待ち時間頼み | `request-reviewer.md`「待ち時間頼みで、たまたま通っているだけでないか」 | **0 件（前例なし）** | 「固定の sleep に頼っているだけ」という意味で読めるが、この言い回し自体はここが初出。判断できない |
| 窓（時間の意味） | `request-writer.md`「ダブルタップの窓 350msec」、`writer-report.md`「窓（350msec）」 | 7 件（ただし全て `archives/agents/TODO-064/` の「窓の外」＝ブラウザウィンドウ／表示領域の意味） | **語自体には前例があるが、意味が違う。** TODO-064 の「窓」は画面の表示領域を指し、今回は「ダブルタップと判定する時間の幅」を指す。同じ語で別の概念に使っているため、紛れないか確認したほうがよい |

## 確認したが前例ありと判断した語（参考）

以下は候補に挙げたが、`HEAD` に前例があり、意味も一致していたため
対象から外した: 委譲（27 件）、後始末（30 件）、下限（6 件）、上限（34 件）、
共通化（7 件）、フォールバック（11 件）、ガード（19 件）、枠組み（5 件）、
衝突（13 件）、余裕（9 件）、確信度の高い指摘／確信度の低い指摘（reviewer
役割の定型見出し。35 件／6 件）、見送る（11 件）、重なる（25 件）、割り込む
（1 件、`TODO-057/reviewer-report.md` に既出）、捨てた（1 件）、取りやめた
（1 件、コミット前の `TODO.md` 自身に既出）、見かけ上（3 件）、shebang（4 件）。

## まとめ

- 読んだファイル: `TODO.md`（差分）、`src/README.md`（差分）、
  `tests/README.md`（差分）、
  `archives/todo/TODO-084. フッターの ◀▶ をダブルタップして自動ページ送り.md`
  （新規）、`archives/agents/TODO-084/README.md`・`request-implementer.md`・
  `request-reviewer.md`・`request-writer.md`・`implementer-report.md`・
  `verifier-report.md`・`reviewer-report.md`・`writer-report.md`・
  `wording-report.md`
- 前例が無い語（今回増えた分）: **5 語**
  クロージャ、浮いた書き方、見送り対象、ポーリング待ち、待ち時間頼み
  （加えて「窓」は語自体に前例があるが意味が異なるため参考として添えた）
