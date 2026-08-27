# TODO-078 verifier への依頼

TODO-078（ゲージの計算を JavaScript に寄せ、Python 側を消す）の実装が
終わった。実際に動くかを確かめてほしい。

- 実装の報告: `archives/agents/TODO-078/implementer-report.md`
- 依頼書: `archives/agents/TODO-078/implementer-task.md`
- 背景: `TODO.md` の TODO-078、`docs/design-review.md` の A・E

## 確かめてほしいこと

1. `mise run lint` と `uv run pytest tests` を走らせ、結果をそのまま報告する。
   **ブラウザのテスト（`tests/test_browser.py`）が skip されていないこと**を
   確かめること（skip されていたら、この項目の確認はほぼ成り立たない）
2. **見え方が変わっていないこと。** これが本題。一時ディレクトリを
   `--datadir` にしてアプリを起動し、`tools/screenshot.py`（`mise run shot`）
   か playwright で、変更**前**（`git worktree add <一時dir> HEAD~1` で
   用意できる。`git stash` は auto mode に拒否されるので使わないこと）と
   変更**後**の画面を撮って見比べる。見るのは次の 3 つ
   - 目盛り 14 個の**文字と左右の位置**が同じか
   - 針の上の文字（`#gauge_r_label`）が同じか。今週なら `±0`
   - 検索したとき（ゲージの帯ごと出ない）に、余計なものが出ていないか
3. 週を送ったとき（スワイプ・ゲージのタップ・キーボード）に、
   針と針の上の文字が今までどおり動くか
4. **読み込んだ直後に、目盛りと針の文字が出るか。**
   サーバが埋めるのをやめたので、JavaScript が描き損ねると空になる。
   `?date=` で今週から離れた週を直接開いた場合も見ること
5. HTML に `{{ gauge` や `{% for d in gauge` の書き残しが無いこと。
   `curl` で取ったページを目で見て確かめる

画像を撮ったら、パスを報告に書くこと（main が見る）。

## 決まりごと

- **コードを直さない。** 見つけたことは報告するだけ
- 報告は `archives/agents/TODO-078/verifier-report.md` に書く。返事は 5 行以内
- **`mise run upgradeproject` は走らせない**
- `~/ytsched/data` の実データを触らない。必ず `--datadir` を指定する
