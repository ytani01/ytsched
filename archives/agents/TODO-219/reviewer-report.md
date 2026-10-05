# reviewer 報告（TODO-219）

対象: 未コミットの `git diff`（`src/ytsched/trash.py`・`src/ytsched/ytsched.py`・
`tests/test_trash.py`・`tests/test_ytsched.py`）。テストの実行と整形は見ていない。

## 結論

要修正: 無し。

## 問題の無い点

- `trash.py` `_parse_line()`: 中身（decode → `json.loads` → `data["trashed_at"]` → `isinstance` で `TypeError`）は 3 か所の元のコードと同じ文で、順序も同じ
- `_BAD_LINE` の組は元と同じ 4 種（`JSONDecodeError, TypeError, ValueError, KeyError`）。3 か所とも `except _BAD_LINE` で、捕まえる範囲は変わらない
- `entries()`: `data.get("sde_id")`・絞り込み・`from_dict()` は引き続き同じ `try` の中。警告の文言 `f"{self.pathname}:{lineno}: {e} .. ignored"` と 1 行 1 回の警告は同じ
- `count()`: 文言・回数・`continue` で数えない扱いは同じ
- `delete_many()`: `from .ytsched import SchedDataEnt` と `from_dict()` も元どおり `try` の中で、壊れた行は `kept.append(line)` で元のバイトのまま残る
- `_parse_line()` が `TrashFile.ENCODING` を参照するのは呼ばれた時点なので、クラスより前に定義しても問題無い
- `delete()` の削除: `rg -w delete src tests docs` で呼び出し側は残っていない（templates・JS の `delete` は別物）。書き換えた 3 件は `delete_many()` の戻り値 0 と書き直しをしないことを見ており、元のテストの意図を保っている
- `get_date/set_date/get_keys` の削除: 呼び出し側は残っていない。`MainBinder.get_date()` は触られていない。`docs/`・`src/README.md` に記述も無い
- `test_todo_urgency` の `set_date(...)` → `sde.date = ...`: 同じ代入なので妥当
- `get_keys()` を使っていたキャッシュのテスト 2 件を `sd._sdf_cache` 直接参照へ: 妥当。`get_keys()` は `str(k)` を並べるだけだったので、キーを `date` のまま比べる今の形の方が正確。順序は `OrderedDict` の挿入順で、元と同じものを見ている。`get_cache_size()` は公開メソッドで残っているが、順序とどのキーが残るかは公開 API では見られないため、private 参照はやむを得ない
- `# self.__log` のコメント行: `ytsched.py` に残りは無い（`rg '#\s*self\.__log' src` で 0 件）。複数行の 1 件も続きの行まで消えている
- 項目 5: `click_utils.py`・`mylog.py` に差分無し（`git diff --stat` で 0 件）

## 検討

1. **`ytsched.py` の `get_sdf()` 末尾に `# if not sdf.sde:` が 1 行だけ残った**（`self._sdf_cache[date] = sdf` の後、`return sdf` の前）。
   元は次の行の `# self.__log.warning(...)` と組のコメントアウトで、今回その片方だけを消したため、意味の無い断片になっている。消すのが自然。項目 3 の範囲（`# self.__log` で始まる行と続きの行）からは外れるので、残したこと自体は依頼どおり。

2. **見なくなった挙動**: 消えたテスト（`test_get_date`・`test_set_date`・`test_set_date_none_is_today`）が見ていたのは消したメソッド自身の挙動なので、ほかで見る必要は無い。
   ただし既存の穴として、`entries()`/`count()` の**警告の文言と回数はどのテストでも見ていない**（`tests/test_trash.py` に `caplog` や `ignored` の確認が無い）。今回の差分は文言を変えていないことを読んで確かめたが、テストでは捕まらない。今回の項目の範囲外なので報告だけ。

## 作り込みすぎ

- `ytsched.py:L971-972`（`get_sdf()`）: shrink: コメント削除で `_i`・`_discarded` が使われなくなった。`for _ in range(discard_size): self._sdf_cache.popitem(last=False)` で足りる（実装の報告でも触れている）。
- `ytsched.py` `get_sdf()` 末尾: delete: 上の「検討 1」の `# if not sdf.sde:`。
- `trash.py` の `_parse_line()`・`_BAD_LINE`: 3 か所の重複を消すための最小の形で、作り込みすぎではない。

net: -3 lines possible.

## 好みの範囲

- `tests/test_trash.py` の `test_delete_unknown_trashed_at_returns_false`・`test_delete_no_file_returns_false`: `delete()` が無くなり戻り値が件数（0）になったので、名前の `returns_false` が実態と合わない（`returns_zero` など）。
