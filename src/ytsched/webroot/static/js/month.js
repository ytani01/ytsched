/**
 *   (c) 2026 ytani01
 */

// 月間表示 (TODO-137)
//
// 外へ出すもの:
//   blockKeyOfDate()       -- このファイル内だけで使う (内部)
//   setActiveBlockOfDate() -- nav.js (popstateHdr / scrollToDate)
//   moveActiveBlock()      -- week.js (moveActiveDate、月間表示のとき)
// 外から使うもの:
//   ytState (state.js)          -- elWeekWrap・activeWeekOffset・activeMonday
//   hasAdjacentWeek() / setActiveWeek() / slideWeekWrap() (week.js)
//     -- moveActiveBlock (week.js の moveToMonday() と同じ枠組みを使い回す)
//   doGet() (nav.js)            -- moveActiveBlock (読み込み範囲の外)
// week.js は base.html でこのファイルより先に読み込まれる

(() => {
  const ytsched = window.ytsched;

  /**
   * ``date_str`` が属するブロックの先頭月を ``"YYYY-MM"`` で返す
   * (内部)。
   *
   * ブロックの区切りは 1〜6月・7〜12月の 2 つだけ。``month.html`` の
   * ``.my-month-panel`` が持つ ``data-block`` と同じ形にする。
   *
   * @param {String} date_str   'YYYY-mm-dd'
   * @return {String}   'YYYY-01' / 'YYYY-07'
   */
  window.ytsched.blockKeyOfDate = (date_str) => {
    const d = new Date(date_str.split("-").join("/"));
    const year = d.getFullYear();
    const start_month = d.getMonth() < 6 ? 1 : 7;
    return `${year}-${String(start_month).padStart(2, "0")}`;
  };

  /**
   * ``date_str`` を含むブロックのパネルが DOM にあれば、そこへ移る
   * (TODO-137)。
   *
   * ミニカレンダーのセルをタップしたときと同じ組み立てだが、月間表示の
   * パネルは ``data-monday`` ではなく ``data-block`` (ブロックの先頭月)
   * で探す。``week.js`` の ``weekOffsetOfDate()`` は月間表示では常に
   * null を返すので、こちらを使う。
   *
   * ブロックへ移るだけだと、今日がすでに表示中のブロックに入っている
   * ときに移り先が同じパネルになり、ゲージの針も ``activeMonday`` も
   * 動かなかった (TODO-173)。パネルの ``data-monday`` はブロックの
   * 代表日なので、渡された日付を基準日として ``setActiveWeek()`` へ
   * 一緒に渡す。ホームボタン・キーの ``Home``・戻る/進むは、どれも
   * ここを通る。
   *
   * @param {String} date_str   'YYYY-mm-dd'
   * @param {boolean} push_flag   ``setActiveWeek()`` へそのまま渡す
   * @return {boolean}   移れたら true
   */
  window.ytsched.setActiveBlockOfDate = (date_str, push_flag = true) => {
    if (!ytsched.ytState.elWeekWrap || !date_str) {
      return false;
    }
    const key = ytsched.blockKeyOfDate(date_str);
    const panel = ytsched.ytState.elWeekWrap.querySelector(
      `.my-month-panel[data-block="${key}"]`,
    );
    if (!panel) {
      return false;
    }
    return ytsched.setActiveWeek(
      Number(panel.dataset.offset),
      push_flag,
      date_str,
    );
  };

  /**
   * ブロックを送る (次/前の 6 ヶ月ブロックへ移る)。``moveToMonday()``
   * (week.js) の月版 (TODO-137)。
   *
   * 隣のブロックまで滑らせてから、**送り先が DOM にあれば、そこへ移る
   * だけ**。読み込んだ範囲の外へ出るときだけ ``doGet()`` して、次の
   * ブロックの先頭月の 1 日を中心に読み直す。フッターの ◀▶・キーの
   * ← →・スワイプ・ドラッグ・自動ページ送りは、どれも
   * ``moveActiveDate()`` (week.js) 経由でここを通る。
   *
   * @param {number} direction
   * @param {String} path
   */
  window.ytsched.moveActiveBlock = (direction, path) => {
    const cur_panel = ytsched.ytState.elWeekWrap
      ? ytsched.ytState.elWeekWrap.querySelector(
          `.my-week-panel[data-offset="${ytsched.ytState.activeWeekOffset}"]`,
        )
      : null;

    const win_w = document.documentElement.clientWidth;
    const target_x = direction > 0 ? -win_w : win_w;
    const next_offset = ytsched.ytState.activeWeekOffset + direction;

    ytsched.slideWeekWrap(target_x, () => {
      if (ytsched.setActiveWeek(next_offset)) {
        return;
      }

      // 読み込んだ範囲の外: いま見ているブロックの先頭月 (data-block)
      // から、次のブロックの先頭月の 1 日を求める
      const block = cur_panel ? cur_panel.dataset.block : null;
      const [year_str, start_month_str] = (block || "").split("-");
      const year = year_str ? Number(year_str) : new Date().getFullYear();
      const start_month = start_month_str ? Number(start_month_str) : 1;

      const total = year * 12 + (start_month - 1) + direction * 6;
      const target_year = Math.floor(total / 12);
      const target_month = (((total % 12) + 12) % 12) + 1;
      const d1_str = `${target_year}-${String(target_month).padStart(2, "0")}-01`;

      ytsched.doGet(path, { date: d1_str, view: "month" });
    });
  };
})();
