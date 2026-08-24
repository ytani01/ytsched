# TODO-043 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier + wording |

## なぜこの分担にしたか

- **実装は main が行った。** 変えたのは `main.html` の 12 行と `my.css` の
  1 ブロックで、何をどう書き換えるかは項目を立てる段階で決まっていた。
  implementer を立てても、依頼書を書く手間のほうが大きい
- **図形の大きさは、フォントから実測して決めた。** 「見た目を変えない」の
  拠り所が要るので、`fa-solid-900.woff2` から fontTools でグリフの輪郭を
  取り出し、`fa-caret-right` が 194x298 units、`fa-grip-lines` が
  448x192 units（`unitsPerEm = 512`）であることを確かめてから SVG の
  寸法を決めた。`uv run --no-project --with fonttools` で一時的に使えるので、
  プロジェクトの依存は増えていない
- **確認は verifier に分けた。** 見た目を変えないことが条件の項目なので、
  画面で見ないと分からない。とくに針と基準線の重なり方は、TODO-042 で
  利用者が実機で見て `centerY - 9` と決めた部分で、今回そこを
  「図形の中心どうしを揃える」に変えている
- **`.md` が入るので wording を立てた。** 項目を立てるコミットで 1 回
  （基準線も SVG にする変更のあと、追加で 1 回）、済ませるコミットでもう 1 回
- **runner に lint とテストを走らせた。** テンプレートと CSS しか触って
  いないが、`main.html` の中の JavaScript が壊れていないことは別の担当に
  確かめさせた

## reviewer を入れなかった理由

`~/.claude/CLAUDE.md` では「挙動や分岐が変わる項目には入れる」となって
いる。今回は**描き方を入れ替えただけで、分岐も呼び出しの順序も増えて
いない**。`elGageRBase.style.bottom` から `- 9` が消えたのが唯一の
ロジックの変更で、それも定数を戻しただけ。

## 報告

| 担当 | 何を任せたか | 依頼書 / 報告 |
|---|---|---|
| main | グリフの実測、`main.html`・`my.css` の書き換え | — |
| verifier | 見た目が変わっていないことの確認 | [依頼](verifier-request.md) / [報告](verifier-report.md) |
| wording | コミットに入る `.md` から前例の無い語を挙げる | [依頼](wording-request.md) / [報告](wording-report.md) |
| runner | lint・テスト | [報告](runner-report.md) |

TODO 項目そのものは
[archives/todo/TODO-043. ゲージの針と基準線を、アイコンフォントでなく図形で描く.md](../../todo/TODO-043.%20ゲージの針と基準線を、アイコンフォントでなく図形で描く.md)。
