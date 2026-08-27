# ソースコードの構成

`src/ytsched/` の構成と、クラス同士の関係をまとめる。個別のメソッドの
引数や挙動は、コード中の docstring を読めば分かるので、ここには書かない。
利用者向けの説明は [../README.md](../README.md)、開発環境やコマンドは
[../docs/Developer.md](../docs/Developer.md)、テストの構成は
[../tests/README.md](../tests/README.md) を見ること。

## モジュール一覧

```
src/ytsched/
  ytsched.py       # データモデル: SchedDataEnt / SchedDataFile / SchedData
  handler.py       # HandlerBase（tornado.web.RequestHandler の共通部分、conf.json の読み書き）
  handler_util.py  # 引数と設定値の変換・検証（self を使わない純粋な関数）
  main_handler.py  # MainHandler（一覧表示と、追加/修正/削除の受け取り）
  sched_update.py  # SchedUpdater（追加/修正/削除の実行。tornado を知らない）
  edit_handler.py  # EditHandler（編集画面）
  webapp.py        # WebServer（tornado.web.Application の組み立て、CLI から呼ばれる）
  migrate.py       # 旧形式（タブ区切り .cgi）から JSON Lines への移行と、設定ファイルの JSON 化（`ytsched migrate`）
  mylog.py         # loguru ラッパ
  click_utils.py   # click の共通オプション（`-h` / `-d` / `-V` `-v`）をまとめたデコレータ
  __main__.py      # click による CLI（`ytsched` コマンド）
  webroot/
    templates/      # tornado のテンプレート（base/main/edit/sde.html）
    static/         # CSS・アイコン・manifest.json・favicon
      js/           # ブラウザ側のスクリプト 8 本（後述）
```

CLI には `webapp`（Web サーバ、本来の入口）と `migrate`（旧形式からの
移行）の 2 つがある。

`-h` / `--help`、`-d` / `--debug`、`-V` / `-v` / `--version` は、
`click_utils.py` の `click_common_opts()` がグループと全サブコマンドに
付ける（TODO-036）。このデコレータは `click.pass_context` も付けるので、
**コマンド関数の第 1 引数は `ctx`** になる。グループ側の `--debug` は
`ctx.obj` に入れてサブコマンドへ引き継ぎ、`__main__.py` の `_is_debug()`
でサブコマンド自身の `--debug` とまとめている（`ytsched --debug migrate`
でも `ytsched migrate --debug` でも DEBUG が出る）。

## データモデル: `SchedDataEnt` / `SchedDataFile` / `SchedData`

3 つのクラスが `ytsched.py` に入っていて、下から上へ積み上がっている。
関係を図にすると次のようになる。

```mermaid
classDiagram
    class SchedDataEnt {
        +sde_id
        +date
        +time_start
        +time_end
        +type
        +title
        +place
        +detail
    }
    class SchedDataFile {
        +date
        +topdir
        +pathname
        +sde : list~SchedDataEnt~
        +load()
        +save()
        +add_sde()
        +del_sde()
        +get_sde()
    }
    class SchedData {
        -_sdf_cache : OrderedDict
        +get_sdf()
        +get_sde()
        +add_sde()
        +del_sde()
    }
    class MainHandler
    class EditHandler
    SchedDataFile "1" *-- "many" SchedDataEnt
    SchedData "1" o-- "many" SchedDataFile : LRU キャッシュ
    MainHandler ..> SchedData : 経由してアクセス
    EditHandler ..> SchedData : 経由してアクセス
```

- **`SchedDataEnt`** が予定・ToDo 1 件を表す。`sde_id`（UUID）、`date`、
  `time_start`/`time_end`、`type`、`title`、`place`、`detail` を持つ。
  `detail` は常に素のテキスト（改行・タブもそのまま持てる）で、保存・
  読み込みで文字列を変換しない。**画面の改行表示は CSS の
  `white-space: pre-wrap` が担っている**（テンプレート側でタグを
  差し込んでいるわけではない）
- **`SchedDataFile`** が 1 ファイル（1 日分、または ToDo 全体）の
  読み書きを担う。パスの決め方は `date2path()` が担う。規則は
  [../docs/data-format.md](../docs/data-format.md) にある
- **`SchedData`** が `SchedDataFile` を日付ごとにキャッシュする
  （`OrderedDict` で LRU 的に古いものから捨てる）。`MainHandler` /
  `EditHandler` はここを経由してデータへアクセスし、`SchedDataFile` を
  直接は触らない

データの中身の仕様（保存形式、壊れた行の扱い、`normalize()` による
「重要」「取り消し」の判定など）は
[../docs/data-format.md](../docs/data-format.md) にまとめてある。

## Web ハンドラ: `HandlerBase` / `MainHandler` / `EditHandler`

継承関係と、`WebServer` がどの URL にどちらを割り当てているかを
図にすると次のようになる。

```mermaid
classDiagram
    class RequestHandler {
        <<tornado.web>>
    }
    class HandlerBase {
        +initialize(sd)
        +load_conf()
        +save_conf()
        +get_conf()
        +set_conf()
    }
    class MainHandler {
        +get()
        +post()
    }
    class EditHandler {
        +get()
        +post()
    }
    class SchedUpdater {
        +exec_update(form)
        +cmd_add()
        +cmd_del()
    }
    class WebServer {
        +main()
    }
    RequestHandler <|-- HandlerBase
    HandlerBase <|-- MainHandler
    HandlerBase <|-- EditHandler
    MainHandler ..> SchedUpdater : cmd の実行
    WebServer ..> MainHandler : "/", url_prefix, url_prefix/
    WebServer ..> EditHandler : url_prefix/edit, url_prefix/edit/
```

- **`HandlerBase`**（`handler.py`）が `tornado.web.RequestHandler` の
  共通部分。リクエストのたびにデータディレクトリ直下の設定ファイル
  `conf.json` を読み書きする（`load_conf()` / `save_conf()` /
  `get_conf()` / `set_conf()`）。JSON のオブジェクト 1 つで、値は
  すべて文字列（TODO-032）。**`LoadMonths` を除いて**、人が手で編集する
  ファイルではない（`LoadMonths` については `MainHandler` の項を参照）。
  読めない設定ファイル（壊れた JSON、オブジェクトでない、値が文字列
  でないキー）は、警告を 1 行出して無視する。
  `SchedData` は `tornado.web.Application` の URL 登録時に渡し、
  `initialize()` で受け取る（`app.settings` 経由ではないので、
  `self._sd` の型が `SchedData` として見える。TODO-081）。
  引数や設定値の変換と検証は、`self` を使わない純粋な関数として
  `handler_util.py` にある（`convert_value()` / `str2date()` /
  `check_date()` / `date_range()` / `check_int_range()`。
  TODO-027・TODO-081）
- **`MainHandler`**（`main_handler.py`）が一覧表示と、追加・修正・削除の
  受け取り（`cmd=add/fix/update/del`）を兼ねる。**`GET` が描画、`POST` が
  実行**で、`post()` は描かずに `redirect()` する（POST-Redirect-GET、
  TODO-050）。リロードで再送信にならないようにするため。`cmd` を
  実行するのは `post()` だけで、`GET` に `cmd` を付けても効かない。
  一覧に出すのは、**渡された日を含む週の月曜から日曜までの 7 日**
  （`load_sched()`。TODO-049）。検索したときだけは週で区切らず、
  条件に当たった日を古いほうへさかのぼって並べる。
  **返す HTML には、前後 1 ヶ月ぶんの週も一緒に入れる**（TODO-069）。
  ブラウザはこの中を動くかぎりページを読み直さない。何ヶ月ぶんかは
  `conf.json` の `LoadMonths` で変えられる（既定 1、範囲 0〜24）。
  **これだけは利用者が手で書く設定**で、画面から変える UI は無く、
  アプリは読むだけ（`get_load_months()`）なので手で書いた値は消えない。
  検索モードでは週の区切りに合わないので 1 週だけ。
  **URL に持たせるのは日付だけ**（`?date=2026-08-24`）。検索語・
  絞り込み・ToDo の日数・目標件数は `conf.json` に保存する。
  それらを送るときは、ブックマークや履歴に残らないよう `POST` を通す
  （`nav.js` の `doPost()`。表示を変えるだけの移動は `doGet()`）
- **`SchedUpdater`**（`sched_update.py`）が `cmd` の実行そのものを担う
  （TODO-087）。**tornado を知らない**ので、ハンドラを組み立てずに
  呼べる。フォームの値は `MainHandler` が取り出して `SchedUpdateForm`
  1 つに詰めて渡す。**読めない値（不正な日付・時刻）で 400 にするのも、
  見つからない `sde_id` で 404 にするのも `MainHandler` 側**
  （`SchedUpdater.get_modified_sde()` は `None` を返すだけ）。400 は
  書き込みが 1 つも起きる前に投げる（TODO-027）ので、値の取り出しは
  `SchedUpdater` を呼ぶより先に済ませる
- **`EditHandler`**（`edit_handler.py`）が編集画面を出す。`date` /
  `sde_id` の決め方（引数 → クエリ文字列 → 既定値の順）は docstring に
  書いてある。フォームの隠しフィールド `orig_date`（更新・削除のときに
  見に行くファイルの日付）は、テンプレートではなく handler が決める
  ＝ **その `sde` を読み込んだファイルの日付**（ToDo は `None`。
  TODO-029）。新規（`sde_id` 無し）のときは、まだどのファイルにも
  入っていないので**表示している日付**にする（`None` にすると、
  新規の画面で `fix` を押したときに `ToDo.jsonl` を開いて `.bak` まで
  作る道が開く）

`WebServer`（`webapp.py`）がこの 2 つを `tornado.web.Application` に
組み立てる。URL は既定で `/ytsched`（`WebServer.DEF_URL_PREFIX`）配下。

## リクエストが来てから画面が出るまでの流れ

`MainHandler`/`EditHandler` に共通の、リクエスト 1 回の流れを図にすると
次のようになる。クラス図だけでは分からない「時間の流れ」を示すためのもの
なので、クラス同士の関係は上の図を見ること。

```mermaid
sequenceDiagram
    participant Browser
    participant Handler as MainHandler / EditHandler
    participant SD as SchedData
    participant SDF as SchedDataFile
    participant Template

    Browser->>Handler: GET または POST
    Note over Handler: __init__ のたびに conf.json を読む (load_conf)
    alt POST
        Handler->>Handler: post() が cmd を実行して conf.json へ保存
        Handler-->>Browser: 302 (日付だけを付けた GET へ)
        Browser->>Handler: GET
    end
    Handler->>SD: get_sdf(date) / get_sde(date, sde_id)
    alt キャッシュに無い
        SD->>SDF: SchedDataFile(date, topdir)
        SDF->>SDF: load()
    else キャッシュに当たる
        Note over SD: ファイルを読まずにそのまま返す
    end
    SD-->>Handler: SchedDataFile / SchedDataEnt
    opt 設定値が変わった (filter_str など)
        Handler->>Handler: set_conf() が conf.json へ書き直す
    end
    Handler->>Template: render(html, ...)
    Template-->>Browser: HTML
```

## ブラウザ側のスクリプト

`static/js/` に 8 本ある（TODO-083）。ES モジュールではなく素の
`<script>` で、関数と定数はグローバルに置いたまま。テンプレートの
`onmousedown="doGet(...)"` と、`tests/test_browser.py` の
`page.evaluate("days2xPercent(0)")` が、どちらもグローバルの名前を直に
呼ぶため。

| ファイル | 中身 |
|---|---|
| `state.js` | ファイルをまたぐ状態（`ytState`） |
| `spinner.js` | 読み込み中のスピナー |
| `gauge.js` | ヘッダの横ゲージ（目盛り・針・タップ） |
| `nav.js` | URL の組み立て、`doGet()` / `doPost()`、スクロール |
| `week.js` | 週の差し替えとアニメーション（`moveToMonday()`） |
| `keyboard.js` | ソフトキーボードへの追従と、キー操作 |
| `swipe.js` | 左右のスワイプとマウスのドラッグ |
| `main-page.js` | 一覧画面（`main.html`）だけで使う初期化とハンドラ |

`base.html` が `main-page.js` 以外の 7 本を読む。`main-page.js` は
`main.html` が自分で読む（`base.html` に入れると、編集画面でも
`onloadHdr()` が走ってしまう）。

**ファイルをまたぐ状態は `state.js` の `ytState` にまとめてある**
（`elLoadingSpinner` / `elMain` / `elGaugeR0` / `elWeekWrap` /
`activeWeekOffset`）。1 つのファイルの中で閉じている状態（`swipeStart`
など）は、そのファイルのトップレベルに置いたまま。以前は `main.html` の
`<script>` がグローバル変数へ直に代入していて、それがファイルを分け
にくくしていた（TODO-083）。テンプレートの値は、`main.html` に残した
2 つの定数（`search_str0`・`today_str`）と、`base.html` の `url_prefix`
から渡す。

## 週の移動（ブラウザ側）

前後 1 ヶ月ぶんの週が最初から DOM にあるので、**週送りはページを
読み直さず、DOM の中で見せる週を差し替えるだけ**（TODO-069）。
スワイプ・メニューバーの◀▶・キーの←→は、どれも `week.js` の
`moveToMonday()` を通る。

```mermaid
flowchart TD
    A["moveToMonday(direction)"] --> B["slideWeekWrap()<br/>隣の週まで滑らせる"]
    B --> C{"送り先の週が<br/>DOM にあるか"}
    C -- ある --> D["setActiveWeek()<br/>my-week-cur を付け替え、<br/>left を振り直す"]
    D --> E["#cur_day / #date / #date_from /<br/>ゲージを、その週の月曜に揃える"]
    E --> F["pushDateInUrl()<br/>URL を履歴に積む"]
    C -- 無い --> G["doGet()<br/>その日を中心に読み直す"]
```

- 各週は `.my-week-panel` で、`data-offset`（最初に描かれた週からの
  週数）と `data-monday`（その週の月曜）を持つ。検索モードでは週の
  区切りに合わないので `data-monday` は付かない
- **通常フローに残るのは、いま見ている週（`my-week-cur`）だけ。**
  隣の 2 週（`my-week-near`）は `position: absolute` で、`left` は
  「いま見ている週から何週ぶん左右か」。`position: absolute` の週は
  body の高さを決めないので、週を差し替えるときは `my-week-cur` も
  一緒に動かさないと、高さが前の週のまま残る
- **離れた週は `display: none`。** 置くのはこの 3 つだけ。
  `position: absolute` の週も縦にはみ出した分だけ文書のスクロールを
  伸ばすので、9 週を全部置くと下に空白ができてスクロールできてしまう
- 日付の欄の `id="date-YYYY-mm-dd"` は、**前後数ヶ月ぶんの週すべてに
  付く**。だから `scrollToId()` で寄せる前に、その日を含む週へ移る
  のは呼び出し側（`scrollToDate()` / `popstateHdr()`）の役目
- **DOM に持っているデータは古くなる。** ホームボタンのダブルタップが、
  手で取り直す道（1 回のタップは今日の週へ移るだけ）

## フィルタ・検索文字列の扱い

利用者の入力を正規表現として扱う（利用者本人しか使わないアプリという
前提）。`MainHandler.get()` の中で 1 回だけコンパイルし、**不正なら
その条件を無視して全件を出す**。不正な文字列でも入力欄と `conf.json` から
消さず、マッチに使うかどうかだけを分けている。`filter_str` も
`search_str` も、照合される側（`SchedDataEnt.search_str()`）と同じ
`normalize()` を通してから `conf.json` へ保存する（TODO-029。全角括弧の
扱いは [../docs/data-format.md](../docs/data-format.md) にある）。検索
モードかどうかは「文字列が空でないか」ではなく「コンパイルできたか」で
判定する（`search_mode`）。

## テンプレートの autoescape

`base.html` は `{% autoescape None %}` のまま（エスケープを切っている）。
単一ユーザ・自分の入力しか自分に見えないため実害が無いと判断し、現状
維持と決めている。
