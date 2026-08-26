# TODO-056 wording 報告

## 前例の無い語

### `TimeoutError`（wait_for_selector / wait_for_url を含む）

- 出てくる場所: `archives/agents/TODO-056/verifier-report.md`
  「`playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout
  10000ms exceeded.`」など
- `git grep`: `TimeoutError` 0 件、`wait_for_selector` 0 件、`wait_for_url` 0 件
- 見立て: playwright / Python の例外名・API 名をそのまま引用したもの。
  造語ではなく、そのまま書くのが CLAUDE.md の方針どおり

### `except A, B, C:`（括弧なしタプル）

- 出てくる場所: `archives/todo/TODO-056. JavaScript の退行を捕まえられる
  ようにする.md`「`except A, B, C:` は直さない」の節、
  `archives/agents/TODO-056/verifier-report.md`「括弧なしタプルとして
  評価される」
- `git grep`: `括弧なしタプル` 0 件（`括弧なし` 単独では 2 件、`タプル` は
  一般語）
- 見立て: Python の文法用語の組み合わせで、一般に通用する言い方。
  このリポジトリの言い換えではない

### `空いている port`

- 出てくる場所: `docs/Developer.md`「テストごとに `ytsched webapp` を
  空いている port で起動し」
- `git grep`: フレーズとしては 0 件（`空いている` 単独では 3 件、`port`
  単独では多数）
- 見立て: 普通の日本語の組み合わせ。造語ではない

## 前例があった語（参考）

「テストの種類を指す言い方」として気にした以下は、いずれも同じ文言が
既に committed の `.md`（`TODO.md` の現行版や `archives/agents/TODO-049`
`TODO-057` 配下）に前例あり。

- `ブラウザを動かすテスト`（3 件）
- `ブラウザを起動するテスト`（2 件）
- `bfcache`（12 件）／`headless`（40 件）／`ゴールデンマスターテスト`
  （40 件）／`chromium`（98 件）／`skip`（37 件）

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-056. JavaScript の退行を捕まえられるようにする.md`
- `archives/agents/TODO-056/README.md`
- `archives/agents/TODO-056/request-verifier.md`
- `archives/agents/TODO-056/verifier-report.md`
- `archives/agents/TODO-056/request-wording.md`
- `docs/Developer.md`（差分部分）
- `tests/README.md`（差分部分）

## 前例なしの語数

3 語（いずれも API/文法用語の引用、または一般的な日本語の組み合わせで、
造語には見えない）。
