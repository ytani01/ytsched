# TODO-182 verifier への依頼

## 目的

ヘッダーの横ゲージを、TODO-178 の下詰めから上詰めに戻し、帯の高さを
44px から 50px に広げた。目盛り・軸・今週のしるし・針が帯の上端に寄り、
帯の下端に指で押す余地（約 18px）が空くこと、そのぶんヘッダーの高さが
増えても下の一覧の始まりが帯にかぶらないことを確かめる。

## 対象

- `src/ytsched/webroot/static/css/my.css`（develop の HEAD からの差分。CSS のみ）

変更の中身:

- `.my-gauge-bar` の `height` を 44px → 50px
- `--my-gauge-shift` を 12px → 0（中身を上詰めに戻す）
- 上記 `--my-gauge-shift` の直前コメントを、いまの形（上詰め・帯 50px）に書き直した

`.my-gauge-axis` / `.my-gauge-base` / `.my-gauge-r` / `.my-gauge-label` の
`top` は `calc(... + var(--my-gauge-shift))` のままで触っていない。
body の `padding-top` は `main-page.js` が週バーの実測高で動的に入れる
（固定値ではない）。

## 確認してほしいこと

1. `mise run lint` と `uv run pytest` が通ること（件数も報告する）。
   とくに `tests/test_browser.py` のゲージ関連（`.my-gauge-bar` の
   bounding_box を使うもの、ドラッグ・クリック・ダブルタップ）
2. playwright で実際に動かして、次を見る。`--datadir` には必ず一時
   ディレクトリを渡すこと
   - **週間表示を開く。** `.my-gauge-bar` の高さが 50px であること。
     軸・今週のしるし・針・目盛りが帯の上寄りに描かれ、帯の下端との間に
     余白（約 18px）があること
   - **目盛りのラベル（±30y〜±1w など 14 個）が、いままでどおり
     読める位置にあり、帯からはみ出して切れていないこと**
   - **週バー（`#week_bar`、position: fixed）の下に一覧の先頭が来ること。**
     帯が 6px 高くなったぶん body の padding-top も増え、一覧の一番上の
     行がゲージや日付欄にかぶらないこと
   - **ゲージのドラッグ／タップで週を移せること（TODO-074・TODO-178）。**
     針の縦位置が週を変えても動かないこと
   - **検索モードでは週バーごと消え**、console エラーが出ないこと
   - スマホ幅（360〜600px）でも上記が崩れないこと
3. 気づいた懸念があれば挙げる

## 決まり

- **コードは直さない。** 見つけたことは報告するだけ。直すかどうかは
  管理者が判断する
- 報告は `archives/agents/TODO-182/verifier-report.md` に書く
- **返事は 5 行以内**（終わったか・報告ファイルのパス・判断が要る点）

---

## 追加分（1 回目の検証で見つかった不具合の修正 ＋ 回帰テスト）

1 回目の検証で、`--my-gauge-shift: 0`（単位なし）だと
`top: calc(19px + var(--my-gauge-shift))` が不正になり、軸・今週のしるし・
目盛りラベルの `top` が 0 に潰れることが分かった。対応:

- `src/ytsched/webroot/static/css/my.css`: `--my-gauge-shift` を `0` →
  `0px`。直前コメントに、0 でも単位を落とさない理由を追記
- `tests/test_browser.py`: `test_gauge_marks_sit_below_the_top_of_the_bar`
  を 1 件追加（`.my-gauge-label` が帯の上端から十分下がり、下端との間に
  余地が残ることを bounding_box で見る）

### 追加で確認してほしいこと

1. `mise run lint` と `uv run pytest` が通ること（件数も報告）
2. **新テストが、修正前の状態では実際に落ちること**を確かめる。
   手元で `--my-gauge-shift` を一時的に `0`（単位なし）へ戻して
   `test_gauge_marks_sit_below_the_top_of_the_bar` だけ走らせ、
   落ちることを確認したうえで `0px` に戻す（CSS は最終的に `0px`）
3. playwright で、`0px` の状態のゲージが意図どおりの並び
   （±0 が針の上に出る／目盛りは帯の下寄り／軸は中ほど／目盛りの下に余地）
   になっていること。幅 360〜600px
4. 気づいた懸念があれば挙げる

報告は同じ `archives/agents/TODO-182/verifier-report.md` に追記する。
返事は 5 行以内。
