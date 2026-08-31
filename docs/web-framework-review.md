# Python Web フレームワークの検討

**結論: 現在の ytsched では Tornado を使い続ける。**
移行先を選ぶ必要が生じた場合の第一候補は、Starlette、Uvicorn、Jinja2
の組み合わせとする。

この文書は 2026-09-01 時点の実装と、各フレームワークの公式資料を
基にした検討結果である。

## 現在の Tornado について

Tornado は登場から時間がたっているものの、保守が止まった
フレームワークではない。現在の 6.5 系は Python 3.14 を正式に
サポートし、標準ライブラリの `asyncio` と同じイベントループを使える。

- [Tornado 公式文書](https://www.tornadoweb.org/en/stable/)
- [Tornado 6.5.0 の変更点](https://www.tornadoweb.org/en/stable/releases/v6.5.0.html)

ytsched は単一ユーザー向けで、JSON Lines による同期ファイル処理が
中心である。リクエストを処理するフレームワークを替えても、現在の
用途で体感できるほど速くなる可能性は低い。

また、`SchedLoader`、`SchedUpdater`、`SchedData`、`ConfFile` などの
ドメイン処理とデータ処理は、すでに Tornado から分離されている。
Tornado に依存しているのは主にハンドラ、Web サーバーの組み立て、
テンプレート、HTTP テストであり、現在の構成が保守しにくい状態とは
いえない。

## 候補の比較

| 候補           | ytsched との相性                   | 判断                                 |
| -------------- | ---------------------------------- | ------------------------------------ |
| Tornado を継続 | とてもよい                         | 現時点の推奨                         |
| Starlette      | よい                               | 将来移行するなら第一候補             |
| FastAPI        | API 中心ならよい                   | 現在の HTML 中心の構成には機能が多い |
| Litestar       | 多機能                             | 現在の規模では利点を生かしにくい     |
| Django         | DB、認証、管理画面、フォームに強い | 現在の構成には大きすぎる             |

### Starlette

Starlette は軽量な ASGI フレームワークで、型注釈、HTTPX を使う
テスト、静的ファイル、テンプレート、WebSocket などを備えている。
2026 年 3 月に 1.0 が公開され、Python 3.14 にも正式に対応している。

ASGI は Web サーバーとアプリケーションの間の標準インターフェース
なので、Tornado 固有の HTTP サーバーから離れ、Uvicorn などの
ASGI サーバーを選べることが移行の主な利点になる。

- [Starlette 公式文書](https://www.starlette.io/)
- [Starlette のリリース履歴](https://www.starlette.io/release-notes/)
- [ASGI 仕様](https://asgi.readthedocs.io/en/latest/specs/main.html)

ただし、ASGI と `async` を採用するだけで処理が速くなるわけではない。
現在の同期ファイル I/O をイベントループ上でそのまま実行すれば、
ほかのリクエストを止める可能性がある。移行時には、同期のまま扱う
処理とスレッドへ出す処理を分ける必要がある。

### FastAPI

FastAPI は Starlette を基盤とし、Python の型注釈と Pydantic を使った
入力検証、OpenAPI、API 文書の自動生成を備える。JSON API を外部へ
公開する場合には有力だが、現在の ytsched は HTML の表示とフォーム
送信が中心なので、主な利点を生かせない。

- [FastAPI 公式文書](https://fastapi.tiangolo.com/)

### Litestar

Litestar は ASGI に対応し、依存関係の注入、OpenAPI、セキュリティ
機能、テンプレートなどをまとめて提供する。必要な機能は揃っているが、
現在の ytsched では Starlette より多い仕組みを導入する理由がない。

- [Litestar 公式文書](https://docs.litestar.dev/2/)

### Django

Django はデータベースの ORM、認証、管理画面、フォームなどを一体で
提供する。これらが必要なアプリケーションには適しているが、独自の
JSON Lines 形式を使い、認証をリバースプロキシへ任せる ytsched では、
導入する仕組みの多くが使われない。

- [Django 公式文書](https://docs.djangoproject.com/)

## Starlette へ移す場合の影響

ドメイン処理は Tornado から分離されているため、その部分は大きく
変えずに済む。一方、次の部分は書き換えが必要になる。

- `RequestHandler` を継承する各ハンドラ
- `tornado.web.Application` と `HTTPServer` の組み立て
- `tornado.testing.AsyncHTTPTestCase` を使う HTTP テスト
- Tornado のテンプレート

特にテンプレートでは、Tornado 固有の `{% end %}`、テンプレート内の
Python 式、`static_url()` を広く使っている。Jinja2 へ移す場合は、
約 900 行のテンプレートを変換し、autoescape の違いを含めて表示結果を
確認する必要がある。ハンドラと HTTP テストを合わせると、直接影響を
受ける範囲は約 3,800 行になる。

したがって、移行は依存パッケージを交換するだけの作業ではなく、
Web 層を一通り作り直す作業になる。性能向上だけを目的に実施するには、
移行費用が大きい。

## 方針

当面は次の順で進める。

1. Tornado を使い続ける。
2. 必要になれば、サーバーの起動処理を `asyncio.run()` を使う現在の
   書き方へ直す。
3. JSON API、外部サービスとの非同期通信、WebSocket などが増え、
   ASGI の共通部品を使う利点が明確になった時点で Starlette への移行を
   改めて検討する。

フレームワークが新しいという理由だけで全面移行はしない。Tornado
固有のコードが実際に保守の妨げになったとき、または ASGI の
エコシステムを使う具体的な必要が生じたときを見直しの時期とする。
