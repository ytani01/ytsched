# TODO-226. 編集画面で Ctrl+Enter で確定する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus / high）+ verifier（Sonnet / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 44 | 5,469 | 15,013 | 1,532,708 | 74% |
| rev-226（reviewer） | Opus 5.5 | high | 14 | 2,919 | 36,857 | 184,085 | 11% |
| ver-226（verifier） | Sonnet 5.5 | medium | 20 | 3,738 | 34,321 | 270,807 | 15% |
| 合計 |  |  | 78 | 12,126 | 86,191 | 1,987,600 | 計 2,085,995 |

## きっかけ

PC ブラウザで、編集画面をキーボードだけで確定したい、と利用者から。
ボタンが `<div>` でフォームに submit ボタンが無いため、Enter を押しても何も起きなかった。

利用者と決めたこと: 端末の判定はせず、Enter 単独ではなく Ctrl+Enter にする。
詳細欄（textarea）の Enter は改行のまま。Cmd+Enter は main の判断で足した。

## やったこと

- `src/ytsched/webroot/static/js/edit-page.js` に `keyDownHdr` を足し、
  `#input_form` の keydown に登録した。Ctrl+Enter / Cmd+Enter で
  `submitCmd("fix")` を呼ぶ。`isComposing` の間は無視する
- `docs/UsersGuide.md` の「3. 編集画面」に 1 行足した

## 確かめたこと

- reviewer: 指摘なし。Safari の IME まわりに確信度の低い点が 1 件あったが、
  Ctrl/Cmd 併用時しか動かないので実害なしと見ている（実機では未確認）
- verifier（Playwright + Chromium、1280x800）: 件名で Ctrl+Enter → `cmd=fix` で保存して週の表示へ、
  詳細で Enter → 改行のみ、詳細で Ctrl+Enter → 保存、件名で Enter → 何も起きない。4 手順すべて期待どおり
- 利用者がテストサーバーで触って OK
- IME 変換中は確かめていない（Playwright で再現しにくい）

報告は `archives/agents/TODO-226/` にある。

## 分担の振り返り

- reviewer は指摘なし、verifier は食い違いなし。見込みどおりの編成で動いた
- 16 行の JS 変更で reviewer と verifier の分が合わせて 26%。次に同じ規模なら、
  分岐が 1 つだけの変更は reviewer を省けないか利用者に聞いてから組む
  （規則上は分岐が変わるので要る）。verifier の手順 4 つは代表として足りていた
