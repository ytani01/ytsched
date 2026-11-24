# TODO-237. 予定に複数のファイルを添付し、画像は詳細を開くと表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Opus 5.5 / high）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | implementer（Opus 5.5 / high）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| impl-237（implementer） | Opus 5.5 | high | 173 | 59,214 | 208,705 | 6,115,159 | 43% |
| main | Opus 5.5 | medium | 160 | 23,037 | 159,715 | 5,043,670 | 36% |
| rev-237（reviewer） | Opus 5.5 | high | 66 | 28,185 | 95,743 | 1,779,391 | 13% |
| ver-237（verifier） | Sonnet 5.5 | medium | 58 | 12,389 | 48,827 | 972,500 | 7% |
| wording-238（wording） | Sonnet 5.5 | low | 6 | 770 | 20,557 | 45,757 | 0% |
| wording-239（wording） | Sonnet 5.5 | low | 6 | 766 | 18,289 | 48,245 | 0% |
| 合計 |  |  | 469 | 124,361 | 551,836 | 14,004,722 | 計 14,681,388 |

- impl-237 は 2 回起動した。1 回目（前のセッション）はコードとテストを書いたところで止まり、報告が無かった。
  2 回目が差分を引き継いで仕上げた。表は 2 回の合計
- wording の 2 行は、この項目の作業中に追加した TODO-238・TODO-239 の言葉の確認で、集計範囲に入った分
- main には、同じ範囲で行った全体ルールの確認（`bff10f6`）も入っている

## きっかけ

前のセッションで、予定にファイルを添付できるようにする項目として立てた（`7bc26b0`）。
依頼のくわしい経緯は、完了させたセッションでは確かめていない。

## やったこと

- 編集画面で複数のファイルを添付し、1 つずつ外せるようにした。置き場所は
  `{データディレクトリ}/attachments/{UUID}/`（`attach.py` の `AttachStore`）。同じ名前があれば
  `名前-1.拡張子` のように番号を付け、上書きしない
- 添付を返す `AttachHandler`（`attach_handler.py`、`StaticFileHandler` を継承）を足した。
  ファイル名と UUID を検証し、データディレクトリの外は返さない
- 詳細を開くと、画像は表示し、ほかはファイル名のリンクにした（`sde.html`）。
  `HandlerBase.get_template_namespace()` で全テンプレートに `attach_store` を渡す
- ゴミ箱から削除したとき・空にしたとき、同じ UUID の版が予定にもゴミ箱にも残っていなければ、
  フォルダを消す（`trash_handler.py`）
- テスト `tests/test_attach.py`（16 件）。文書は `docs/data-format.md`（置き場所と扱い）、`README.md`、
  `src/README.md`（モジュール一覧、クラス図、`URLSpec` の記述）、`tests/README.md` を直した
- 方針では大きさの上限を「tornado の既定の 100MB」としていたが、実際に効くのは ytsched の
  `webapp --size-limit`（既定 100MB）なので、文書はこちらに合わせた

## 確かめたこと

- `mise run fmt` / `lint` / `typecheck`、`uv run pytest -q tests/test_attach.py`（16 件）が通る
- ファイル名の検証とゴミ箱の判定を一時的に壊すと、`tests/test_attach.py` が失敗する
- 一時ディレクトリで webapp を起動し、Playwright で PNG と PDF を添付 → 詳細で画像が表示され
  （`naturalWidth` 20）、PDF はリンクで開ける → PDF を外すと消える → ゴミ箱で 2 件のうち 1 件だけ
  削除するとフォルダが残り、残りも削除するとフォルダが消える
- 添付の URL に `..`・`%2F`・`%2e%2e`・`%5C` を含むパスを 7 通り送り、すべて 404
- `src/README.md` のクラス図を描画し、欠けが無いこと（矢印のラベルが近い箇所はあるが読める）

担当の報告の指摘との対応（`archives/agents/TODO-237/`）:

- reviewer 1（`. a.png` のような名前が開けず外せない）: 直した
- reviewer 2（長すぎる名前で 500）: 直した（UTF-8 で 255 バイト以内に縮める）
- reviewer 3（`src/README.md`・`tests/README.md` が古い）: 直した。元から一覧に無い 3 つのテストは TODO-238
- reviewer 4（複製の分岐をテストが見ていない）: テストを足した。分岐は挙動を変えないので消した
- reviewer 5（同じ名前で付け直した画像のキャッシュ）: TODO-239
- reviewer 6（ゴミ箱の読めない行は版の数に入らない）: コードを読んで、そのとおりと確かめた。
  読めない行は復活できないので、直さない
- reviewer の好みの範囲（ファイルが無くても `removed:` のログを出す）: 実害が無いので直さない
- reviewer 再レビュー 7（`docs/data-format.md` に名前の扱いの変更が無い）: 直した
- verifier（ゴミ箱で全件が消えた）: 1 件だけ選んで確かめ直した（上記）。最初は「すべて選択」を押したと見られる

## 残ること

- `tests/README.md` に元から載っていないテストが 3 つある（TODO-238）
- 同じ名前で付け直した画像が、キャッシュで古いまま表示され続けないか（TODO-239）

## 分担の振り返り

- **各担当が見つけたもの:** reviewer は実際に値を渡して不具合 1 件と検討 3 件を見つけ、再レビューで
  文書の漏れも見つけた。verifier は全項目を実測し、ゴミ箱で全件が消えた件を挙げた（確かめ直すと
  問題は無かった）。implementer は文書の不足と、消しても挙動が変わらない分岐を見つけた
- **見込みとの食い違い:** 編成は見込みどおり。implementer が途中で止まって起動し直したぶん、
  implementer の量が増えた
- **次に同じ規模なら:** 同じ編成でよい。ただし、implementer への依頼には「途中で止まっても引き継げるよう、
  区切りごとに報告ファイルへ追記する」と書く。verifier に画面の操作を頼むときは、押す要素をセレクタで
  指定する（今回は「すべて選択」と同じクラスで取り違えた）。`model-check.md` の判定は「適切」の 1 件だけ
