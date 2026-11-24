# TODO-240. 利用者向けの文書に、ファイルの添付の使い方を足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書）+ reviewer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（文書）+ reviewer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 43 | 7,749 | 24,616 | 1,583,190 | 59% |
| ver-240（verifier） | Sonnet 5.5 | medium | 44 | 8,976 | 42,156 | 770,822 | 30% |
| rev-240（reviewer） | Sonnet 5.5 | medium | 16 | 4,773 | 42,871 | 245,213 | 11% |
| 合計 |  |  | 103 | 21,498 | 109,643 | 2,599,225 | 計 2,730,469 |

- 項目を立てる前に動かした wording-240（Haiku 5.5 / low）は、集計範囲の外

## きっかけ

利用者から「最新の仕様に合わせてドキュメントを修正して」と頼まれた。1.3.0 以降の
機能を文書と突き合わせたところ、TODO-237 の添付ファイルだけが `docs/UsersGuide.md` に
無かった（Ctrl+Enter、ホームボタンの点滅、`notify` の新しいオプションは載っていた）。

## やったこと

- `docs/UsersGuide.md`: 1 節に、詳細を開いたときの画像の表示・リンク・「添付 N 件」を足した。
  3.1 節「添付ファイル」を新しく作り、添付・外す・同名の番号付け・複製で付かないこと・
  大きさの上限を書いた。8 節に、ゴミ箱と添付ファイルの関係を足した。目次に 3.1 を足した
- `docs/Install.md`: 5 節に、`--size-limit`（バイト数、`ExecStart` に足す）とリバースプロキシの
  上限（nginx の `client_max_body_size`）、`attachments/` をバックアップに含めることを足した

## 確かめたこと

- reviewer が、書いた挙動を実装と 1 件ずつ照らし、食い違いは無かった
- verifier が、一時ディレクトリの webapp を Playwright（412px）で操作し、6 項目すべて文書どおりだった
  （画像は `inline`、ほかは `Content-Disposition: attachment`）

担当の指摘との対応（`archives/agents/TODO-240/`）:

- wording の言い換え案: 直した。「無駄を省く工夫」は todo-workflow skill の書式なので残した
- reviewer 検討 1（「版」が利用者に通じない）: 直した（「編集前の内容」と言い換え）
- reviewer 確信度低 1（「閉じているあいだ」と限ると開くと消えるように読める）: 直した
- reviewer 確信度低 2（`--size-limit` の指定先が無い）: 直した（`ExecStart` と単位を書いた）

## 分担の振り返り

- wording は言い回しを 5 件、reviewer は利用者に通じにくい語と誤読されうる書き方を 3 件見つけた。
  verifier は食い違いを見つけなかったが、ダウンロードになることを応答ヘッダで裏付けた
- 見込みどおりで、食い違いは無い
- 次に同じ規模の文書の追記なら、verifier の 6 項目は reviewer のコード照合とほぼ重なっていたので、
  ゴミ箱の判定のように読むだけでは分かりにくいものだけに絞り、3 項目程度にする
