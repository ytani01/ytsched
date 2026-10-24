# TODO-220. mylog の使われていない機能を削る（対応しない）

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ（決めるだけの項目） |
| 実施 | Opus 5.5 / effort medium | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 96 | 20,699 | 133,972 | 3,229,505 | 100% |
| 合計 |  |  | 96 | 20,699 | 133,972 | 3,229,505 | 計 3,384,272 |

- コード全体の見直しと TODO-219 を立てるところまでを含めた量（同じ会話で決めたので分けられない）

## きっかけ

コード全体を無駄な処理・過剰な実装の観点で見直したところ、`src/ytsched/mylog.py` の
次の部分が ytsched の src から使われていなかった。

- 名前ごとの水準（`_levels`・`setLevel()`・`_filter()`・`getLogger()` の `level` 引数）。
  使っているのは docstring の例と `tests/test_mylog.py` だけ
- `exmsg()`。docstring の例にしか出てこない

## やらないと決めた理由

**`mylog.py` は他のプロジェクトと同じものを使っている**（tmr、ytBackgammon、
ytstreetorgan、ccspk など）。ytsched だけ削ると中身がずれ、あとで直すときに
そろえ直す手間が増える。削れるのは約 35 行で、その手間に見合わない。

利用者に選んでもらい、残すことにした。

## 残ること

他のプロジェクトとそろえて削るなら、`mylog.py` を使うプロジェクト全体の話として
別に立てる。
