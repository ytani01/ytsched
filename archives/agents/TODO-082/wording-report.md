# TODO-082 wording 報告

対象は 6 ファイル（TODO.md、archives/todo/TODO-082、archives/agents/TODO-082/
README.md・implementer-request.md・implementer-report.md・
verifier-request.md・verifier-report.md、src/README.md、docs/Developer.md）。
更新の 3 つは差分のみ確認した。

候補は前例の件数が少ない順。

## 1. `本質ではない`

- 箇所: `archives/agents/TODO-082/implementer-request.md`
  「あれは `get_conf` / `set_conf` の読み書きそのものを見るテストで、
  キーが何かは本質ではない。」
- `git grep` の件数: 前例なし
- 見立て: 一般的な言い回し（「〜は重要ではない」の意）で、リポジトリ
  固有の造語には見えない。判断は main に委ねる。

## 2. `test helper`（英語のまま）

- 箇所: `verifier-report.md`「`test_handler.py` / `test_main_handler.py`
  の `make_app()` / `self._app` はいずれも別物（WebServer 側や
  test helper 側の概念）で問題なし。」
- `git grep` の件数: 前例なし
- 見立て: 一般的な IT 用語を英語のまま使っただけで、造語ではなさそう。
  ただし他の報告では和訳（「テスト用の補助」等）を使っている例もあるか
  未確認。判断できない。

## 3. `素の文字列`（2 語の組み合わせとして）

- 箇所: `implementer-request.md` / `implementer-report.md`
  「`HandlerBase` に残る `CONF_KEY_SEARCH_STR` か、素の文字列
  （`"ToDo_Days"` など）に置き換える」
- `git grep` の件数（フレーズそのもの）: 前例なし。ただし「素の」単独は
  83 件、「文字列」も多数あり、組み合わせが初出なだけ。
- 見立て: 「定数を介さない、生の文字列リテラル」の意味で自然に読める。
  造語というより偶然の初出に見える。

## 4. `re-export`

- 箇所: `README.md`（TODO-082/`archives/todo/TODO-082...md` の
  「`__init__.py` の re-export をやめた」、implementer-request.md にも
  同様の表現）
- `git grep` の件数: 1 件（`archives/agents/TODO-077/wording-report.md`
  で「re-export の訳語」として一度前例あり）
- 見立て: プログラミングの一般用語で、TODO-077 の wording でも
  「通用する語に見える」と判定済み。今回も同じ扱いでよさそう。

## 5. `残存参照`

- 箇所: `verifier-request.md`「消した属性…と `x_data1` / `DataFileApp`
  への参照が…どこにも残っていないこと」の見出し的な言い方、
  `verifier-report.md` の見出し「7. 消した属性・参照の残存確認」
  （直接の文字列「残存参照」は本文中）
- `git grep` の件数: 2 件（TODO-072 verifier-report、TODO-081
  reviewer-report で既に使われている）
- 見立て: このリポジトリで定着しつつある言い回しに見える。問題なさそう。

## その他、確認したが候補から外したもの

- 「決着済み」（6 件）「振り分け」（4 件）「写し」（60 件）「別物」
  （18 件）「素通り」（18 件）「折り返し」（21 件）「生残り」（33 件、
  `{{` `{%` の生残り、という verifier 定番の言い回し）「片付ける」
  （9 件）は、いずれも前例が複数あり、既に定着した言い回しに見える。
- 「未使用の属性」はフレーズとしては前例なしだが、「未使用」（20 件）
  「属性」（78 件）とも単独では多用されており、組み合わせが初出なだけ
  なので造語とは考えにくい。

## 読んだファイル

- TODO.md（差分のみ）
- archives/todo/TODO-082. import の意図と実態のズレ、未使用の属性、
  定数の置き場所を片付ける.md
- archives/agents/TODO-082/README.md
- archives/agents/TODO-082/implementer-request.md
- archives/agents/TODO-082/implementer-report.md
- archives/agents/TODO-082/verifier-request.md
- archives/agents/TODO-082/verifier-report.md
- src/README.md（差分のみ）
- docs/Developer.md（差分のみ）

## 前例の無い語数

2 語（「本質ではない」「test helper」）。ほかに「素の文字列」を
組み合わせフレーズとして 1 語挙げたが、構成語はいずれも多用されており
造語性は低いと見る。
