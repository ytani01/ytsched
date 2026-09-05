/**
 *   (c) 2026 ytani01
 */

// ファイルをまたいで参照・更新する状態 (TODO-083)。他のスクリプトから
// ``window.ytsched.ytState.xxx`` の形で読み書きする
//
// 外へ出すもの:
//   window.ytsched.ytState -- spinner / gauge / nav / week / swipe / main-page / edit-page の
//     ほぼ全ファイルが読み書きする
// 外から使うもの: なし (このファイルは一番先に読み込まれる)
const ytsched = (window.ytsched ??= {});
ytsched.url_prefix = document.documentElement.dataset.urlPrefix;
ytsched.ytState = {
  elLoadingSpinner: null,
  elMain: null,
  // ゲージの針 (``.my-gauge-r``) の一覧。ヘッダーとフッターの直上に
  // 1 つずつあるので、配列で持つ (TODO-187)。検索モードではゲージが
  // 出ないので空になる
  elGaugeRs: [],
  elWeekWrap: null,
  // いま見ている週が、最初に描かれた週から何週ぶん離れているか
  // (TODO-069)。``.my-week-panel`` の ``data-offset`` と同じ数え方で、
  // 読み込んだ直後は 0
  activeWeekOffset: 0,
  // 表示中の週の月曜日 ('YYYY-MM-DD')。週表示は DOM の中だけで週を
  // 移るので (TODO-069)、どの週を見ているかをここで覚える (TODO-093)。
  // 読み込み時に main.html の #week_wrap の data 属性から入れる
  activeMonday: "",
};
