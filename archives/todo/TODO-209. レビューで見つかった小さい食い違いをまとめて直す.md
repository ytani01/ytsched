# TODO-209. レビューで見つかった小さい食い違いをまとめて直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Sonnet 5.5 / effort 記載なし | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Sonnet 5.5 | 記載なし | 40 | 7,870 | 60,131 | 1,153,037 | 48% |
| implementer | Sonnet 5.5 | medium | 16 | 134 | 36,340 | 199,700 | 9% |
| reviewer | Opus 5.5 | high | 44 | 3,024 | 55,084 | 841,042 | 35% |
| verifier | Sonnet 5.5 | medium | 16 | 200 | 51,497 | 138,050 | 7% |
| 合計 |  |  | 116 | 11,228 | 203,052 | 2,331,829 | 計 2,546,225 |

- main は見込みが Opus 5.5 だったが、着手したセッションのモデルは Sonnet 5.5
  だった（`/model` の切り替えが無かった）。effort は記録に残らない
- 集計は `--since '2026-09-30 07:40:00'`（立てたコミットから着手まで
  別の項目が挟まっているため）
- 担当のモデル・effort は定義どおり。上書きはしていない

## きっかけ

TODO-204 の周辺のレビューで見つかった、独立した小さい食い違い 5 件。

## やったこと

- `ConfFile.DEF_CONF["ToDo_Days"]` を `"1y"` から `"365"` にした
  （`"1y"` は `int()` で読めず、リクエストのたびに WARNING が出ていた）。
  `tests/test_handler.py` と `tests/test_web.py` の期待値も直した。
  既にある `conf.json` は書き換えない
- `holiday.py` の `urlopen()` に `timeout=30` を付けた
- 使われていない `SchedData.sdf_has_sde()` と、そのテスト 3 件を消した
- `base.html` の `{% autoescape None %}` を消した
- `src/README.md`（CLI 5 つ、`load_month_cal()` の判定、autoescape の節）と
  `docs/data-format.md`（autoescape の記述）を実装に合わせた

## 確かめたこと

- `mise run fmt` / `typecheck` / `lint` / `test`（712 passed）が通る
- 一時ディレクトリで起動し、200 が返る・WARNING が出ない・`conf.json` の
  `ToDo_Days` が `"365"` になる
- `ToDo_Days` の既定を `"1y"` に戻すと `tests/test_handler.py` が 3 件落ちる
  （reviewer が実際に戻して確かめ、元に戻した）

## 分かったこと

**この項目の背景の「`base.html` にはそのあと式が無いので何も変えていない」は
誤りだった。** tornado の `{% autoescape None %}` は、書いた位置より前の式も
含めて `base.html` 全体に効いていた。削除で `url_prefix` / `title` /
`version` / `static_url` がエスケープされるようになった（`--urlprefix "/a'b"`
で `/a'b/` が `/a&#x27;b/` になる）。既定の `urlprefix` では HTML の違いは
空行 1 つだけ。子テンプレートは以前からエスケープされていた。

## 残ること

- `docs/data-format.md` の「旧形式ではファイルに残っていた `&quot;` が
  ブラウザ側で解かれていた」という文は、いまのテンプレートの実測と合わない
  （`&quot;` を入れると画面に `&quot;` がそのまま見える。`HEAD` でも同じ）。
  因果の説明（autoescape のせい）だけ外して事実の文は残した。旧アプリの挙動
  として正しいのかは未確認で、`migrate.py` が `html.unescape()` を 2 回
  かける根拠に関わる

## 分担の振り返り

- implementer: 依頼どおり 5 項目を実装した。判断が要る点として、
  `data-format.md` の因果が怪しいことを自分で挙げた
- reviewer: 背景の誤り（`autoescape None` が `base.html` 全体に効いていた）と、
  `data-format.md` の主張が実測と合わないことを、実際にアプリを起動して
  測って見つけた。これは implementer・verifier には拾えない
- verifier: 全項目が通ることを確かめた。**報告ファイルを作らなかった**
  （返事だけで返した）。また**起動した確認用のサーバを 1 つ止め忘れた**
  （別のポートで残っていた。main が PID を確かめて止めた）
- 見込みとの食い違い: 担当は見込みどおり。main のモデルだけが違った
- 次に同じ規模なら: 「文書の記述が実装と合っているか」を含む項目には、
  reviewer に**実測**を依頼文で名指しする形を続ける（今回これで誤りが見つかった）。
  verifier の依頼には「報告ファイルを必ず書く」「起動したプロセスを終わりに
  PID で止め、`pgrep` で残りが無いことを確かめる」を明記する。
  項目を立てるときの背景の文は、`tornado` の挙動のように**実測で確かめて
  から書く**（今回は着手前の実測が不十分だった）
