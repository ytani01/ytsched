# TODO-073. クレジット表示を「(c) 2026 ytani01」に統一する

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier + wording |
| 実施 | Opus 5 / effort high | main + verifier + wording |
| 消費 | output 7,734 / cache_creation 63,872 / 概算 $1.1 |
|      | main 80% + verifier 12% + wording 8%（料金の割合） |

## きっかけ

Web 画面のフッターが `(c) 2020 Yoichi Tanibayashi` のままだった。年を
2026 に、名前をハンドル名の `ytani01` に変える。

フッターだけ直すと、ソースの先頭コメントや `LICENSE` と食い違う。範囲を
利用者に確認したうえで、まとめて揃えた。年は範囲（2020-2026）にせず
`2026` 固定にする。

## やったこと

`Yoichi Tanibayashi` を含む 28 ファイルを一括で置換した。

| 場所 | 変更 |
|---|---|
| `main.html` のフッター | `(c) 2020 {{ author }}` → `(c) 2026 {{ author }}` |
| `__author__`・`author=`・テストの期待値 | `"Yoichi Tanibayashi"` → `"ytani01"` |
| `src` / `tests` / `tools` の先頭コメント | `(c) 20xx Yoichi Tanibayashi` → `(c) 2026 ytani01` |
| `LICENSE` | `Copyright (c) 2021-2026 Yoichi Tanibayashi` → `Copyright (c) 2026 ytani01` |
| `pyproject.toml` | 著者名のみ `ytani01`。メールアドレスは変えない |

先頭コメントの年は `2020`・`2021`・`2025`・`2026`・年なしが混在して
いたが、すべて `2026` に揃えた。

`docs/licenses/bootstrap-LICENSE` と `my.css` にある Bootstrap の
著作権表示は他者のものなので触っていない。

### 一括置換が説明文まで書き換えた

最初に走らせた正規表現は、`TODO.md` の説明文（「フッターが `(c) 2020
Yoichi Tanibayashi` のままになっている」）まで置換してしまった。除外の
指定が効いていなかった（`grep -rl` の出力に `./` が付かず、
`^\./TODO\.md$` にマッチしなかった）。気づいて戻した。

一括置換では、**直す対象を書いた文書そのものが置換の巻き添えになる**。

## テスト

新しくは書いていない。文字列の置換なので、既存のテストが期待値ごと
追随すれば足りる。

- `tests/test_handler.py` — `handler._author == "ytani01"`
- `tests/helpers.py` — テスト用アプリの `author="ytani01"`

verifier の報告は
[archives/agents/TODO-073/verifier-report.md](../agents/TODO-073/verifier-report.md)。
fmt・typecheck・lint・455 件のテストが通り、実アプリを起動して
フッターに `(c) 2026 <strong>ytani01</strong>` が出ることまで確認した。
差分 28 ファイルを全件見て、意図しない置換は無し。指摘は無かった。

分担の理由は
[archives/agents/TODO-073/README.md](../agents/TODO-073/README.md)。
