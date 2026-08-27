# TODA-078 wording 報告

（ファイル名は依頼どおり `wording-report.md`）

## 対象ファイル

- `archives/todo/TODO-078. ゲージの計算を 1 か所にする.md`
- `archives/agents/TODO-078/README.md`
- `archives/agents/TODO-078/implementer-task.md`
- `archives/agents/TODO-078/implementer-report.md`
- `archives/agents/TODO-078/verifier-task.md`
- `archives/agents/TODO-078/verifier-report.md`
- `archives/agents/TODO-078/reviewer-task.md`
- `archives/agents/TODO-078/reviewer-report.md`
- `TODO.md`（差分のみ）
- `tests/README.md`（差分のみ）

## 前例の無い語

### 二重持ち

- 出てくる箇所:
  - `implementer-report.md`: 「Python 側との**二重持ち**を説明していた
    コメントを、JS 側だけになった旨に書き直し」
  - `reviewer-report.md`: 「以前は `main_handler.py` にもあったが、
    **二重持ち**をやめて JavaScript 側だけに寄せた (TODO-078)」
- `git grep` の件数: 前例なし（`git grep -cF 二重持ち HEAD -- '*.md'` は
  何も出さずステータス 1）
- 見立て: 「二重に持つ」という言い回し自体は `TODO-078.md` 本文
  （「二重に持つこと自体は解消しない」）や `docs/design-review.md` に
  既にあるが、名詞化した「二重持ち」の形は今回が初出。一般にも通じそうな
  自然な日本語で、造語というほどではないと見るが、判断は main に委ねる。

### 描き損ねる

- 出てくる箇所: `verifier-task.md`「サーバが埋めるのをやめたので、
  JavaScript が**描き損ねる**と空になる。」
- `git grep` の件数: 前例なし
- 見立て: 「〜し損ねる」は日常的な言い回しで、このリポジトリだけの
  言い換えには見えない。専門用語というより普通の日本語。

### フルリロード

- 出てくる箇所: `reviewer-report.md`「ページ遷移は `doGet()`/`doPost()`
  とも `location.href` 変更かフォーム送信による**フルリロード**で、
  bfcache 復元時は…」
- `git grep` の件数: 前例なし
- 見立て: Web 開発では一般に通用する語（"full reload" のカタカナ）。
  このリポジトリでは初出というだけで、造語ではなさそう。

## 前例はあったが確認した語（参考）

以下は候補に挙がったが、`HEAD` の時点で既に使われていたため外した。
- 突き合わせ（80 件）、目盛り（82 件）、帯（72 件）、経路（235 件）、
  分岐（165 件）、キャプチャ（96 件）、実測（123 件）、確信度の高い
  （36 件、reviewer 定義由来）、スピナー（26 件）、bfcache（16 件）、
  pageshow（14 件）、位置合わせ（14 件）、早期 return（1 件、TODO-049）、
  張り付く（2 件、TODO-059）、揃え続け（2 件、`TODO.md`/
  `docs/design-review.md` に既存）、旧版・新版（それぞれ 22・19 件）

## まとめ

- 読んだファイル: 上記「対象ファイル」の 10 件
- 前例の無い語: **3 語**（二重持ち／描き損ねる／フルリロード）。
  いずれも一般的な日本語・カタカナ語に見え、このリポジトリ特有の
  言い換え（TODO-021 の「足場」のような造語）には見えない、というのが
  こちらの見立て。決めるのは main。
