# TODO-239. 添付ファイルを外して同じ名前で付け直したとき、古い画像が表示され続けないかを確かめる（対応しない）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | verifier（Sonnet 5.5 / medium）→ 直すなら implementer（Sonnet 5.5 / medium）+ reviewer（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 11 | 2,647 | 5,941 | 420,572 | 39% |
| verifier-239（verifier） | Sonnet 5.5 | medium | 36 | 10,527 | 48,019 | 605,871 | 61% |
| 合計 |  |  | 47 | 13,174 | 53,960 | 1,026,443 | 計 1,093,624 |

- 集計は `--since '2026-11-25 06:04:00'`（項目を立ててから作業を始めるまでに TODO-237・238 の完了を挟んだため）

## きっかけ

TODO-237 の reviewer の指摘 5（`archives/agents/TODO-237/reviewer-report.md`）。`AttachHandler` は ETag も `Cache-Control` も出さないので、同じ名前で付け直した画像をブラウザが古いまま出すかもしれない、というもの。

## やらないと決めた理由

実測では起きた（下）。直す案として `Cache-Control: no-cache` を付ける案と、URL に版を付ける案を示したが、利用者が「やらない」を選んだ。同じ名前での付け直しはまれで、古い画像はブラウザの再読み込みで直るため。

## 確かめたこと

verifier が Playwright と `/usr/bin/chromium` で実測した（`archives/agents/TODO-239/verifier-report.md`、スクリプトは `measure.py`）。

- 旧 `a.png`（10x10、mtime を 30 日前にした）を外し、40x30 の `a.png` を画面操作で付け直した。名前は `a.png` のまま
- `page.goto` で同じ画面へ移動した場合も、週画面から詳細を開き直した場合も、3 回中 3 回とも古い 10x10 が出た。応答の `Last-Modified` は旧ファイルの値で、Chromium は `servedFromCache` と報告した
- 確かめていないこと: 旧ファイルの mtime が新しい場合、Chromium 以外のブラウザ。やらないと決めたので、これ以上は確かめない

## 分担の振り返り

- verifier は、古い画像が出ることを画面操作だけで再現した。サーバに要求が届いたかは、アクセスログに残らず決めきれなかったが、寸法と `Last-Modified` で判定には足りた
- 見込みでは「直すなら implementer + reviewer」としていたが、やらないことになったので起動していない
- 次に同じ規模の「起きるかを確かめる」項目なら、verifier（Sonnet / medium）1 人で足りる。依頼で「判定には寸法と応答ヘッダを使う」と決めておけば、要求が届いたかの調べに使った分を省ける
