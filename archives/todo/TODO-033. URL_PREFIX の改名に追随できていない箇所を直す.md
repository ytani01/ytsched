# TODO-033. URL_PREFIX の改名に追随できていない箇所を直す

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier
実施: main = Opus 5 / effort medium、担当 = implementer + verifier + wording

- [x] `tests/helpers.py` / `tests/test_webapp.py` の参照を直す
- [x] `src/README.md` の記述を直す
- [x] テストが集められるようになり、全件通ることを確かめる
- [x] `src/ytsched/__main__.py` の整形崩れを直す

分担の理由と各担当の報告は
[archives/agents/TODO-033/](../agents/TODO-033/README.md) にある。

## きっかけ

TODO-027 の 3 回目の確認で、verifier が「`pytest` が 1 件も実行できない」
と報告してきた。TODO-027 の変更とは無関係で、`develop` の HEAD 自体が
その状態だった。

`2b4fcce feat(webapp): add url_prefix option` で `WebServer.URL_PREFIX`
が `DEF_URL_PREFIX` に改名されたが、追随していない箇所が残っていた。

```
tests/helpers.py:23: URL_PREFIX = WebServer.URL_PREFIX
AttributeError: type object 'WebServer' has no attribute 'URL_PREFIX'
```

`tests/helpers.py` はほぼ全部のテストファイルが import するので、
`test_handler.py` / `test_main_handler.py` / `test_web.py` /
`test_ytsched.py` の 4 つがテストを集める段階で止まり、1 件も実行
できなかった。`basedpyright` / `mypy` も同じところで止まる。

**TODO-027 を先に決着させるか、これを先に直すかを利用者に聞き、
一度は「後回し」と決めた。** そのまま 4 回目の実装まで進めたが、
テストを書き直しても通ることを確かめられないため、利用者の判断で
先に直すことにした。

## やったこと

3 か所の置き換え。

| 場所 | 直したもの |
|---|---|
| `tests/helpers.py:23` | 右辺を `WebServer.DEF_URL_PREFIX` に |
| `tests/test_webapp.py:30,34` | 同上 |
| `src/README.md:70` | 「URL は既定で `/ytsched`（`WebServer.DEF_URL_PREFIX`）配下」に |

`tests/helpers.py` のモジュール変数 `URL_PREFIX` という名前は残した。
`test_handler.py` / `test_web.py` / `test_main_handler.py` から
import されていて、そこまで直すと差分が無駄に大きくなる。

あわせて、`src/ytsched/__main__.py` の整形崩れも直した。`2b4fcce` が
`urlprefix` 引数を足したことで `webapp()` の定義と `WebServer(...)` の
呼び出しが 78 桁を超えていた。`ruff format` を当てただけで、挙動は
変わらない。**同じコミット由来の取りこぼしなので、別項目を立てずに
この項目へ足した**（利用者の判断）。

## テスト

`uv run pytest tests` が **380 件すべて通る**ようになった。
`ruff format --check` / `ruff check` / `basedpyright` / `mypy` も
すべて通る。

verifier が、`git grep -n URL_PREFIX` で `WebServer.URL_PREFIX` の参照が
1 つも残っていないことと、アプリが既定の `/ytsched/` でも
`--urlprefix` で別の値を指定したときでも 200 を返すことを確かめた。

**依頼書に書いた CLI のオプション名 `--url-prefix` は間違いで、実物は
`--urlprefix`（ハイフンなし）だった**（verifier の指摘）。README の
記述には影響しない。
