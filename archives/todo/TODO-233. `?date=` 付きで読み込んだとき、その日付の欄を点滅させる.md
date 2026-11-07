# TODO-233. `?date=` 付きで読み込んだとき、その日付の欄を点滅させる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high、再レビュー 1 回）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 58 | 14,716 | 28,861 | 2,214,777 | 62% |
| review-233（reviewer） | Opus 5.5 | high | 42 | 11,265 | 53,460 | 776,434 | 23% |
| verify-233（verifier） | Sonnet 5.5 | medium | 32 | 6,910 | 39,969 | 487,654 | 15% |
| 合計 |  |  | 132 | 32,891 | 122,290 | 3,478,865 | 計 3,634,178 |

- どの担当も定義のモデル・effort のまま（Agent ツールに同じ値を付けた）

## きっかけ

日付指定のリンクで開いたとき、削除のあとと同じように、その日の日付の欄を点滅させたい（利用者の依頼）。

## やったこと

- `main-page.js` の `flashUpdated()` で、`flash_date` が無ければ、開いた URL の `date` を点滅させる日付に使う。`date` は URL から消さない
- `date` はスクリプトを読んだ時点で `linkDate` に取る。`load` では `onloadHdr()` が先に URL へ `date` を書き込むので、日付なしで開いてもページが長いと点滅していた（reviewer の指摘 1）
- `date` だけのときは TODO-215 の位置合わせ（`scrollBy`）をしない。`sde_align=bottom` で予定の多い日を、日付の欄が見えるようにずらしてしまうため
- 点滅させる場合を利用者と決めた: ページを読み込んだとき（リンク・リロード・`doGet()`・ページ全体を読み込み直すリンクからの戻る）は毎回。画面内の移動（`pushState`）からの戻る/進む（`popstate`）では点滅させない（reviewer の指摘 2）。月の表示には日付の欄が無いので点滅しない（対象外のまま）
- `tests/test_browser.py` に 3 件足した（`date` で点滅する、日付なしでは点滅しない、位置をずらさない）。TODO-215 のテストの予定の書き出しを `_write_many_sched` に切り出した
- `src/README.md` に点滅の条件を足し、前からあった「3 秒点滅」を CSS に合わせて 5 秒に直した（reviewer の範囲外の指摘）

## 確かめたこと

- main: 位置合わせのガードを外す・`linkDate` を URL の値に戻すと、足したテストがそれぞれ落ちる
- reviewer: `flash_*` があるときの挙動は変わらない。再レビューで指摘 1 の直しを確認。JSDoc と `flashUpdated` の間に `linkDate` が挟まった件は、`linkDate` を JSDoc の上へ移して直した
- verifier: fmt で差分なし、lint・typecheck・点滅のテストが通った。Playwright で a（`?date=` で 1 件点滅）・b（日付なしで 0 件）・c（画面内の移動から戻ると 0 件）を実測。ページ全体を読み込み直すミニカレンダーのリンク（`view=month`）から戻ると点滅するのは、ページを読み込むので決めたとおり（`archives/agents/TODO-233/verifier-report.md`）

## 分担の振り返り

- reviewer は、`onloadHdr()` が先に `date` を書き込む件（指摘 1）と、`popstate` の経路（指摘 2）を Playwright で確かめて見つけた。どちらも main のテストでは捕まえていなかった。verifier は、ページ全体を読み込み直すリンクからの戻る経路を見つけた
- 見込みとの食い違いは再レビュー 1 回だけ。指摘 2 は、最初に「戻る/進むも含め」と選択肢に書いたのが曖昧だった
- 次に同じ規模でやるなら同じ組み方でよい。ただし「いつ点滅させるか」のように経路が複数ある方針を聞くときは、選択肢に `load` と `popstate` を分けて書き、reviewer の指摘 2 を先に潰す
