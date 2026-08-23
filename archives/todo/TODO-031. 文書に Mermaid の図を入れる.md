# TODO-031. 文書に Mermaid の図を入れる

見込み: main = Opus 5 / effort medium、担当 = writer + verifier + wording
実施: main = Opus 5 / effort medium、担当 = writer + verifier + wording
消費: output 22,950 / cache_creation 263,322（main 35% + writer 30% + verifier 24% + wording 11%）

分担の理由と各担当の報告は
[archives/agents/TODO-031/](../agents/TODO-031/README.md) にある。

## きっかけ

TODO-030 で文書を 6 つに分けたが、どれも文章と箇条書きだけで、クラス同士の
関係やモジュールの依存は読まないと分からなかった。

**Mermaid を選んだ。** Markdown の中に ```mermaid のブロックを書くだけで
GitHub がそのまま図として表示する。ソースが数行で済み、コードが変わった
ときに直しやすい。SVG を直に書く手もあるが、座標を自分で決めることになり、
git の差分を読んでも意味が分からない。`docs/javascript-scroll.svg` は画面の
座標そのものを説明する図なので直書きのままでよく、今回のような関係を示す図
とは用途が違う。

## やったこと

候補は 5 つ挙げてあった。着手時に利用者と相談して **1〜4 を入れると決め、
5 は見送った**。

| # | 入れた場所 | 種類 | 何の図か |
| --- | --- | --- | --- |
| 1 | `src/README.md` データモデルの節 | `classDiagram` | `SchedDataEnt` / `SchedDataFile` / `SchedData` の積み上がりと、ハンドラが `SchedData` 経由でしか触らないこと |
| 2 | `src/README.md` Web ハンドラの節 | `classDiagram` | `RequestHandler` → `HandlerBase` → `MainHandler` / `EditHandler` の継承と、`WebServer` が割り当てる URL |
| 3 | `src/README.md`（新しい節） | `sequenceDiagram` | リクエスト 1 回の流れ |
| 4 | `docs/data-format.md` 変換の手順の節 | `graph TD` | 旧形式から JSON Lines への変換の分岐 |

**5（`tests/README.md` の `helpers.py` とテストの関係）は入れなかった。**
8 つのテストファイルが `helpers.py` を使うだけで関係が単純で、図にしても
文章より分かることが増えない。

3 は 1・2 と内容が重なるのを避けるため、**時間の流れでしか分からないこと**
に絞った。`Conf.cgi` を `HandlerBase.__init__()` のたびに読むこと、`post()`
が `get()` に委譲するだけであること、キャッシュに当たればファイルを読まない
ことの 3 つ。図の頭に「クラス同士の関係は上の図を見ること」と断ってある。

決めたとおり、**`style` / `classDef` で色を指定していない**（GitHub にも
Artifact にもダークテーマがあり、背景色を固定すると片方で読めなくなる）。
**既存の文章も消していない。**「なぜそうなっているか」は図では表せない。

## テスト

`verifier` が確かめた（[verifier-report.md](../agents/TODO-031/verifier-report.md)）。

- **4 つの図とも、実際に mermaid でパースして SVG まで作れた。** scratchpad
  に mermaid 11.17.0 を入れ、playwright の Chromium で `mermaid.parse()` と
  `mermaid.render()` の両方を通した。目視だけで済ませていない
  （`~/work/ytsched` には何も足していない）
- とくに疑っていた `WebServer ..> MainHandler : "/", url_prefix, url_prefix/`
  のダブルクォートとカンマ入りのラベル、`list~SchedDataEnt~` のジェネリック
  記法、`-_sdf_cache` の先頭アンダースコア、`<<tornado.web>>` のステレオ
  タイプは、いずれも問題なかった
- 図に出てくるクラス名・属性名・メソッド名・URL を `src/ytsched/*.py` と
  突き合わせ、**食い違いは無かった**。`HandlerBase.__init__()` が直接
  `load_conf()` を呼んでいること（`initialize()` や `get()` ではない）も
  確かめてある
- `mise run test` は 404 件 passed。lint・型チェックも通る

`wording` は前例の無い語を 11 語挙げた
（[wording-report.md](../agents/TODO-031/wording-report.md)）。図に関する語
（`ステレオタイプ` `ジェネリック記法` `エッジラベル` `クラス図` `graph TD`）が
まとまって初出になっているが、いずれも UML・Mermaid の一般的な用語で、
**直さないと判断した**。`LRU キャッシュ` は判断が要る語として挙がったが、
`src/README.md` の本文（「`OrderedDict` で LRU 的に…」）と
`docs/data-format.md`（「LRU のキャッシュ」）に前例があり、
`_sdf_cache` の実装も `pop()` して入れ直し `popitem(last=False)` で捨てる
本来の LRU なので、図のラベルとして正確。

**GitHub の画面そのものでは確かめていない。** mermaid 本体で描画まで通って
いるので、push したあとに実際の表示を見て、崩れていれば直す。

## 補足

`mermaid-cli`（`mmdc`）で SVG に書き出す案は採らなかった。依存が増えるわりに、
GitHub がそのまま表示できる以上の利点が無い。確認のために一時的に mermaid を
使うのは scratchpad の中だけで済ませてある。
