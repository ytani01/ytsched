# TODO-165 reviewer 報告

対象: 未コミットの `git diff`（`src/ytsched/webroot/static/js/main-page.js`、
`tests/test_browser.py`）。動作確認・テスト実行はしていない。

## まず、名指しで頼まれた 3 点の結論

- **sessionStorage の干渉（依頼 1）— 無い。**
  `clearSearchPageTurnState()` が消すのは
  `ytsched_search_auto_turn_direction` と `ytsched_search_page_turn_tap` の
  2 つだけで、新設の `ytsched_search_home_tap` には触らない。
  `pageTurnPointerDownHdr()` は `pointerdown` の capture で、ホームボタン
  （`[data-page-turn]` を持たない）を押すと `stopAutoPageTurn()` →
  `clearSearchPageTurnState()` が走るが、消えるのは上の 2 つ。
  順序も `pointerdown` → `mousedown`（`homeButtonHdr`）で、ホーム側の
  読み書きより前に終わる。**キーの取り違え・上書きは起きない。**
  ただし「誰もホームの記録を消さない」ことから来る誤判定はある（指摘 4・5）。
- **`doGet` → `doPost`（依頼 2）— 週間表示・月間表示で結果は変わらない。**
  `MainHandler.post()` は `mkurl(url_prefix, {date, sde_align})` へ
  リダイレクトし、`mkurl()` は空の値を落とすだけなので、最終 URL は
  `?date=<月曜>&sde_align=top` で `doGet` のときと同一。
  `update_conf_args()` は POST 本体に無い引数
  （`filter_str` / `todo_days` / `search_n` / `month_cal`）を
  `value is None` で読み飛ばすので、既存の設定を潰さない。
  `search_str=""` は `empty_is_given=True` なので確実に `SearchStr` を
  空にする。`conf.json` への書き込みは `on_finish()` で 1 回にまとまる。
  `get_view()` は `conf.json` に保存しないので、月間表示からの読み直しで
  週間表示に戻るのも正しい。`cmd` が無いので `exec_cmd()` は素通り。
  差分は「GET 1 回が POST + リダイレクト + GET になる」ことだけ。
- **シングルタップの遅延廃止（依頼 3）— TODO-164 の問題は再発しない。**
  TODO-164 が直したのは「2 回目がダブルタップと判定されない」ことで、
  それは sessionStorage 側で担保されている。遅延の廃止で戻るのは
  「1 回目が即座に読み直す」という TODO-164 以前の挙動だが、これ自体は
  不具合ではない。

以下、確信度の高い順。

---

## 1.（高）`docs/User.md` の記述が実態と食い違う

`docs/User.md` 9.5「検索をやめる」180〜181 行:

```
画面下部の**ホーム**（家のアイコン）では検索は解除されない。
**検索したまま**今週の月曜へ移る。
```

TODO-165 でダブルタップは検索を解除するようになるので、この 2 行は
**誤り**になる。「1 回押すと検索したまま今週の月曜へ移り、続けてもう一度
押すと検索を解除してトップ画面へ戻る」という趣旨に直す必要がある。
検索の解除手段を列挙している節なので、ここに載らないと利用者は
新しい操作に気づけない。

TODO.md の項目には文書の更新が入っていないので、範囲に含めるかどうかは
main の判断。

## 2.（高）`test_home_button_single_tap_still_reloads_search_screen` が、月曜には何も検証しない

`_open_search()` は `_open(page, server, today)` → `form_search` を送信する。
`form_search` が持つのは `search_str` と `cur_day`（= today）だけで `date` は
無いので、`MainHandler.post()` の `get_date(None)` は `cur_day` を返し、
リダイレクト先は `?date=<today>` になる。

**今日が月曜だと、この時点で URL に `date=<今週の月曜>` が入っている。**
テストはこのあと

```python
page.wait_for_url(lambda url: f"date={monday.strftime('%Y-%m-%d')}" in url, ...)
```

で待つので、**タップが何も起こさなくても即座に成立する**。続く
`_in_search_mode()` と `#search_str` の値も、無操作のまま成立する。
つまり月曜に走らせると、検索画面のシングルタップが完全に壊れていても
このテストは緑になる。

`_double_tap_home_in_search()` 側は `_mark()` と
`wait_for_function` で読み直しを確かめているので同じ穴は無い。
シングルタップ側にも `_mark()` / `_marked()` を入れるか、
`sde_align=top` が**付かない**ことまで見れば塞がる。

（TODO-164 から引き継いだ穴だが、この項目でテストを書き直すので挙げる。）

## 3.（高）`_double_tap_home_in_search()` の skip が、直そうとしている失敗そのものを握りつぶす

```python
elapsed = (time.monotonic() - start) * 1000
at = max(interval_msec, elapsed)
if at >= HOME_DOUBLE_TAP_MSEC:
    pytest.skip(...)
```

`interval_msec` は 0 / 300 / 600 なので、skip するのは
**1 回目の読み直しに 1000 ミリ秒以上かかったとき**だけ。だがこれは
「読み直しが 1 秒窓に収まらないので、実機でもダブルタップが成立しない」
という状態であり、**TODO-165 が直そうとしている失敗の形そのもの**。
それをテストの失敗ではなく skip に変換している。

具体的に困る筋道:

- 負荷の高いときや遅い機械（この開発機は Raspberry Pi）で、検索画面の
  読み直しが 1 秒を越えると、**ホームボタンのテスト 3 件
  （マウス 1 件 + タッチ 2 件）が黙って skip し、pytest は緑**になる。
  ダブルタップの主要な退行テストが消えたことに気づけない
- CI やまとめ実行では skip の行を見落としやすい

加えて、`at = max(interval_msec, elapsed)` なので、**テストは 2 回目の
タップ間隔を下から決められない**。`elapsed` が 600 を越える環境では
`interval_msec=300` と `600` が同じ操作になり、パラメータ 2 件が同じ
テストになる。TODO.md の「300〜600 ミリ秒の現実的な間隔で成立することを
見る」は、環境が速いときにしか担保されない。

判断が要る点: skip をやめて失敗させるか、少なくとも
「skip が出たら分かる形」（`-rs` を前提にする、実測した `elapsed` を
出力に残す等）にするか。

## 4.（中）検索画面で「ホーム → 別の操作 → ホーム」が、1 秒以内ならダブルタップになる

`ytsched_search_home_tap` を消すのは**ダブルタップが成立したとき**だけで、
他の操作では消えない。TODO-123 側は
`pageTurnPointerDownHdr()` がボタン以外の `pointerdown` で
`ytsched_search_page_turn_tap` を消す作りになっており、**対称になっていない**。

起きる例（検索画面）:

1. T にホームを 1 回タップ → 検索を保ったまま今週の月曜へ読み直し
2. T+400 に ▶（`forward_button`）をタップ → 1 週送りで再び読み直し
3. T+800 にホームをタップ → `now - T = 800 < 1000` で**ダブルタップと判定**
   → 検索が解除されてトップ画面へ飛ぶ

利用者から見ると「ホームを 1 回押しただけなのに検索が消えた」になる。
実害は小さいが、間に別の操作が入ったら記録を捨てる作りのほうが素直で、
TODO-123 の先例とも揃う。

## 5.（中）3 回叩くと、検索画面へ引き戻される

`setSearchHomeTapMsec(0)` で**成功時に記録を消している**ため、
遷移が終わる前の 3 回目のタップが「1 回目」に戻る。

1. T: tap1 → キー = T、検索語つき POST（画面はまだ検索画面）
2. T+400: tap2 → ダブル成立、**キーを削除**して `reloadHome()` を POST。
   トップ画面の読み込みが始まるが、古い検索画面はまだ操作できる
3. T+700: tap3（反応が無いと思って 3 回目を叩く）。古い検索画面で
   `search_str0` は生きており、キーは消えているので「1 回目」と判定。
   **検索語つきの POST** を投げ、これが 2 の遷移を上書きする
4. 結果、トップ画面ではなく検索画面（`date=今週の月曜`）に着地する

記録を消さずに残しておけば、3 回目も窓の内なら `reloadHome()` になり
同じ場所へ着く。読み直しが遅い環境ほど起きやすい
（＝指摘 3 と同じ条件で起きる）。

## 6.（中・低）検索画面のダブルタップで、履歴が 1 つ増える

TODO-164 では 1 回目の読み直しを 350 ミリ秒待って取り消していたので、
ダブルタップの遷移は 1 回だった。今は 1 回目も必ず遷移するので
`検索@today` → `検索@今週の月曜` → `トップ@今週の月曜` と 3 つ積まれる。
トップへ戻ったあと「戻る」を押すと、**意図して開いたわけではない
検索画面**（今週の月曜）に戻る。

週間・月間表示は `doGet`（1 エントリ）→ POST + リダイレクト（1 エントリ）
で変わらない。仕様として許容するかどうかは main の判断。

---

## 確信度の低いもの（参考）

- **週間・月間表示のダブルタップは 350 ミリ秒のまま**で、タッチのテストも
  検索画面にしか無い。TODO-165 は「350 ミリ秒は人の指には狭すぎる」と
  判断し、テストでも 600 ミリ秒間隔を「現実的」としているのに、
  週間表示のダブルタップ（TODO-069 のデータ取り直し）は 600 ミリ秒の
  指では成立しない。項目では意図してそのままにすると決めているので
  範囲外だが、**同じ利用者から同じ形の報告が来る筋**なので、archives に
  「なぜ週間表示は据え置いたか」を残しておくとよい。
- `_in_search_mode()` が bool を返しながら中で `assert` している。
  False を返す経路（検索モードでない）には assert が無いので、
  `assert not _in_search_mode(...)` の側は週パネル数・週バーを見ていない。
  補っているのはマウス版の 1 件だけで、タッチ版の 2 件は
  `data-search-date-to` の有無しか見ていない。
- `HOME_DOUBLE_TAP_MSEC = 1000`（テスト）と
  `SEARCH_HOME_DOUBLE_TAP_MSEC = 1000`（JS）が二重管理。片方だけ変えると
  テストが静かに意味を失う（指摘 3 の skip と組み合わさると気づきにくい）。
- 検索の正規表現が不正なとき（`search_error`）は `search_mode` が false
  なのに `data-search-str0` は非空なので、`homeButtonHdr()` は検索側の
  分岐に入る。この状態でホームを 1 回押すと、週間表示なのに毎回
  サーバへ POST して読み直す。TODO-164 以前からある挙動で、今回の変更で
  悪くはなっていない（むしろダブルタップで不正な検索語から抜けられる
  ようになった）。
- `page.wait_for_function()` を**遷移をまたいで**使うのは、この
  ファイルでは今回が初めて。Playwright は新しい実行コンテキストで
  評価し直す作りなので動くはずだが、他の使い方（同一文書内）と違うので、
  verifier の繰り返し実行で flaky が出ないかは見ておきたい。
