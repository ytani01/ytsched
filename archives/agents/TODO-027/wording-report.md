# TODO-027（および同時にコミットする TODO-033）wording の報告

対象は次の全 .md（`git status` の未追跡・変更分すべて）。

- `TODO.md`（差分）
- `src/README.md`（差分）
- `archives/todo/TODO-027. 不正な入力で 500 になるのをやめる.md`（新規）
- `archives/todo/TODO-033. URL_PREFIX の改名に追随できていない箇所を直す.md`（新規）
- `archives/agents/TODO-027/` 全ファイル（README・依頼書 4 回分×3 担当・
  報告 4 回分×3 担当）
- `archives/agents/TODO-033/` 全ファイル（README・依頼書・報告、
  implementer/verifier）。`wording-report.md` のみ対象外（指示どおり）

文書は直していない。前例の有無は `git grep -cF <語> HEAD -- '*.md'` で
`HEAD` を基準に確認した（作業ツリーではない）。

## 前例の無い語（前例の件数が少ない順、0 件はまとめて列挙）

いずれも 0 件（前例なし）。

| 語 | 出てくる場所（例） | 見立て |
|---|---|---|
| **コレクション段階** | `implementer-request4.md:22`「`uv run pytest` は今、コレクション段階で全滅する」、`verifier-report4.md:23` | pytest の "collection" フェーズを指す訳語。カタカナ＋漢語の組み合わせがこのリポジトリでは初出。一般に通用するかは判断できない（pytest 用語として妥当だが、定訳かは分からない） |
| **全滅** | `implementer-request4.md:22`、`implementer-report4.md:108,134`、`verifier-report3.md:8,161`、`verifier-report4.md:23,96` | 一般語としては普通だが、このリポジトリでは初出かつ 7 箇所で繰り返し使われている（テスト全部が collection で落ちる、の意味）。一般語としては通用しそうだが、「造語ではないか」の見立ては main の判断 |
| **総称化** | `reviewer-report3.md:51`「`get_conf_arg()` の総称化と `convert=`」 | PEP 695 のジェネリック化を指す訳語。一般的な IT 用語としても定訳かはっきりしない（「ジェネリック化」のほうが通りが良いかもしれない）。判断できない |
| **消し間違い** | `TODO-027.md:65`「消し間違いを `fix` 側で作っていた」、`implementer-report3/4.md`、`reviewer-request3.md:46`、`reviewer-report3.md:129`、`verifier-report3.md:120` 他、計 8 箇所 | 意味は透明（誤って消してしまうこと）だが辞書語ではない複合語。このリポジトリのこの項目内で繰り返し使われている中心的な言い回し。一般的な言い回しに見えるので、造語というより普通の日本語の可能性が高い |
| **二度読み** | `reviewer-request3.md:31`「`get_argument()` の二度読みで作っている」、`implementer-report4.md:24`、`reviewer-report3.md:172`、`implementer-request4.md:67` | 「同じ引数を 2 回読む」の意味で透明だが、辞書語ではない複合語。判断できない |
| **押さえが緩んだ** | `reviewer-report.md:195`「`TestConfArgs` の docstring と、押さえが緩んだ件」、`verifier-report2.md:103` | 「テストの押さえ（固定・検証範囲）」を「緩んだ」と形容する比喩的な言い回し。他の箇所では「押さえている」「押さえる」という動詞は多数使われている（前例あり、後述）が、「緩んだ」との組み合わせは初出 |
| **一本に揃える** | `reviewer-report3.md:544`「書き込む経路は、読めない引数を受け取ったら断るで一本に揃う」、`implementer-request4.md` の見出し「方針: … で一本に揃えた」 | 「一つの扱いに統一する」の意味で、口語としては自然だが定型句としての前例は無い |
| **継ぎ当て** | `implementer-request2.md:31,40`「3 件をばらばらに継ぎ当てせず」 | 衣類の「継ぎ当て」を比喩的にコード修正へ転用した表現。一般に通じるが前例なし |
| **頭打ち** | `implementer-report2.md:144`、`reviewer-report2.md:43`「`SEARCH_MODE_MAX_DAYS` で頭打ち」 | 一般語としては普通の言い回し。造語というより普通の日本語に見える |
| **居座る/居座って/居座り** | `reviewer-report.md:56,193`、`implementer-request2.md:15`、`reviewer-report2.md:16,88`（計 5 箇所） | 「不正な値が `Conf.cgi` に残り続ける」ことの比喩。一般語で、この項目内での中心的な言い回し |
| **下ごしらえ** | `implementer-request4.md:86`、`implementer-report4.md:172`「`check_int_range()` のような下ごしらえは要らない」 | 料理由来の比喩を「事前の検証処理」に転用。一般に通じるが前例なし |
| **すり抜ける** | `reviewer-report.md:60`「桁数がその手前のときだけすり抜ける」 | 一般語。造語ではなさそう |
| **抜け道** | `reviewer-request.md:32`、`reviewer-report.md:14`「`set_conf()` の抜け道は無い」 | 一般語。造語ではなさそう |
| **取りこぼし** | `reviewer-report.md:53,190`、`reviewer-report2.md:84,191`（計 4 箇所） | 一般語。造語ではなさそう |

## 前例が少数だけあった語（参考。前例なしではないので本文からは除外候補）

- **素通し** — `implementer-report4.md:502` 付近「素通しをやめ」等（複数箇所）。
  `git grep` では `archives/agents/TODO-005/reviewer-report.md:135` に
  1 件のみ前例あり（「`__init__` から素通しで全リクエスト」）。ほぼ
  前例なしに近いので参考として挙げる
- **素通り** — 「`except ValueError` を素通りする」など。前例 11 件で、
  このリポジトリでは既に定着した言い回し。造語ではない

## 判断できない語について

上の表のうち、**「コレクション段階」「全滅」「総称化」「一本に揃える」
「二度読み」「押さえが緩んだ」** は、一般的な IT 用語・日本語表現として
定着しているかどうか自分では判断できない。特に「総称化」は
「ジェネリック化」という、より通りの良い言い方があるかもしれない。

「消し間違い」「継ぎ当て」「頭打ち」「居座る」「下ごしらえ」
「すり抜ける」「抜け道」「取りこぼし」は、比喩的だが一般的な日本語の
範囲に見え、このリポジトリ固有の言い換えには見えない。

## 読んだファイル

- `TODO.md`、`src/README.md`
- `archives/todo/TODO-027. 不正な入力で 500 になるのをやめる.md`
- `archives/todo/TODO-033. URL_PREFIX の改名に追随できていない箇所を直す.md`
- `archives/agents/TODO-027/README.md`
- `archives/agents/TODO-027/implementer-request.md`〜`request4.md`（4 件）
- `archives/agents/TODO-027/implementer-report.md`〜`report4.md`（4 件）
- `archives/agents/TODO-027/verifier-request.md`〜`request4.md`（4 件）
- `archives/agents/TODO-027/verifier-report.md`〜`report4.md`（4 件）
- `archives/agents/TODO-027/reviewer-request.md`〜`request3.md`（3 件）
- `archives/agents/TODO-027/reviewer-report.md`〜`report3.md`（3 件）
- `archives/agents/TODO-033/README.md`
- `archives/agents/TODO-033/implementer-request.md` / `implementer-report.md`
- `archives/agents/TODO-033/verifier-request.md` / `verifier-report.md`

## 前例の無い語数

**14 語**（コレクション段階・全滅・総称化・消し間違い・二度読み・
押さえが緩んだ・一本に揃える・継ぎ当て・頭打ち・居座る（居座って／居座り
を含む）・下ごしらえ・すり抜ける・抜け道・取りこぼし）。
