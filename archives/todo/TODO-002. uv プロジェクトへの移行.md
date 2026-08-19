# TODO-002. uv プロジェクトへの移行

見込み: Opus 5 / effort medium（サブエージェントなし）
実施: サブエージェント（archives/agents/TODO-002/）

## きっかけ

2021 年に setuptools（`setup.py` + `setup.cfg` + `entry_points.cfg`）で
作ったまま止まっていた。Python 3.14 / uv / pytest の環境へ移すための
最初の一歩として、まずパッケージングを新しくする。

TODO-008 で `uv tool install` した先でも `ytsched` コマンド 1 つで
動くようにしたいので、`webroot/`（テンプレートと静的ファイル）を
パッケージに同梱するところまでを範囲に含めた。

## やったこと

- `setup.py` / `setup.cfg` / `entry_points.cfg` / `pkgs.txt` を削除し、
  `pyproject.toml`（hatchling + hatch-vcs）に置き換えた。構成は `tmr` に揃えた
- `ytsched/` → `src/ytsched/`、`webroot/` → `src/ytsched/webroot/` へ
  `git mv` で移動。`[tool.hatch.build.targets.wheel] packages = ["src/ytsched"]`
  だけで、webroot 配下は wheel・sdist の両方に入る
  （hatchling が既定でパッケージ配下の全ファイルを拾うため、
  `[tool.hatch.build.targets.sdist]` の明示は不要だった）
- `requires-python = ">=3.14"`、`.python-version` に `3.14`
- 未使用の依存 `html2text`（`ytsched.py` にコメントとして残るのみ）と
  `monthdelta`（参照なし）を外した。依存は `click` と `tornado` だけ
- `__version__` を `importlib.metadata.version()` から取る方式へ変更（`tmr` と同形）
- `webapp.py` の `DEF_WEBROOT` をカレントディレクトリ依存の `'./webroot/'` から
  パッケージ同梱パスへ変更した

```python
DEF_WEBROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'webroot')
```

`importlib.resources` ではなく `__file__` にしたのは、Tornado の
`static_path` / `template_path` が実ファイルシステム上のパス文字列を
要求すること、`webapp.py` は `__init__.py` から import されるので
`importlib.resources.files("ytsched")` が初期化途中の自パッケージを
参照する恐れがあること、の 2 点による。

### 版数（git タグを打たないと決めた）

利用者の判断で git タグは打たない。タグが無くても hatch-vcs は
`0.1.dev3+gedc735adb.d20260819` のような開発版数を出すので、
`fallback-version` は入れずに済んだ。`.dYYYYMMDD` は作業ツリーが
汚れているときだけ付く印で、コミット済みなら `0.1.dev4+g9e4153e7f` の形になる。
`+g...` はローカル版数識別子なので PyPI へは上げられないが、
`uv tool install` で使う分には支障がない。

### `uv.lock`

生成したが、`.gitignore` の `*.lock` により git の追跡対象外
（`mise run upgradeproject` が毎回作り直すため。TODO-001 で決めた）。

## テスト

TODO-003 の前なので自動テストはまだ無い。`verifier` が手で確認した。

- `uv sync` が通り、`.venv` の Python は 3.14.7。`click 8.4.2` / `tornado 6.5.8`
- `uv run ytsched webapp --datadir <一時ディレクトリ>` で起動し、curl で確認
  - `/ytsched/` → 200
  - `/ytsched/static/css/my.css` → 200
  - `/ytsched/static/favicon.ico` → 200
  - `/ytsched/edit`（GET のみ） → 200
- トップページの HTML にテンプレートタグ（`{{ }}` / `{% %}`）が生で残っていない。
  `<title>Ytsched: 0.1.dev3+gedc735adb.d20260819</title>` と版数が展開されている
- サーバのログに例外・トレースバックは無し
  （出たのは起動メッセージと、空のデータディレクトリに対する `cache miss` の warning のみ。
  この warning 自体は TODO-005 で直す）
- `uv build` した wheel / sdist に `ytsched/webroot/` の 9 ファイルが入っている。
  wheel を使い捨ての venv へ入れ、`DEF_WEBROOT` が `site-packages/ytsched/webroot` を
  指すことも確認した
- `uv run ytsched webapp --help` の `--webroot` 既定値が同梱パスの絶対パスになっている

## 気づいたが直さなかったもの

移行の範囲外として残した。

- `main_handler.py` の `print('DAYS_YEAR=...')` が import 時に出る（`--help` にも混ざる）— TODO-005
- `webapp.py` の `except Exception as ex: raise ex`、`autoreload=True` 固定 — TODO-005
- 正常系のキャッシュミスを warning で出している — TODO-005
- `install.sh` が `$MYDIR/webroot` を参照しており、移動で壊れた — TODO-008
- `README.md` に `setup.py` と旧 Python 版の記述が残っている — TODO-009
- `__main__.py` の docstring が `"""main for musicbox package"""`、
  `cli` の help が `sample package` のまま（テンプレートの残骸）
