# TODO-057 reviewer への依頼

TODO-057「スワイプで隣の週を指に追従させる」の変更を見る。
**コードは直さない。** 見つけたことは報告に書き、直すかどうかは main が
決める。

読む順:

1. `TODO.md` の `## TODO-057. スワイプで隣の週を指に追従させる`（決めごと）
2. `archives/agents/TODO-057/request-implementer.md`（依頼書）
3. `archives/agents/TODO-057/implementer-report.md`（実装の報告）

変更は**まだコミットしていない**。`git diff` で見られる。

## 見てほしいこと

- **決めごとどおりに作られているか。** 違っていたら、その理由が
  実装の報告に書かれているか
- **正しさ。** とくに、状態を持つ変数（`swipeStart`・`swipeDragging`）と
  クラス（`my-week-wrap-dragging`・`my-week-wrap-sliding`）の付け外しが、
  途中で割り込まれたときに矛盾しないか。指が離れないまま次の指が触れた、
  `touchcancel` が来た、送りの途中でもう一度スワイプした、といった順序
- **`transitionend` が来なかったときの逃げ道**が効くか。
  `slideWeekWrap()` はタイマーでも進むようにしてあるが、二重に
  `on_done()` が呼ばれないか
- **`getElementById('date-...')` が隣の週を拾わないこと。** これが
  この項目でいちばん外しやすいところで、外すと TODO-049 の退行
  （URL だけ変わって画面が変わらない）と同じ形になる
- **`touchmove` を `{passive: false}` にした影響。** 縦スクロールの
  邪魔になっていないか、`preventDefault()` を呼ぶ条件が広すぎないか
- **サーバ側で `load_sched()` を 3 回呼ぶようにした影響。**
  検索モードでの分岐、`todo_sde`/`todo_today_sde` の使い回し、
  既存の `sched`・`date_from`・`date_to` との食い違い
- **プロジェクトの決まりからの逸脱。** `CLAUDE.md`・`src/README.md` の
  約束（ログは `mylog.py`、`base.html` の autoescape、など）

## 気にしている 2 点

main が気になっているところ。見立てを聞かせてほしい。

- **`slideWeekWrap()` の `finish()` が、`transform` を空にしてから
  `on_done()`（`doGet()`）を呼ぶ。** `doGet()` は `location.href` を
  変えるだけで、新しいページが来るまで今のページが映っている。
  隣の週まで滑らせた直後に元の週へ戻って見えないか
- **検索モードでもスワイプ・◀▶・キーの送りが同じアニメーションを
  通る。** 隣に週が無いので、滑らせている間、画面の端に白い余白が
  見えるはず。分岐を足して即 `doGet()` にすべきか、このままでよいか

## 報告

`archives/agents/TODO-057/reviewer-report.md` に書く。
指摘は**根拠（どのファイルの何行目が、どういう場合にどうなるか）**を
添えること。

**返事は 5 行以内**（終わったか・報告ファイルのパス・判断が要る点）。
報告の中身を返事に貼らないこと。
