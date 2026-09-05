# TODO-187 verifier への依頼

## 目的

TODO-187（ゲージをフッターの直上にも出す）の実装が、**実際に動くか**を
確かめる。コードは直さない。見つけたことは報告するだけ。

## 前提

- 依頼の全文は `archives/agents/TODO-187/implementer-brief.md`
- implementer の報告は `archives/agents/TODO-187/implementer-report.md`
- 変更されたファイルは `git diff --stat` で分かる（未コミット）

## 確かめること

1. `mise run lint` と `mise run typecheck` が通ること
2. `uv run pytest tests/test_browser.py` が通ること
   （新しい 4 件が実際に走っているかも見る）
3. `uv run pytest --ignore=tests/test_browser.py` が通ること
4. **アプリを実際に起動して**（`--datadir` に一時ディレクトリを指定）、
   幅 390px 程度で次を確かめる:
   - ヘッダーとフッターの直上に、ゲージが 1 つずつ出る
   - 下のゲージがメニューバーの直上にあり、重なっていない
   - 上下の針の位置とラベルが同じ
   - **下のゲージをドラッグして週が移る**（上のゲージも同時に動く）
   - メニューを開くと下のゲージが隠れる
   - フッターの下に余白が残り、ページの一番下までスクロールしても
     下のゲージが中身を隠していない
   - 検索モードではゲージが出ない（上下とも）
5. implementer が「捕まえられない」と書いた点
   （下の帯の矩形の取り違え）について、実際にそうか確認する。
   `mondayFromClientX()` に渡る帯が下の帯になっているかを、
   ブラウザ上で確かめられるなら確かめる

## 注意

- `mise run upgradeproject` は走らせない
- 実データ（`~/ytsched/data`）を触らない
- コードは直さない

## 報告

`archives/agents/TODO-187/verifier-report.md` に、
**何を走らせたか・結果・見つけた問題**だけを書く。
返事は 5 行以内。
