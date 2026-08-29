/**
 *   (c) 2026 ytani01
 */

// 週の管理 (TODO-083)
//
// 外へ出すもの:
//   weekOffsetOfDate() -- nav.js (popstateHdr / scrollToDate)
//   hasAdjacentWeek()  -- swipe.js (swipeDragTo)
//   layoutWeeks()      -- main-page.js (onloadHdr)
//   setActiveWeek()    -- nav.js (popstateHdr / scrollToDate)
//   slideWeekWrap()    -- swipe.js (cancelSwipeDrag)
//   moveToMonday()     -- swipe.js (swipeFinish)・keyboard.js (keyHdr)・
//                         main-page.js (startAutoPageTurn / pageTurnPointerUpHdr)
//   weekPanelOf() / cancelActiveSlide / SWIPE_SLIDE_MSEC はこのファイル内だけで使う
// 外から使うもの:
//   ytState (state.js)          -- elWeekWrap・activeWeekOffset・activeMonday
//   mondayOf() (gauge.js)       -- weekOffsetOfDate
//   dispGauge() (gauge.js)      -- setActiveWeek
//   getLocaltimeDateString() / getLocaltimeString() / shiftDays() (nav.js)
//     -- weekOffsetOfDate・moveToMonday
//   pushDateInUrl() / scrollToId() (nav.js) -- setActiveWeek
//   doGet() (nav.js)            -- moveToMonday

// 滑らせるアニメーションの長さ (msec)。CSS の
// ``.my-week-wrap-sliding`` の transition と合わせる (TODO-057)
(() => {
const ytsched = window.ytsched;
const SWIPE_SLIDE_MSEC = 200;

/**
 * ``offset`` の週の ``.my-week-panel`` を返す (TODO-069)。
 *
 * 読み込んだ範囲の外なら null。
 *
 * @param {number} offset
 * @return {Element | null}
 */
const weekPanelOf = (offset) => {
  if (!ytsched.ytState.elWeekWrap) {
    return null;
  }
  return ytsched.ytState.elWeekWrap.querySelector(
    `.my-week-panel[data-offset="${offset}"]`,
  );
};
/**
 * ``date_str`` を含む週が DOM にあれば、その ``offset`` を返す
 * (TODO-069)。無ければ null。
 *
 * 週の panel は月曜 (``data-monday``) を持っているので、渡された
 * 日付を月曜へ丸めてから探す。
 *
 * @param {String} date_str   'YYYY-mm-dd'
 * @return {number | null}
 */
window.ytsched.weekOffsetOfDate = (date_str) => {
  if (!ytsched.ytState.elWeekWrap || !date_str) {
    return null;
  }
  const monday = ytsched.getLocaltimeDateString(ytsched.mondayOf(date_str));
  const panel = ytsched.ytState.elWeekWrap.querySelector(
    `.my-week-panel[data-monday="${monday}"]`,
  );
  if (!panel) {
    return null;
  }
  return Number(panel.dataset.offset);
};

/**
 * 隣の週が DOM にあるかどうか (TODO-057・TODO-069)。
 *
 * 検索モードでは ``weeks`` が 1 要素で、隣の週は CSS で隠れている
 * のではなく、そもそも DOM に無い。読み込んだ範囲の端でも同じ。
 * 滑らせても中身の無い余白が見えるだけなので、その場合は false。
 */
window.ytsched.hasAdjacentWeek = () => {
  return !!(
    weekPanelOf(ytsched.ytState.activeWeekOffset - 1) ||
    weekPanelOf(ytsched.ytState.activeWeekOffset + 1)
  );
};

/**
 * 週の並べ直し (TODO-069)。
 *
 * ``ytState.activeWeekOffset`` の週だけを通常フロー (``my-week-cur``) に
 * 残し、他は ``left`` で左右へ振り分ける。**通常フローに残す週を
 * 差し替えるのは、body の高さをその週に合わせるため**
 * (``position: absolute`` の週は高さを決めない)。
 *
 * 隣の 2 週にだけ ``my-week-near`` を付ける。指の追従中に見える
 * ようにするのはこの 2 週だけで、前後数ヶ月ぶんを全部見せない。
 */
window.ytsched.layoutWeeks = () => {
  if (!ytsched.ytState.elWeekWrap) {
    return;
  }
  const panels = ytsched.ytState.elWeekWrap.querySelectorAll(".my-week-panel");
  for (const panel of panels) {
    const offset = Number(panel.dataset.offset);
    const rel = offset - ytsched.ytState.activeWeekOffset;

    panel.classList.toggle("my-week-cur", rel === 0);
    panel.classList.toggle("my-week-near", Math.abs(rel) === 1);
    panel.style.left = `${rel * 100}%`;
  }
};

/**
 * いま見ている週を ``offset`` の週にする (TODO-069)。
 *
 * ページを読み直さずに、DOM の中だけで週を移る。並べ直したうえで、
 * 週に付いて回るもの (``ytState.activeMonday``・画面に出ている
 * ヘッダーとフッターの日付入力欄・ヘッダーのゲージ) を、その週の月曜に
 * 揃える。
 *
 * ``push_flag`` が真なら URL を履歴に積む。戻る/進むから呼ぶときは
 * 偽にする (``popstate`` で来た時点で URL はもう動いている)。
 *
 * @param {number} offset
 * @param {boolean} push_flag
 * @return {boolean}   移れたら true
 */
window.ytsched.setActiveWeek = (offset, push_flag = true) => {
  const panel = weekPanelOf(offset);
  if (!panel) {
    return false;
  }

  ytsched.ytState.activeWeekOffset = offset;
  ytsched.layoutWeeks();

  // 滑らせ終わった位置から、ずらした分を戻す。並べ直しで見た目の
  // 位置は変わらないので、transition を掛けずに戻す
  ytsched.ytState.elWeekWrap.classList.remove("my-week-wrap-sliding");
  ytsched.ytState.elWeekWrap.classList.remove("my-week-wrap-dragging");
  ytsched.ytState.elWeekWrap.style.transform = "";

  const monday = panel.dataset.monday;
  ytsched.ytState.activeMonday = monday;

  // 画面に出ている日付入力欄および #cur_day を合わせる (TODO-111)
  for (const id of ["header_date", "footer_date"]) {
    const el_date = document.getElementById(id);
    if (el_date) {
      el_date.value = monday;
    }
  }
  const el_cur_day = document.getElementById("cur_day");
  if (el_cur_day) {
    el_cur_day.value = monday;
  }

  if (push_flag) {
    ytsched.pushDateInUrl(monday);
  }

  ytsched.dispGauge(monday);
  ytsched.scrollToId(`date-${monday}`, "top", "instant");

  return true;
};

// 走っている ``slideWeekWrap()`` の後始末 (リスナーを外し、タイマーを
// 消す)。呼び出しが重なったとき、次の呼び出しの先頭で使う (TODO-057)。
// week.js だけで閉じる状態 (TODO-083)
let cancelActiveSlide = null;

/**
 * ``ytState.elWeekWrap`` を ``target_x`` (px) まで滑らせてから ``on_done`` を
 * 呼ぶ (TODO-057)。
 *
 * 指の追従で途中まで動いていれば、その位置から続けて滑らせる
 * (``ytState.elWeekWrap.style.transform`` を見る)。追従無しの呼び出し
 * (メニューバー・キー) は 0 から始める。
 *
 * ``transitionend`` を待つが、来なかったときのために、タイマーでも
 * 進める (来ないと週送りが効かなくなる)。
 *
 * 前の呼び出しがまだ終わっていなければ、その後始末 (リスナーを外し、
 * タイマーを消す) だけ行い、``on_done()`` は呼ばない。あとから来た
 * 呼び出しが勝つ。
 *
 * @param {number} target_x
 * @param {Function} on_done
 */
window.ytsched.slideWeekWrap = (target_x, on_done) => {
  if (!ytsched.ytState.elWeekWrap || !ytsched.hasAdjacentWeek()) {
    on_done();
    return;
  }

  if (cancelActiveSlide) {
    cancelActiveSlide();
    cancelActiveSlide = null;
  }

  ytsched.ytState.elWeekWrap.classList.add("my-week-wrap-dragging");
  if (!ytsched.ytState.elWeekWrap.style.transform) {
    ytsched.ytState.elWeekWrap.style.transform = "translateX(0px)";
  }
  void ytsched.ytState.elWeekWrap.offsetWidth; // 強制的にレイアウトし、transition を効かせる

  let done = false;
  let timeoutId;
  const cleanup = () => {
    ytsched.ytState.elWeekWrap.removeEventListener("transitionend", onEnd);
    clearTimeout(timeoutId);
  };
  const finish = () => {
    if (done) {
      return;
    }
    done = true;
    cancelActiveSlide = null;
    cleanup();
    ytsched.ytState.elWeekWrap.classList.remove("my-week-wrap-sliding");
    on_done();
  };
  const onEnd = (event) => {
    if (
      event.target !== ytsched.ytState.elWeekWrap ||
      event.propertyName !== "transform"
    ) {
      return;
    }
    finish();
  };

  cancelActiveSlide = () => {
    done = true;
    cleanup();
  };

  ytsched.ytState.elWeekWrap.addEventListener("transitionend", onEnd);
  timeoutId = setTimeout(finish, SWIPE_SLIDE_MSEC + 100);

  ytsched.ytState.elWeekWrap.classList.add("my-week-wrap-sliding");
  ytsched.ytState.elWeekWrap.style.transform = `translateX(${target_x}px)`;
};

/**
 * 週を送る (次/前の月曜へ移る)。
 *
 * 隣の週まで滑らせてから、**送り先が DOM にあれば、そこへ移るだけ**
 * (TODO-069)。読み込んだ範囲の外へ出るときだけ ``doGet()`` して、
 * 新しい日付を中心に前後数ヶ月を取り直す。スワイプ・メニューバーの
 * ◀▶・キーの←→の、どの経路もここを通る。
 *
 * @param {number} direction
 * @param {String} path
 */
window.ytsched.moveToMonday = (direction = 1, path) => {
  let cur_day = new Date(ytsched.ytState.activeMonday);
  console.log(`moveToMonday:path=${path}`);
  console.log(`moveToMonday:cur_day=${ytsched.getLocaltimeString(cur_day)}`);

  let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
  if (wday == 0) {
    wday = 7; // Sun: 0 --> 7
  }

  // まず ``cur_day`` をその週の月曜まで戻してから、前後へ 7 日
  // ずらす (TODO-063)。週の途中の日付から直に前の月曜を求めると、
  // 同じ週の月曜になって週が送れない
  const days = 1 - wday + (direction > 0 ? 7 : -7);
  console.log(`moveToMonday:days=${days}`);

  let d1 = new Date(ytsched.ytState.activeMonday);
  d1 = ytsched.shiftDays(d1, days);
  const d1_str = ytsched.getLocaltimeDateString(d1);
  console.log(`moveToMonday:d1_str=${d1_str}`);

  const win_w = document.documentElement.clientWidth;
  const target_x = direction > 0 ? -win_w : win_w;
  const next_offset = ytsched.ytState.activeWeekOffset + direction;
  console.log(`moveToMonday:next_offset=${next_offset}`);

  ytsched.slideWeekWrap(target_x, () => {
    if (ytsched.setActiveWeek(next_offset)) {
      return;
    }
    ytsched.doGet(path, { date: d1_str, sde_align: "top" });
  });
};
})();
