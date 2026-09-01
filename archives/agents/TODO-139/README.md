# TODO-139 の分担

項目は
[TODO-139. ゴミ箱から消す UI（1 件ずつと、全部）](../../todo/TODO-139.%20ゴミ箱から消す%20UI（1%20件ずつと、全部）.md)。

## 誰に何を担当させたか

| 担当 | 依頼書 | 報告 |
|---|---|---|
| implementer | [implementer-task.md](implementer-task.md) | [implementer-report.md](implementer-report.md) |
| verifier | （main がメッセージで依頼） | [verifier-report.md](verifier-report.md) |
| reviewer | （main がメッセージで依頼） | [reviewer-report.md](reviewer-report.md) |
| writer | （main がメッセージで依頼） | [writer-report.md](writer-report.md) |

## その分担にした理由

- **implementer を分けた。** Python 2 ファイル・テンプレート・CSS・
  テスト 2 ファイルにまたがり、実装とテストがまとまって要る規模だった
- **reviewer を入れた。** 消したら戻せない操作を足す項目で、削除の分岐が
  増える。`CLAUDE.md` の「挙動や分岐が変わる項目には入れる」に当たる
- **verifier を分けた。** 「1 件だけ消えて他が巻き添えにならない」は、
  実際にファイルを作って消してみないと分からない。試せる手順があるので
  main では済ませない
- **writer に `src/README.md` を任せた。** 実装と同時に走らせられ、
  他の担当とファイルがぶつからないため

## この項目で分かったこと

- **verifier と reviewer が、独立に同じ 1 点を挙げた。**
  `tempfile.mkstemp()` で作った一時ファイルを差し替えるため、
  `trash.jsonl` のパーミッションが 0644 から 0600 に変わる件。依頼書で
  「パーミッションを見てほしい」と名指ししたのは verifier だけだったが、
  reviewer も自分で実測して同じ結論に達した。**どちらもテストを通す
  だけでは出てこない指摘**で、pytest は 578 件とも通っていた
- **画面を撮るまで、表示の崩れは誰も見つけられなかった。** pytest は
  579 件とも通り、verifier は curl で HTML を取って中身も見ていたが、
  スマホ幅で撮った画像を main が見るまで、日付の折り返し・ボタンの
  縦並び・1 件目がヘッダに隠れることは分からなかった。**UI を足す項目
  では、担当にスクリーンショットまで撮らせる**（実際、直しの依頼では
  implementer に自分で撮って確かめさせた）
- **依頼書の指示が、プロジェクトの決まりとぶつかることがある。**
  main は `onsubmit="return confirm(...)"` と書いたが、TODO-108 で
  インラインイベントハンドラを禁止しているため、そのままではテストが
  落ちる。implementer が `data-confirm` 属性 + `trash-page.js` に
  読み替えて、範囲外のファイル追加として報告してきた。依頼書を書く前に
  既存のテストが何を禁じているかを見ておくべきだった
