# テストの構成

`tests/` の各ファイルが何を見ているかをまとめる。走らせ方（`mise run test`
や `pytest` の叩き方）は [../docs/Developer.md](../docs/Developer.md) に
あるので、ここには書かない。ソースコードの構成は
[../src/README.md](../src/README.md) を見ること。

## 各ファイルの役割

- `helpers.py` — `webapp.WebServer` が組み立てているのと同じ
  `tornado.web.Application` を、`datadir` だけ差し替えて作る
  （`make_app()`）。リクエストを実際に送らずに handler を作る
  `make_handler()` や、ロケール依存の読み書きを確かめる
  `run_in_c_locale()` もここにある
- `test_ytsched.py` — データモデル（`SchedDataEnt` /
  `SchedDataFile` / `SchedData`）のテスト
- `test_handler.py` — `HandlerBase`（`conf.json` の読み書き）と
  `days2x_percent` のテスト
- `test_main_handler.py` — `MainHandler` の個々のメソッドのテスト
- `test_web.py` — `tornado.testing` を使い、`MainHandler` /
  `EditHandler` へ実際にリクエストを送るテスト
- `test_webapp.py` — `WebServer` の組み立てそのもののテスト
- `test_migrate.py` — 旧形式（タブ区切り `.cgi`）から JSON Lines への
  移行のテスト
- `test_mylog.py` — `mylog.py` のテスト
- `test_browser.py` — chromium を実際に動かして、`my.js` の動きを
  見るテスト（TODO-056）。ホームボタンと週送りを押して、URL だけで
  なく画面が変わったかまで確かめる。ブラウザが無ければ skip する。
  週送りが**ページを読み直さずに済んでいるか**もここで見る（TODO-069）
- `make_test_data.py` — 移行元（旧形式）の合成テストデータを
  `tests/data/old_format/` に生成するスクリプト。個人の予定そのものは
  リポジトリに入れられないため、構造だけを写して中身を架空にした
  データを使う

## ゴールデンマスターテスト

`test_handler.py` の `test_settings_are_read` のように、「今の挙動」を
そのまま固定して確かめるテストが何本かある（TODO-021 で足した）。
リファクタリングの前後で挙動が変わっていないことを確かめるためのもので、
**挙動を変える変更なら、そのテストも合わせて書き直してよい**。落ちたのが
リファクタリングのミスなのか、意図した挙動の変更なのかは、変更内容を
見て判断する。

## ブラウザを動かすテスト

`test_browser.py` だけは、`ytsched webapp` を起動して chromium で
操作する（TODO-056）。他のテストが使う `tornado.testing` は HTML を
返すところまでしか見ないので、**`my.js` の不具合は原理的に捕まらない**。
実際 TODO-049 でホームボタンに持ち込んだ不具合（今日から離れた週で
押すと、URL だけが今日に書き換わって画面は前の週のまま）は、
テストが 1 件も落ちないまま利用者が見つけた。

- **URL が変わったことだけを見ない。** 上の不具合はまさに「URL は
  変わったが画面が変わらない」ものだった。目的の日の欄が実際に
  出ているかまで見ること
- **ビューポートの高さを変えると再現しなくなる。** 上の不具合は
  「週の内容が 1 画面に収まっているか」を先に見ていたせいで起きた。
  収まらない大きさで見ると、退行を戻しても落ちない
- **ページを読み直したかどうかは、目印で見る**（TODO-069）。
  `window` に値を置いておき、操作のあとに残っているかを見る。
  読み直しが起きれば `window` ごと作り直されるので消える。URL や
  画面の中身だけを見ても、読み直したかどうかは分からない
- 走らせ方と前提（ブラウザの持ってき方など）は
  [../docs/Developer.md](../docs/Developer.md) にある

## テストデータの置き場所

- `tests/data/old_format/` — `make_test_data.py` が生成する、移行元
  （旧形式）の合成テストデータ。どのファイルが何を再現しているかは、
  そのディレクトリの `README.md` にある
- そのほかのテストは、`tmp_path`（pytest の fixture）の下に
  データディレクトリを作って使う。実データ（`~/ytsched/data`）には
  触れない
