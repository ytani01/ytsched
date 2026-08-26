# TODO-075 wording 報告（直したあと）

対象: `README.md` / `src/README.md` / `docs/Developer.md` /
`docs/data-format.md` / `TODO.md`（変更差分）、
`archives/todo/TODO-075. 文書と実装のズレを直す.md`（新規）、
`archives/agents/TODO-075/README.md`（新規）、
`archives/agents/TODO-075/verifier-report.md`（新規、verifier 作成）。

`README.md` / `src/README.md` / `docs/Developer.md` / `docs/data-format.md` /
`TODO.md` は `git diff` の差分のみを見た（前後の文脈込み）。新規の 3 ファイル
は全文を読んだ。

前例の有無は `git grep -cF <語> HEAD -- '*.md'` で確認した（基準は
このコミットが入る前の `HEAD`）。

## 前例なしの語

### 1. 直しそこね

- 箇所: `archives/todo/TODO-075. 文書と実装のズレを直す.md`
  「あわせて**直しそこね**が無いかも見させた」、
  `archives/agents/TODO-075/verifier-report.md` の見出し
  「## **直しそこねた**ズレの探索」
- `git grep` の件数: 前例なし
- 見立て: 「直し忘れ」「修正漏れ」のような一般語で言えるところを、
  この文書だけの言い回しにしている可能性がある。ただし「〜そこねる」
  自体はふつうの日本語の言い回しで、造語というより単なる言い換えに
  近い。判断は main に委ねる

### 2. 置き去り

- 箇所: `archives/todo/TODO-075. 文書と実装のズレを直す.md`
  「どれも TODO-048 以降の変更（週表示・ゲージ・アイコン・データ形式）
  で**置き去りになった**もので、直す先ははっきりしている」
- `git grep` の件数: 前例なし
- 見立て: 一般に通用する言い回し（「取り残された」の意味）で、
  このリポジトリだけの言い換えには見えない。初出というだけで、
  問題は無さそうに見える

### 3. IntersectionObserver

- 箇所: `archives/agents/TODO-075/verifier-report.md` の項目 2
  「`my.js` に `IntersectionObserver` や スクロールでの追加読み込みは
  無く」
- `git grep` の件数: 前例なし
- 見立て: 造語ではなく Web の標準 API 名（固有名詞）。このリポジトリの
  文書での初出というだけで、専門用語をそのまま書く分には問題ないはず
  （`CLAUDE.md` の「専門用語は無理に和訳しない」に沿っている）

## 前例ありで、造語の疑いは薄いが確認した語

以下は候補に挙げたが、前例が複数あり、このコミットで初めて作られた
語ではないと判断した（参考として残す）。

- 突き合わせ・突き合わせる（73 件）
- 洗い出し（2 件。`archives/agents/TODO-035` などで既出）
- 逆算（22 件。`archives/agents/TODO-043` などで既出）
- 残存（9 件）
- 探索（既出。`archives/agents/TODO-035` など）
- 想定どおり（既出多数）
- 文言（既出多数）
- 帰属表示・線画・土台・描き起こし・潰しが効く・キャッシング・見送り・
  同梱・退避・思い込み・ズレ・食い違い・分担・経緯・正規化・寄せる
  （いずれも `README.md` / `docs/data-format.md` の**既存の未変更部分**
  にあり、この差分より前から使われている）

`README.md` / `src/README.md` / `docs/Developer.md` /
`docs/data-format.md` / `TODO.md` の**変更された行そのもの**には、
前例の無い語は見当たらなかった（差分は数値・語句の更新と、既に他の
文書で使われている言い回しの書き換えが中心）。

## 読んだファイル

- `README.md`（差分）
- `src/README.md`（差分）
- `docs/Developer.md`（差分）
- `docs/data-format.md`（差分）
- `TODO.md`（差分）
- `archives/todo/TODO-075. 文書と実装のズレを直す.md`（全文）
- `archives/agents/TODO-075/README.md`（全文）
- `archives/agents/TODO-075/verifier-report.md`（全文）

## 前例の無い語数

3 語（うち 2 語は一般語・固有名詞で、造語の疑いは薄いと見立てた）。
