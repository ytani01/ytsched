# TODO-078 reviewer への依頼

TODO-078（ゲージの計算を JavaScript に寄せ、Python 側を消す）の実装が
終わった。**良いかどうか**を見てほしい。動作確認は verifier が別に行う。

- 実装の報告: `archives/agents/TODO-078/implementer-report.md`
- 依頼書: `archives/agents/TODO-078/implementer-task.md`
- 変更点は `git diff` で見られる（まだコミットしていない）

## 特に見てほしいところ

1. **観点が減っていないか。** Python 側で見ていたテスト
   （`test_days2x_percent_*` 5 本、`test_calc_gauge_label_*` 2 本、
   `test_web.py` の 3 本）を消して、ブラウザ側へ移したことになっている。
   **消えた観点が本当に移っているか**を、消す前
   （`git show HEAD:tests/test_handler.py` など）と突き合わせて見ること
2. ブラウザのテストの期待値（`-1w`=46.21%、`+1w`=53.79%）が、
   変更前の Python の式と合っているか。自分で計算して確かめること
3. `dispGaugeMarks()` の呼び出し位置。読み込みの経路が 2 つある
   （`onloadHdr()` の早期 return する経路・しない経路）ので、
   **どちらでも 1 回だけ呼ばれるか**。二重に描かれる道が無いか
4. `my.js` のコメントが、二重に持っていた時代の説明のまま残っていないか
5. `~/.claude/CLAUDE.md`・`CLAUDE.md` の決まりからの逸脱

## 決まりごと

- **コードを直さない。** 指摘するだけ
- **確信度の高い指摘に絞る。数を稼がない**
- 報告は `archives/agents/TODO-078/reviewer-report.md` に書く。返事は 5 行以内
