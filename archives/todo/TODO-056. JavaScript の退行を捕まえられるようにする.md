# TODO-056. JavaScript の退行を捕まえられるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort high | main + verifier + wording |
| 消費 | output 25,179 / cache_creation 148,620 / 概算 $3.4 |
|      | main 89% + verifier 7% + wording 5%（料金の割合） |

## きっかけ

**TODO-049 で `my.js` の `scrollToId()` に持ち込んだ不具合を、reviewer も
verifier も捕まえられず、利用者が見つけた。** 今日から離れた週でホーム
ボタンを押すと、URL だけが今日に書き換わって画面は前の週のままだった。

`tests/` にブラウザを起動するテストが 1 件も無く、`mise run test` は
`pytest` だけで JavaScript を実行しない。`tornado.testing` は HTML を返す
ところまでしか見ないので、**この種の不具合は原理的に捕まらない。**
TODO-054 も、この穴が空いたまま済ませた。

## 決めたこと

着手時に利用者に確認した（項目に「決めること」として残してあったもの）。

- **playwright は dev 依存に入れる。** `mise run test` で他のテストと
  一緒に走る。ブラウザを起動する分だけ `mise run test` は重くなるが
  （3 件で 8 秒ほど）、走らせ忘れを防ぐほうを採った
- **範囲は、TODO-049 の不具合 1 件 ＋ 週送り（前・次）の 3 件。**
  まず「落ちるテストが書ける」ことと、置き場所・走らせ方を固める
- **ブラウザはシステムの `/usr/bin/chromium`。** `mise run shot` と同じ
  前提（TODO-045）。無ければ skip する

## やったこと

`tests/test_browser.py` を足した。

- テストごとに `ytsched webapp` を空いている port で起動し、`--datadir`
  には `tmp_path` を渡す（実データに触れない。検索語が `conf.json` に
  残るので、使い回さずテストごとに作り直す）
- playwright で chromium を起動してボタンを押し、URL と画面の両方を見る

書いたテストは 3 件。

- `test_home_button_moves_the_view` — 70 日前の週を開いてホームボタンを
  押し、**今日の欄が実際に画面に出る**ことまで見る（TODO-049）
- `test_forward_button_moves_a_week` — 週の途中（水曜）から ▶ を押すと、
  次の週の月曜になる（TODO-063）
- `test_back_button_moves_a_week` — 同じく ◀ で前の週の月曜になる

あわせて、playwright を dev 依存に入れたことで要らなくなった
`uv run --with playwright` を、`mise.toml` の `shot` タスクと
`tools/screenshot.py` の説明から外した。

## 落ちることを確かめた

**落ちないテストでは意味が無い**ので、`my.js` をわざと元へ戻して
確かめた（確かめたあとに戻してある）。

- `scrollToId()` で `el == null` を見るブロックと `body_h <= win_h` を
  見るブロックの順番を入れ替える（TODO-049 の変更前の形）
  → `test_home_button_moves_the_view` が落ちる
- `moveToMonday()` の `days` の計算を `c01013e` の変更前に戻す
  → `test_back_button_moves_a_week` が落ちる（同じ週の月曜
  `2026-08-24` に止まる）。▶ 側の式は元と同じなので、
  `test_forward_button_moves_a_week` は通ったまま

**ビューポートの高さは 1600px にしてある。** TODO-049 の不具合は
「週の内容が 1 画面に収まっているか」を先に見ていたせいで起きたので、
**収まらない大きさで見ると、元へ戻しても落ちない。**

## `except A, B, C:` は直さない

verifier が「Python 2 の構文に見える。`except (A, B, C):` のほうが
読み手に誤解を与えない」と挙げた。**書いたときは括弧を付けており、
外したのは `ruff format`。** Python 3.14 で括弧なしの複数指定が
書けるようになり（PEP 758）、ruff がそれに合わせて外す。

```
$ cat e.py
except (ValueError, TypeError):
$ uv run ruff format --line-length 78 e.py && cat e.py
except ValueError, TypeError:
```

括弧を書き戻しても `mise run fmt` で毎回外れるので、そのままにした。

## テスト

`mise run test` で 442 passed（`test_browser.py` の 3 件を含む）。
verifier が独立に確かめた（`archives/agents/TODO-056/verifier-report.md`）。

## 残っているもの

- **押さえたのはホームボタンと週送りだけ。** スワイプ、検索結果からの
  移動、編集画面との行き来は書いていない
- **bfcache は headless の chromium では再現しない**（TODO-068）。
  スピナーが出たままになる不具合は、このテストでは捕まらない
