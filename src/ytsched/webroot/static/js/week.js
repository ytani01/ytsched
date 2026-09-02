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
//   moveToMonday()     -- moveActiveDate (このファイル)・
//                         main-page.js (startAutoPageTurn)
//   moveActiveDate()   -- swipe.js (swipeFinish)・keyboard.js (keyHdr)・
//                         main-page.js (pageTurnPointerUpHdr)
//   moveActiveMonth()  -- swipe.js (swipeFinish、ミニカレンダーの上での
//                         スワイプ・ドラッグ、TODO-136)
//   weekPanelOf() / cancelActiveSlide / SWIPE_SLIDE_MSEC / mondayDaysInMonth()
//     はこのファイル内だけで使う
// 外から使うもの:
//   ytState (state.js)          -- elWeekWrap・activeWeekOffset・activeMonday
//   mondayOf() (gauge.js)       -- weekOffsetOfDate
//   dispGauge() (gauge.js)      -- setActiveWeek
//   getLocaltimeDateString() / getLocaltimeString() / shiftDays() (nav.js)
//     -- weekOffsetOfDate・moveToMonday・moveActiveDate・moveActiveMonth
//   pushDateInUrl() / scrollToId() (nav.js) -- setActiveWeek
//   doGet() (nav.js)            -- moveToMonday・moveActiveDate
//   scrollToDate() (nav.js)     -- moveActiveMonth (TODO-136)
//   window.ytsched.search_date_to (main.html の <script>) -- moveActiveDate
//   window.ytsched.view_month (main-page.js の onloadHdr()) -- moveActiveDate・
//     weekOffsetOfDate (TODO-137)
//   moveActiveBlock() (month.js) -- moveActiveDate (月間表示、TODO-137)

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
    // 月間表示のパネルは data-monday に週の月曜ではなくブロックの
    // 基準日 (base_date) を持つので、これで探すと取り違える。
    // 月間表示のパネル探しは setActiveBlockOfDate() (month.js) に
    // 任せる (TODO-137)
    if (ytsched.view_month) {
      return null;
    }
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
    const panels =
      ytsched.ytState.elWeekWrap.querySelectorAll(".my-week-panel");
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
   * 週に付いて回るもの (``ytState.activeMonday``・ヘッダーのゲージ) を、
   * その週の月曜に揃える。
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

    // 画面に出ている #cur_day を合わせる (TODO-111)
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

  /**
   * 週を送るか、検索の基準日を動かすかを決める (TODO-117)。
   *
   * ``ytsched.search_date_to`` (main.html の ``data-search-date-to``、
   * 検索モードのときだけ付く) があれば、月曜へ丸めずに検索の基準日
   * (``date_to``) を ±7 日するだけ (TODO-116)。``moveToMonday()`` を
   * 通らないので、週枠を滑らせるアニメーションも出ない。
   * それ以外は今までどおり ``moveToMonday()`` を呼ぶ。
   *
   * フッターの ＜ ＞・キーの ← →・左右のスワイプ・ドラッグの、
   * どの経路もここを通る。
   *
   * @param {number} direction
   * @param {String} path
   */
  window.ytsched.moveActiveDate = (direction, path) => {
    // 月間表示では 6 ヶ月単位で送る (TODO-137)。フッターの ＜ ＞・
    // キーの ← →・スワイプ・自動ページ送りは、どれもこの関数を通るので、
    // ここで分けるだけで全部が月単位になる
    if (ytsched.view_month) {
      ytsched.moveActiveBlock(direction, path);
      return;
    }
    if (ytsched.search_date_to) {
      let d1 = new Date(ytsched.search_date_to);
      d1 = ytsched.shiftDays(d1, direction * 7);
      const d1_str = ytsched.getLocaltimeDateString(d1);
      ytsched.doGet(path, { date: d1_str, sde_align: "top" });
      return;
    }
    ytsched.moveToMonday(direction, path);
  };

  /**
   * ``year``/``month`` (``month`` は Date と同じ 0 始まり) の月に
   * 収まる月曜の、日 (1-31) を古い順に返す (TODO-136)。
   *
   * @param {number} year
   * @param {number} month
   * @return {number[]}
   */
  const mondayDaysInMonth = (year, month) => {
    const days = [];
    const d = new Date(year, month, 1);
    while (d.getMonth() === month) {
      if (d.getDay() === 1) {
        days.push(d.getDate());
      }
      d.setDate(d.getDate() + 1);
    }
    return days;
  };

  /**
   * ミニカレンダーの領域での左右のスワイプ・ドラッグで、1 ヶ月単位に
   * 移動する (TODO-136)。
   *
   * **月の中で「何番目の月曜か」を保ったまま、月だけ進める/戻す。**
   * ``activeMonday`` を月単位でずらしてから週の月曜へ丸める案
   * (``Date.setMonth()`` → 週の月曜へ丸める) も考えたが、丸めが
   * 月の境界を越えて元の月 (時には 2 か月前) へ戻ってしまう日付が
   * 少なくなかった (reviewer の指摘、2021〜2030 年の月初の月曜だけでも
   * 前進 42 件・後退 71 件で発生)。
   *
   * 代わりに、``activeMonday`` がその月の何番目の月曜か
   * (``mondayDaysInMonth()`` の何番目か) を求め、ずらした先の月でも
   * 同じ番目の月曜へ移る。ずらした先の月の月曜の数がそれより少なければ
   * (4 週の月から 5 週の月へ動いたときなど)、その月の最後の月曜に
   * 留める。この方法なら、結果の月が必ずずらした先の月そのものになる
   * (2021〜2030 年の全ての月曜で確認済み)。
   *
   * ミニカレンダーのセルをタップしたときと同じ ``scrollToDate()`` に
   * 乗せるので、読み込み範囲にあればそのまま移り、無ければ読み直す。
   *
   * 検索モードではミニカレンダーを出さない (TODO-104) ので、
   * ``moveActiveDate()`` と違って検索の基準日を動かす分岐は無い。
   *
   * @param {number} direction
   * @param {String} path
   */
  window.ytsched.moveActiveMonth = (direction, path) => {
    const cur = new Date(ytsched.ytState.activeMonday);
    let wday = cur.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
      wday = 7; // Sun: 0 --> 7
    }
    // ``activeMonday`` が月曜とは限らない (TODO-138)。その週の月曜へ
    // 丸めてから月内の何番目かを求める (moveToMonday() と同じ考え方)
    const monday = ytsched.shiftDays(cur, 1 - wday);
    const year = monday.getFullYear();
    const month = monday.getMonth();
    const curDays = mondayDaysInMonth(year, month);
    const idx = curDays.indexOf(monday.getDate());

    const total = year * 12 + month + direction;
    const targetYear = Math.floor(total / 12);
    const targetMonth = ((total % 12) + 12) % 12;
    const targetDays = mondayDaysInMonth(targetYear, targetMonth);
    const targetDay = targetDays[Math.min(idx, targetDays.length - 1)];

    const target = new Date(targetYear, targetMonth, targetDay);
    const target_str = ytsched.getLocaltimeDateString(target);
    ytsched.scrollToDate(path, target_str, "top");
  };
})();
