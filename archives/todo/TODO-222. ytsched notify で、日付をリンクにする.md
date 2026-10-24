# TODO-222. ytsched notify で、日付をリンクにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 60 | 17,616 | 37,169 | 2,805,626 | 81% |
| verifier | Sonnet 5.5 | medium | 28 | 210 | 77,470 | 282,499 | 10% |
| reviewer | Opus 5.5 | high | 18 | 2,145 | 44,522 | 270,767 | 9% |
| 合計 |  |  | 106 | 19,971 | 159,161 | 3,358,892 | 計 3,538,130 |

- 立ててから内容を直し（`cff76d2`）、そのあと TODO-223 を立てたので、
  `--since '2026-10-05 23:14:57'`（`cff76d2` の時刻）で切った
- main の分には、並行して進めた TODO-223 の改名作業も少し入っている
- verifier の output が小さいのは、`subagents/` のログが途中までしか
  拾えないため（`token-usage.py` の既知の傾向）

## きっかけ

TODO-153 の毎朝の通知から、その日の Web 画面を 1 タップで開きたい。
`slack-send.sh` は本文全体をコードブロックで囲んで送るので、その中では
リンクにならない。そのため `slack-send.sh` の側も変える必要があった。
最初は既定でリンクを付ける案だったが、`--url` を指定したときだけ付ける
形に利用者と決め直した（既定の URL は持たない）。

## やったこと

- `ytsched notify --url URL` を足した（`src/ytsched/notify.py`・
  `src/ytsched/__main__.py`）。指定したときだけ本文を Slack の mrkdwn で出す
  - 日付の見出しを `<URL?date=YYYY-MM-DD|2026-09-02 (水)>` のリンクにする
  - 予定の行を、時刻の桁が揃うよう `` ` `` で囲む。タイトル中の `` ` `` は
    インラインコードを途中で切るので `'` に置き換える
  - タイトル・ToDo・memo の `&` `<` `>` をエスケープする（`slack_escape()`）
  - 指定しなければ、出力は今までと同じ
- `slack-send.sh` に `-r` を足した（別リポジトリ `~/work/slack-send`、
  `e3ca7bc`）。付けると本文をコードブロックで囲まずに送る。付けなければ
  payload は今までと同じ。README にも書いた
- テストを 2 件足した（`tests/test_notify.py`）
- `docs/User.md`・`docs/Developer.md` に `--url` と `-r` の cron の例を足した。
  URL にはクエリ（`?…`）を付けないことも書いた

## 確かめたこと

- reviewer: 要修正の指摘は無し。検討の 3 点のうち、タイトル中の `` ` `` と
  URL の前提は main が直した。CLI の `url=url` を消しても落ちるテストが
  無い点は、verifier の CLI の確認で補った
  （[reviewer-report.md](../agents/TODO-222/reviewer-report.md)）
- verifier: lint・型チェック・テスト（721 passed）が通った。CLI で、
  `--url` 無しの出力が素のテキストのままであること、`--url` 付きで 2 日目の
  リンクが `date=2026-09-03` になることを見た。予定の行の
  `slack_escape` を外すとテストが落ちた。`slack-send.sh` は偽の `curl` で
  payload を見て、`-r` の有無で text が期待どおり変わった
  （[verifier-report.md](../agents/TODO-222/verifier-report.md)）

## 残ること

- 実際に Slack へ送ったときの見た目（行頭の空白が残るか、インライン
  コードの中で日本語の桁が揃うか）は確かめていない。cron に `--url` と
  `-r` を足したあとの最初の通知で見る

## 分担の振り返り

- reviewer は、タイトル中の `` ` `` で行が崩れる点と、クエリ付きの URL で
  リンクが壊れる点を出力で示した。どちらも main が見送ろうとしていた所で、
  直すのは数行で済んだ
- verifier は食い違いを見つけなかった。CLI 経由のテストが無い穴を、
  依頼に書いた CLI の実行で埋められた
- 見込みと実施は一致した。次に同じ規模（出力の分岐が 1 つ増える、別
  リポジトリの小さな変更を伴う）なら同じ組み方でよい。verifier の
  「壊すと落ちるか」は 1 か所で足りたので、次も 1 か所に絞って頼む
