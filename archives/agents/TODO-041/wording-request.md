# TODO-041 wording への依頼

## この項目でやったこと

スクロールで追加読み込みが起きるたびに画面が下から上へ流れる、という
症状を直した。原因は TODO-040 で入れた Bootstrap 5.3.8 の
`:root{scroll-behavior:smooth}` で、`scrollTo()` に渡していた `"auto"` が
smooth 扱いになっていた。`"instant"` に変えた（`main.html` の 1 か所）。

## 見てほしいファイル

このコミットに入る `.md` は次の 6 つ。**依頼書と報告ファイルも含める。**

```
TODO.md
archives/todo/TODO-041. 追加読み込みのたびに自動スクロールが起きるのを直す.md
archives/agents/TODO-041/README.md
archives/agents/TODO-041/verifier-request.md
archives/agents/TODO-041/verifier-report.md
archives/agents/TODO-041/wording-request.md   （このファイル）
```

`TODO.md` は項目を archives へ移した差分だけ。

## 決まりごと

- **前例なし ＝ 造語ではない。** 一般に通用する専門用語でも、このリポジトリ
  では初出になる。候補を挙げて見立てを添えるところまでで、**決めるのは main**
- 文書は直さないこと
- 報告は `archives/agents/TODO-041/wording-report.md` に書く。
  返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内
