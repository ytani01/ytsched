# TODO-031 wording 報告

対象は次の 7 ファイル（`git status --porcelain=v1 -- '*.md'` で確認。
`TODO.md`・`src/README.md`・`docs/data-format.md` は変更、残り 4 つは
未追跡の新規ファイル）。

- `TODO.md`
- `src/README.md`
- `docs/data-format.md`
- `archives/todo/TODO-031. 文書に Mermaid の図を入れる.md`
- `archives/agents/TODO-031/README.md`
- `archives/agents/TODO-031/writer-report.md`
- `archives/agents/TODO-031/verifier-report.md`

`TODO.md` の差分は TODO-031 の節の削除とリンクの追加のみで、新しい語は
無かった。`archives/agents/TODO-031/README.md` も見立てが割れる語は
見当たらなかった。

以下、前例の件数が少ない順（0 件のものはまとめて先に）。

## 前例なし（0 件）

- **`graph TD`**（`docs/data-format.md` の Mermaid ブロック 1 箇所）。
  `git grep -cF "graph TD" HEAD -- '*.md'` は 0 件（`graph` 単体は
  `TODO.md` に前例あり）。見立て: Mermaid の図の種類を表す構文そのもの
  で、一般に通用する語。図のソース内なので指摘は参考まで

- **`ステレオタイプ`**（`verifier-report.md` 24 行 `<<tornado.web>>` の
  ステレオタイプ、`archives/todo/TODO-031...md` 57 行）。0 件。
  見立て: UML/Mermaid の一般的な用語（クラスに付く `<<...>>` 表記）。
  一般に通用する

- **`ジェネリック記法`**（`verifier-report.md` 21 行 `list~SchedDataEnt~`
  のジェネリック記法、`archives/todo/TODO-031...md` 56〜57 行）。0 件。
  見立て: Mermaid の classDiagram でジェネリック型を表す記法を指す説明的
  な言い回し。Mermaid のドキュメントにも近い言い方があり、通用しそう

- **`先頭アンダースコア`**（`verifier-report.md` 22 行 `-_sdf_cache` の
  先頭アンダースコア、`archives/todo/TODO-031...md` 57 行）。0 件。
  見立て: 普通の日本語の組み合わせで、専門用語というほどでもない。
  問題なさそう

- **`エッジラベル`**（`verifier-report.md` 26 行 ダブルクォート・カンマ
  入りエッジラベル）。0 件（`ラベル` 単体は他所に前例があるかもしれない
  が確認していない）。見立て: グラフ理論・図表ツールで一般に通用する語
  （辺に付くラベル）。この文脈では自然

- **`LRU キャッシュ`**（`src/README.md` の classDiagram、
  `SchedData o-- SchedDataFile : LRU キャッシュ` のエッジラベル）。0 件。
  見立て: 一般的なキャッシュアルゴリズムの名称。ただし本文の説明文には
  「LRU」という語自体が今まで出てきていなかったのか要確認（`SchedData`
  の説明文には元々 `OrderedDict` を使ったキャッシュ、という記述がある
  はずで、`LRU` という呼び方をここで初めて当てはめている可能性がある）

- **`経由してアクセス`**（`src/README.md` の classDiagram、
  `MainHandler ..> SchedData : 経由してアクセス` のエッジラベル）。0 件。
  見立て: 普通の言い回し。図のラベルとして短く言い換えただけで、造語
  というほどではなさそう

- **`継承関係`**（`src/README.md` 94 行「継承関係と、`WebServer` が
  どの URL にどちらを割り当てているかを図にすると次のようになる」）。
  0 件。見立て: 一般的なプログラミング用語（クラスの継承関係）。
  通用する

- **`クラス図`**（`src/README.md` 154 行「クラス図だけでは分からない
  『時間の流れ』を示すためのものなので」）。0 件。
  見立て: UML の一般用語。通用する

- **`時間の流れ`**（`src/README.md` 154 行、同上の引用符内。TODO.md の
  旧記述にも近い言い回しがあったが「流れ」単体で、「時間の流れ」という
  組み合わせでは前例なし）。見立て: 普通の日本語で、専門用語ではない

- **`キャッシュに当たる`**（`src/README.md` 176 行 sequenceDiagram の
  `else キャッシュに当たる`）。0 件（`食い違いが起きていた` のような
  「当たる」を含む言い回しは他にあるかもしれないが、「キャッシュに
  当たる」という組み合わせでは前例なし）。見立て: 「キャッシュヒット」
  の意味で一般に通じる普通の言い回し。問題なさそう

## 前例あり（参考）

- `classDiagram` / `sequenceDiagram`: `TODO.md`（旧 TODO-031 節、今回の
  差分で削除される側）と `archives/agents/TODO-030/wording-report.md` に
  前例があり（4 件・2 件）、造語ではない
- `分岐` `積み上がり` `変換の手順` `移行の手順` `委譲` `食い違い`
  `素のテキスト` `気づいたこと` `書けなかったところ`: いずれも
  リポジトリ内に複数の前例があり、問題なし

## 判断できないもの

- `LRU キャッシュ` は上に書いたとおり、`LRU` という呼称そのものが本文の
  説明に既にあったかどうかを突き合わせていない。前例カウントは 0 件
  だが、一般語かリポジトリ固有の言い換えかは main の判断に委ねる

読んだファイルは上記 7 つ全部。前例の無い語は 11 語
（`graph TD` `ステレオタイプ` `ジェネリック記法` `先頭アンダースコア`
`エッジラベル` `LRU キャッシュ` `経由してアクセス` `継承関係` `クラス図`
`時間の流れ` `キャッシュに当たる`）。
