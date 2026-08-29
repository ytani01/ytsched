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
  if (!ytState.elWeekWrap) {
    return null;
  }
  return ytState.elWeekWrap.querySelector(
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
const weekOffsetOfDate = (date_str) => {
  if (!ytState.elWeekWrap || !date_str) {
    return null;
  }
  const monday = getLocaltimeDateString(mondayOf(date_str));
  const panel = ytState.elWeekWrap.querySelector(
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
const hasAdjacentWeek = () => {
  return !!(
    weekPanelOf(ytState.activeWeekOffset - 1) ||
    weekPanelOf(ytState.activeWeekOffset + 1)
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
const layoutWeeks = () => {
  if (!ytState.elWeekWrap) {
    return;
  }
  const panels = ytState.elWeekWrap.querySelectorAll(".my-week-panel");
  for (const panel of panels) {
    const offset = Number(panel.dataset.offset);
    const rel = offset - ytState.activeWeekOffset;

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
 * ``#date``・ヘッダのゲージ) を、その週の月曜に揃える。
 *
 * ``push_flag`` が真なら URL を履歴に積む。戻る/進むから呼ぶときは
 * 偽にする (``popstate`` で来た時点で URL はもう動いている)。
 *
 * @param {number} offset
 * @param {boolean} push_flag
 * @return {boolean}   移れたら true
 */
const setActiveWeek = (offset, push_flag = true) => {
  const panel = weekPanelOf(offset);
  if (!panel) {
    return false;
  }

  ytState.activeWeekOffset = offset;
  layoutWeeks();

  // 滑らせ終わった位置から、ずらした分を戻す。並べ直しで見た目の
  // 位置は変わらないので、transition を掛けずに戻す
  ytState.elWeekWrap.classList.remove("my-week-wrap-sliding");
  ytState.elWeekWrap.classList.remove("my-week-wrap-dragging");
  ytState.elWeekWrap.style.transform = "";

  const monday = panel.dataset.monday;
  ytState.activeMonday = monday;

  // 画面に出ている日付入力および #cur_day を合わせる (TODO-109)
  const el_date = document.getElementById("date");
  if (el_date) {
    el_date.value = monday;
  }
  const el_cur_day = document.getElementById("cur_day");
  if (el_cur_day) {
    el_cur_day.value = monday;
  }

  if (push_flag) {
    pushDateInUrl(monday);
  }

  dispGauge(monday);
  scrollToId(`date-${monday}`, "top", "instant");

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
const slideWeekWrap = (target_x, on_done) => {
  if (!ytState.elWeekWrap || !hasAdjacentWeek()) {
    on_done();
    return;
  }

  if (cancelActiveSlide) {
    cancelActiveSlide();
    cancelActiveSlide = null;
  }

  ytState.elWeekWrap.classList.add("my-week-wrap-dragging");
  if (!ytState.elWeekWrap.style.transform) {
    ytState.elWeekWrap.style.transform = "translateX(0px)";
  }
  void ytState.elWeekWrap.offsetWidth; // 強制的にレイアウトし、transition を効かせる

  let done = false;
  let timeoutId;
  const cleanup = () => {
    ytState.elWeekWrap.removeEventListener("transitionend", onEnd);
    clearTimeout(timeoutId);
  };
  const finish = () => {
    if (done) {
      return;
    }
    done = true;
    cancelActiveSlide = null;
    cleanup();
    ytState.elWeekWrap.classList.remove("my-week-wrap-sliding");
    on_done();
  };
  const onEnd = (event) => {
    if (
      event.target !== ytState.elWeekWrap ||
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

  ytState.elWeekWrap.addEventListener("transitionend", onEnd);
  timeoutId = setTimeout(finish, SWIPE_SLIDE_MSEC + 100);

  ytState.elWeekWrap.classList.add("my-week-wrap-sliding");
  ytState.elWeekWrap.style.transform = `translateX(${target_x}px)`;
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
const moveToMonday = (direction = 1, path) => {
  let cur_day = new Date(ytState.activeMonday);
  console.log(`moveToMonday:path=${path}`);
  console.log(`moveToMonday:cur_day=${getLocaltimeString(cur_day)}`);

  let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
  if (wday == 0) {
    wday = 7; // Sun: 0 --> 7
  }

  // まず ``cur_day`` をその週の月曜まで戻してから、前後へ 7 日
  // ずらす (TODO-063)。週の途中の日付から直に前の月曜を求めると、
  // 同じ週の月曜になって週が送れない
  const days = 1 - wday + (direction > 0 ? 7 : -7);
  console.log(`moveToMonday:days=${days}`);

  let d1 = new Date(ytState.activeMonday);
  d1 = shiftDays(d1, days);
  d1_str = getLocaltimeDateString(d1);
  console.log(`moveToMonday:d1_str=${d1_str}`);

  const win_w = document.documentElement.clientWidth;
  const target_x = direction > 0 ? -win_w : win_w;
  const next_offset = ytState.activeWeekOffset + direction;
  console.log(`moveToMonday:next_offset=${next_offset}`);

  slideWeekWrap(target_x, () => {
    if (setActiveWeek(next_offset)) {
      return;
    }
    doGet(path, { date: d1_str, sde_align: "top" });
  });
};
