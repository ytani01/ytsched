# TODO-074 wording 報告

対象: TODO.md の差分（`git diff TODO.md`、TODO-074 を立てる部分）。
このコミットに入る `.md` は `TODO.md` の 1 ファイルのみ。

## 前例の無い語

### xPercent2days

- 出てくる箇所: `TODO.md` の TODO-074 節、1 個目のチェック項目
  「`days2xPercent()` の逆算（`xPercent2days()`）を `my.js` に足す」
- `git grep -cF xPercent2days HEAD -- '*.md'`: 前例なし（0 件、`HEAD` 時点）
- 見立て: これから作る関数名そのものなので、前例が無いのは当然。
  対になる `days2xPercent` は TODO-058／TODO-059 の archives に既出
  （`git grep -cF days2xPercent HEAD -- '*.md'` で TODO-058 の archive 1 件、
  TODO-059 の archive 1 件、`archives/agents/` にも複数件）。命名の対称性
  から自然に導ける名前で、造語というより実装対象の識別子。問題ないと見る

## 前例があった語（参考。造語ではない）

念のため、他に呼び名になりそうな語も `HEAD` に対して確認したが、
いずれも TODO-042／043／049／054〜072 などの既存 archives・
`src/README.md`・`tests/README.md` に前例があった。

逆算、頭打ち、帯（`.my-gage-bar` を含む）、針、目盛り、週送り、
スワイプ、タップ、ゲージ、月曜、読み直す、ラベル、週バー、ジャンプ、
追従、`days2xPercent`、`my-gage-bar`、針の位置。

## 読んだファイル

- `TODO.md`（差分部分。このコミットに入る唯一の `.md`）

## まとめ

前例の無い語: **1 語**（`xPercent2days`）。これは新しく作る関数名を
文中で言及したものであり、一般的な意味での造語（呼び名の言い換え）
には当たらないと考えるが、判断は main に委ねる。
