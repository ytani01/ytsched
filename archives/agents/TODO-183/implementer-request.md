# TODO-183 implementer への依頼

## 目的

ゴミ箱の戻るボタンで、直前に表示していた週へ戻す。
いまは `trash.html` の戻るボタンが `href="{{ url_prefix }}"` なので、
どの週からゴミ箱へ入っても、戻ると今日を含む週が開く。

## 対象範囲

以下の 4 ファイルと、テスト 2 ファイル。それ以外は触らない。

### 1. `src/ytsched/webroot/templates/main.html`（384〜393 行）

フッターのゴミ箱リンクは素の `<a href>` で日付を持てない。
ミニカレンダーの見出し（`data-action="month-view"`）と同じ形にする。

```html
<a class="my-btn{% if not trash_count %} my-btn-disabled{% end %}"
  {% if trash_count %}data-action="trash"{% end %}>
```

`href` は消す。件数が 0 のときに属性を付けないのは今までどおり。

### 2. `src/ytsched/webroot/static/js/main-page.js`

`actionMouseDownHdr()` の `switch` に `case "trash"` を足す。

```js
case "trash":
  // フッターのゴミ箱。表示中の週の月曜を渡して、ゴミ箱の戻る
  // ボタンでその週へ返せるようにする (TODO-183)
  ytsched.doGet(`${ytsched.url_prefix}trash`, {
    date: ytsched.ytState.activeMonday,
  });
  break;
```

置き場所は `month-view` の近く。既存の case の書き方に合わせる。

### 3. `src/ytsched/trash_handler.py`

- `handler_util` を import する。
- 戻り先の日付を読むメソッドを足す。**無指定・不正なら `None`**
  （＝今日の週。今までと同じ遷移先）。

```python
def _back_date(self) -> datetime.date | None:
    """戻り先の週の日付 (TODO-183)。

    フッターのゴミ箱ボタンが、表示中の週の月曜を ``date`` で渡す。
    無指定や、日付として読めない値なら ``None``（今日を含む週へ
    戻る。TODO-183 より前と同じ）。
    """
    date_str = self.get_argument("date", None)
    if not date_str:
        return None
    return handler_util.convert_value(
        "date", date_str, handler_util.str2date
    )
```

- `_back_date()` の結果を `?date=` の断片にするメソッドも足す
  （`get()` と `_delete_many()` の両方で使う）。無指定なら空文字。

```python
def _back_query(self) -> str:
    date = self._back_date()
    return f"?date={date}" if date else ""
```

- `get()`: `self.render(...)` に `date=self._back_date()` を渡す。
- `_delete_many()`: リダイレクト先に `_back_query()` を付ける。
  ゴミ箱へ戻るときも、空になって週間表示へ移るときも同じ。

```python
query = self._back_query()
if trash.entries(max_entries=1):
    self.redirect(f"{self._app_info.url_prefix}trash{query}")
else:
    self.redirect(f"{self._app_info.url_prefix}{query}")
```

- **`_restore()` は変えない。** 復活した予定の日付へ移るのが正しい
  （復活したものを見せるための遷移。利用者と確認済み）。

### 4. `src/ytsched/webroot/templates/trash.html`

- 戻るボタン（`my-trash-back-col` の `<a>`）:

```html
<a href="{{ url_prefix }}{% if date %}?date={{ date }}{% end %}"
   class="my-btn" aria-label="一覧へ戻る">
```

- 削除フォーム（`#trash-delete-form`）に hidden を足して、完全に
  削除したあとも日付を引き継ぐ:

```html
{% if date %}<input type="hidden" name="date" value="{{ date }}">{% end %}
```

## テスト

### `tests/test_web.py`

- `TestMainHandler.test_trash_count_with_entries`（209 行あたり）は
  `trash">` を当てにしている。`data-action="trash"` を見るように直す。
- `TestTrashHandler` に足す:
  - `date` を渡すと、戻るボタンの `href` が `{URL_PREFIX}/?date=…` に
    なり、削除フォームに `name="date"` の hidden が入る。
  - `date` が無いとき・不正なとき（例 `date=2026-99-99`）は、
    戻るボタンが `{URL_PREFIX}/` のままで hidden が入らない。
  - `delete_many` で 1 件残るとき、`date` を渡すと Location が
    `{URL_PREFIX}/trash?date=…` になる。
  - `delete_many` で全部消えるとき、`date` を渡すと Location が
    `{URL_PREFIX}/?date=…` になる。
  - 既存の `test_delete_many_removes_entry_and_redirects_to_trash` と
    `test_delete_many_all_entries_redirects_to_week`（`date` を渡さない）
    は、そのまま通ること。

### `tests/test_browser.py`

- 週間表示のフッターのゴミ箱を押すと、`{server}trash?date={その週の月曜}`
  へ移り、ゴミ箱の戻るボタンを押すとその週へ戻る、というテストを足す。
  既存の `_write_trash(tmp_path)` を使う（件数が 0 だとボタンが無効）。
  週の指定は `page.goto(f"{server}?date=…")` で行う。

## 完了条件

- 上の変更が入っている。
- `mise run fmt` → `mise run lint` → `mise run typecheck` →
  `mise run test` が通る（`upgradeproject` は走らせない）。
- ブラウザテストを含めて通ること。

## 報告

`archives/agents/TODO-183/implementer-report.md` に、変更点・実行した
コマンドと結果・残る懸念を書く。返事は 5 行以内。
