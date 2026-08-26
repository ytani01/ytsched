# TODO-058 reviewer への依頼

## 何をした項目か

**左端の縦ゲージをやめて、週バーの下に横向きのゲージの帯を 1 行出す
ようにした。** 概要は
[request-verifier.md](request-verifier.md) の「何をした項目か」と、
[implementer-report.md](implementer-report.md) を読むこと。

`git diff` で変更を見て、正しさ・設計・プロジェクトの決まりからの
逸脱を報告する。

## 特に見てほしいところ

1. **Python の `days2x_percent()` と JavaScript の `days2xPercent()`
   が、本当に同じ値を出すか。** 定数（`0.6`、`365.25`、30 年）と
   頭打ちの扱いが片方だけずれていないか。**ずれるとラベルと針が
   食い違い、見ただけでは気づけない**
2. **検索モードで `gage_r` が存在しない経路。** `dispGage()` /
   `setGagePosition()` / `placeGageWithoutTransition()` の
   どこかで `null` を触っていないか
3. **`sessionStorage` を使った補間（TODO-049）が壊れていないか。**
   前の週の位置へ `transition` 無しで置いてから今の週へ動かす手順が、
   `bottom` から `left` に変わっても成り立っているか。
   `.my-gage-r-no-transition` の詳細度の話（TODO-049 reviewer 指摘 2）
   もそのまま効いているか
4. **消し残し。** `days2y_offset` / `y_offset` / `gage_r_base` /
   `my-osd-base` / `my-gage-text` / `centerY` が、どこかに残って
   いないか。逆に、**まだ使われているものを消していないか**
5. `main` の `padding-left` を詰めたことで、他の見た目に影響が
   出ないか
6. コメントが「なぜそうしたか」を書いているか（このリポジトリの
   書き方に合っているか）

## 報告

`archives/agents/TODO-058/reviewer-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。
**コードは直さない。** 見つけたことを報告するところまで。
