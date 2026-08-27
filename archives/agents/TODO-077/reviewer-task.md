# TODO-077 reviewer への依頼

TODO-077（`fix` で `.bak` が中間状態に上書きされるのを直す）の実装が
終わった。**良いかどうか**を見てほしい。動作確認は verifier が別に行う。

- 実装の報告: `archives/agents/TODO-077/implementer-report.md`
- 依頼書: `archives/agents/TODO-077/implementer-task.md`
- 背景: `TODO.md` の TODO-077、`docs/design-review.md` の B
- 変更点は `git diff` で見られる（まだコミットしていない）

## 特に見てほしいところ

1. **`SchedData.save()` が日付から `get_sdf()` で引き直している点。**
   変更してから `save()` するまでの間に、その日が LRU から捨てられると
   どうなるか。捨てられ得るのか、得るなら変更が失われるのか。
   `SchedDataFile` そのものを覚えるほうがよいか
2. 保存し忘れる道が開いていないか。`SchedData.add_sde()` /
   `del_sde()` を呼んで `save()` を呼ばない経路が、`src/` の中に
   残っていないか
3. 例外で `exec_update()` を抜けたときに `_dirty_dates` が残る。
   同じ `SchedData` を使う次のリクエストで、意図しないファイルが
   保存される道が開かないか
4. docstring の書き方と、`~/.claude/CLAUDE.md`・`CLAUDE.md` の決まりからの逸脱
5. 足したテストが、本当にこの不具合を捕まえるものになっているか
   （実装を戻したら落ちるか、を頭の中で追う）

## 決まりごと

- **コードを直さない。** 指摘するだけ
- **確信度の高い指摘に絞る。数を稼がない**
- 報告は `archives/agents/TODO-077/reviewer-report.md` に書く。
  返事は 5 行以内
