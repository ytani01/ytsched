# TODO-189. `.codegraph` を git の追跡対象から外す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 3,325 | 7,242 | 84% |
| verifier | Haiku 4.5 | medium | 3,048 | 37,445 | 16% |
| 合計 |  |  | 6,373 | 44,687 | 概算 $0.5 |

- verifier は定義のモデルが sonnet。`git status` と `git check-ignore` を
  見るだけで判断が要らないので Haiku 4.5 に下げた
- verifier の定義には `effort: medium` の行があるが、**Haiku は effort に
  対応しない**ので効いていない
- `~/.claude/bin/token-usage.py` が無くなっていて `mise run tokens` が
  動かず、`~/work/ytsched-codex/tools/token-usage.py`（別リポジトリに
  残っていた同じもの）で集計した。別項目として立て直すか要判断

## きっかけ

codegraph（コードの知識グラフ）を入れ、`codegraph init` でこのリポジトリの
インデックスを作った。53 ファイル・1,484 ノード・4,783 エッジで 5.10 MB。

できた `.codegraph/` が git の未追跡ファイルとして出た。`codegraph sync` の
たびに中身が変わる SQLite の生成物なので、追跡しない。

## やったこと

`.gitignore` の末尾（`## ytsched` の節）に足した。

```
# codegraph のインデックス（TODO-189）。codegraph init / sync が作り直す
# 生成物なので追跡しない
.codegraph/
```

## テスト

verifier に確かめさせた（`archives/agents/TODO-189/verifier-report.md`）。

- `git status --short` に `.codegraph/` が出ない
- `git check-ignore -v .codegraph/` が `.gitignore:106` を指す。
  `*.lock` など既存の行に拾われているのではない
- 追跡中のファイルは変わらない（`git ls-files` が前後とも 1,130 件で差分なし）
- `.codegraph/` 以外の未追跡ファイルが新たに無視されるようになっていない
- コメントの書き方が、同じファイルの既存の形（`（TODO-019）`・`（TODO-020）`）に揃っている

## 分担の振り返り

- **verifier は 5 点すべてを実際のコマンドで確かめ、すべて OK だった。**
  指摘は出なかったが、「追跡中のファイルが巻き添えになっていないか」
  「他の未追跡ファイルが新たに無視されていないか」は、`.gitignore` を
  眺めるだけでは分からない。この 2 点は分けた価値があった
- **見込みと食い違っていない。** 1 行の追加なので implementer は立てず、
  分岐も条件式も変わらないので reviewer も立てなかった
- **次に `.gitignore` や設定ファイルだけを 1 行変える項目をやるなら、
  同じ組み方（main + Haiku の verifier）でよい。** verifier の
  cache_creation が main の 5 倍になっているのは、起動時に `CLAUDE.md` 一式を
  読み込むため。それでも料金の割合は 16% で、Haiku に下げた効果が出ている。
  依頼文に確認項目を 5 点まで絞って書いたので往復も無かった
