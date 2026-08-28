# wording 報告 (TODO-104)

## 前例の無い語

前例の件数が少ない順（すべて 0 件＝前例なし）。

### 当たり判定

- 出てくる箇所:
  - `archives/todo/TODO-104. 月間ミニカレンダーの表示を切り替えるスイッチ.md:41`
    「`padding` で当たり判定を広げた。」
  - `archives/agents/TODO-104/reviewer-report.md:65`
    「スイッチの当たり判定はアイコンそのまま…」
  - `archives/agents/TODO-104/verifier-report.md:67`
    「スイッチの当たり判定（`bounding_box()`）は…」
- `git grep -cF 当たり判定 HEAD -- '*.md'`: 前例なし
- 見立て: ゲーム開発・UI 実装で一般に通用する語（「押せる範囲」の意味で
  広く使われる）。このリポジトリでは初出。造語ではなく一般用語だと思う。

### 自由関数

- 出てくる箇所: `archives/agents/TODO-104/implementer-report.md:52`
  「`handler_util.py` の自由関数にした（`self` を使わず…）」
- `git grep -cF 自由関数 HEAD -- '*.md'`: 前例なし
- 見立て: C++ などで使われる一般的なプログラミング用語（クラスに属さない
  関数）。Python の文脈でも通じるが、この用語をあえて使わず「モジュール
  レベルの関数」「トップレベル関数」と書く選択肢もある。一般に通用する
  かはやや微妙で、判断できない。

### バリアント

- 出てくる箇所: `archives/agents/TODO-104/implementer-report.md:58-59`
  「対応する既存の小さいバリアントが無く、最小のクラスがこれだった…」
- `git grep -cF バリアント HEAD -- '*.md'`: 前例なし
- 見立て: 一般的なカタカナ語（variant）。CSS のサイズ違いクラスを指して
  使っており、通じる範囲の語だと思う。

### 変換失敗（時）

- 出てくる箇所: `archives/agents/TODO-104/reviewer-report.md:9`
  「`update_conf_arg()` / `convert_value()` の実装まで遡って…値・変換
  失敗時の扱い…」
- `git grep -cF 変換失敗 HEAD -- '*.md'`: 前例なし
- 見立て: 普通の日本語の組み合わせ（変換＋失敗）で、このリポジトリだけの
  言い換えには見えない。問題ないと思う。

### 月始まり

- 出てくる箇所: `archives/agents/TODO-104/verifier-report.md:41`
  「カレンダーの曜日は月始まり（月火水木金土日）で、日曜は一番右の列」
- `git grep -cF 月始まり HEAD -- '*.md'`: 前例なし
- 見立て: カレンダー UI で「月曜始まり」の意味で使われる一般的な言い方
  （「日曜始まり」の対）。一般に通用すると思う。

### 厚み（が違う）

- 出てくる箇所: `archives/agents/TODO-104/reviewer-report.md:64`
  「この場合分けだけ厚みが違う」
- `git grep -cF 厚み HEAD -- '*.md'`: 前例なし
- 見立て: テストケースの「網羅の濃さ」を比喩的に「厚み」と呼んでいる。
  一般的な比喩ではあるが、テスト観点の呼び名としてこの語を定着させて
  よいかは判断が要る。TODO-021 の「足場」（characterization test を
  独自に呼んだ例）と似た形の可能性があるので、念のため挙げる。

### 触感

- 出てくる箇所: `archives/agents/TODO-104/reviewer-report.md:69-70`
  「押しにくく感じる可能性はある（見た目・触感の話で、動作の正しさとは
  別の観点）」
- `git grep -cF 触感 HEAD -- '*.md'`: 前例なし
- 見立て: 一般的な日本語（手触り・触った感じ）。UI のタップしやすさを
  指す語として自然で、造語には見えない。

## 前例はあるが件数が少なく参考に挙げた語

- **スイッチ**: 前例 11 件（既に使われている一般語）
- **反転**: 前例 2 件
- **焦った**: 前例 1 件（verifier-report.md「焦ったが、実装の不具合ではない」。
  口語的だが日記調の報告文なので問題ないと思う）
- **押しやすい**: 前例 1 件

これらは前例があるため「前例の無い語」には含めていない。

## 読んだファイル

- `TODO.md`（差分のみ）
- `archives/todo/TODO-104. 月間ミニカレンダーの表示を切り替えるスイッチ.md`
- `archives/agents/TODO-104/README.md`
- `archives/agents/TODO-104/implementer-order.md`
- `archives/agents/TODO-104/implementer-report.md`
- `archives/agents/TODO-104/verifier-report.md`
- `archives/agents/TODO-104/reviewer-report.md`

## 前例の無い語数

7 語（当たり判定、自由関数、バリアント、変換失敗、月始まり、厚み、触感）。
