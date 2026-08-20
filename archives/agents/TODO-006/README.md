# TODO-006 の分担

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

## なぜこの分担にしたか

型の付け直しが `ytsched.py` / `main_handler.py` / `edit_handler.py` と
テストの 4 ファイルにまたがる。`time_start` / `time_end` の `''` → `None`
は、データ形式（`:-:` などの出力）に直接触るので、判断の要る実装を
`implementer` に分けた。

確認は 2 系統に分けた。型を直すと「型チェッカーは通るが挙動が変わって
いる」が起きやすく、その 2 つは別の見方で見つかるため。

- `verifier` — mypy / basedpyright / pytest の実測と、**データ形式が
  変わっていないこと**（一時 datadir に実際に POST して `cat -A` で確認）
- `reviewer` — 型を通すために入れた guard や 1 文化が、挙動を変えて
  いないか

実際、この分け方が効いた。verifier は「壊れていない」ことを網羅して
確かめ、reviewer は verifier が通した経路の**外側**で挙動が変わった点
（下記 1-1）を見つけた。どちらか一方では出てこなかった。

## 報告

- [implementer](implementer-report.md)
- [verifier](verifier-report.md) — 末尾に追加変更の再検証（2 回目）がある
- [reviewer](reviewer-report.md)

## main が判断したこと

implementer が単独で決めた判断（報告の「単独で決めた判断」7 点）は、
verifier が呼び出し箇所を網羅し、reviewer が妥当と確認した上で承認した。
特に確認したのは次の 2 つ:

- `exec_update()` の戻り値型を `tuple[datetime.date | None, str | None]`
  にした件（呼び出しは 1 か所。`None` を受けても壊れない）
- `SchedData.add_sde()` の `date` / `sde` から既定値を外した件
  （呼び出しは 5 か所とも 2 引数の位置引数）

reviewer の指摘 2 件への対応:

- **1-1**（`sde` が `None` のとき黙って通るようになった）— `else` 側に
  `warning` を 1 行足した。**根本原因（`date` が空の POST で ToDo
  ファイルへ書かれる）は TODO-006 より前からあるもので範囲外**なので、
  [TODO-016](../../todo/) として別に立てた
- **1-2**（`SchedData` の docstring がキーの型と食い違い）— 今回直した
