/**
 *   (c) 2026 ytani01
 */

// 横ゲージ (TODO-083)

// 横ゲージ (TODO-058)。以前は ``main_handler.py`` にも同じ定数・同じ式が
// あったが、二重に持つのをやめて JavaScript 側だけに寄せた (TODO-078)
//
// 外へ出すもの (他ファイル・テンプレートから使うもの):
//   mondayOf()         -- week.js (weekOffsetOfDate)・
//                        main-page.js (homeButtonHdr)
//   dispGauge()        -- week.js (setActiveWeek)・main-page.js (onloadHdr)
//   dispGaugeMarks()   -- main-page.js (onloadHdr)
//   gaugeBarPointerDownHdr / gaugeBarPointerMoveHdr / gaugeBarPointerUpHdr /
//   gaugeBarPointerCancelHdr -- main-page.js が window の pointerdown / pointermove /
//                              pointerup / pointercancel に登録する (TODO-178)
//   ほかの定数・関数 (DAYS_* / days2xPercent / xPercent2days / GAUGE_MARKS /
//     gaugeDiffLabel / setGaugeNeedles / setGaugeNoTransition /
//     setGaugePosition / GAUGE_START_KEY / get・setGaugeStart /
//     placeGaugeWithoutTransition) はこのファイル内だけで使う
// 外から使うもの (nav.js は base.html でこのあとに読み込まれるが、
//   呼ぶのは実行時なので前方参照でよい):
//   shiftDays() (nav.js)              -- mondayOf・gaugeBarPointerUpHdr
//   getLocaltimeDateString() (nav.js) -- setGaugePosition・dispGauge・gaugeBarPointerUpHdr
//   calcDays() (nav.js)              -- setGaugePosition
//   scrollToDate() (nav.js)          -- gaugeBarPointerUpHdr
//   weekOffsetOfDate() (week.js)      -- gaugeBarPointerMoveHdr (一定時間後の追従判定)
//   gauge_follow_msec (main.html の <script>) -- startGaugeBarFollowTimer
//   ytState (state.js)               -- ytState.elGaugeRs
//   hasBlockOfDate() (month.js)       -- gaugeBarPointerMoveHdr (月間表示での追従判定)
(() => {
  const ytsched = window.ytsched;

  window.ytsched.DAYS_YEAR = 365.25;
  const DAYS_YEAR = ytsched.DAYS_YEAR;
  const DAYS_MONTH = DAYS_YEAR / 12;
  const DAYS_GAUGE_MAX = DAYS_YEAR * 30;
  // 中心の近くをどれだけ詰めるか (TODO-059)
  const DAYS_GAUGE_K = 10.0;

  /**
   * 今週の中心からの左右のずれを、ゲージの幅に対する割合 (%) で返す。
   * 頭打ちあり (TODO-058)。
   *
   * @param {number} days
   *
   * @return {number} xPercent
   */
  window.ytsched.days2xPercent = (days) => {
    // console.log(`days=${days}`);
    let xPercent =
      (50.0 * Math.log10(1 + Math.abs(days) / DAYS_GAUGE_K)) /
      Math.log10(1 + DAYS_GAUGE_MAX / DAYS_GAUGE_K);
    xPercent = Math.min(xPercent, 50.0);

    if (days < 0) {
      return -xPercent;
    }
    return xPercent;
  };
  /**
   * ``days2xPercent()`` の逆算 (TODO-074)。ゲージの帯をタップしたときに、
   * その位置 (中央からの割合 %) から、今週の月曜との日数の差を出すために使う。
   * 同じ式・同じ定数 (``DAYS_GAUGE_K`` / ``DAYS_GAUGE_MAX``) の逆関数で、
   * 頭打ちは無い (``xPercent`` は呼び出し側で -50〜+50 に収まっている前提)。
   *
   * @param {number} xPercent
   *
   * @return {number} days
   */
  window.ytsched.xPercent2days = (xPercent) => {
    const abs_xPercent = Math.abs(xPercent);
    const exponent =
      (abs_xPercent / 50.0) * Math.log10(1 + DAYS_GAUGE_MAX / DAYS_GAUGE_K);
    const abs_days = DAYS_GAUGE_K * (Math.pow(10, exponent) - 1);

    if (xPercent < 0) {
      return -abs_days;
    }
    return abs_days;
  };

  // ゲージの目盛りの一覧 (TODO-058)。以前は ``main_handler.py`` の
  // ``GAUGE`` がテンプレートへ渡していたが、同じ一覧を JavaScript 側だけに
  // 寄せた (TODO-078)
  const GAUGE_MARKS = [
    { label: "-30y", days: -DAYS_YEAR * 30 },
    { label: "-10y", days: -DAYS_YEAR * 10 },
    { label: "-3y", days: -DAYS_YEAR * 3 },
    { label: "-1y", days: -DAYS_YEAR },
    { label: "-4m", days: -DAYS_MONTH * 4 },
    { label: "-1m", days: -DAYS_MONTH },
    { label: "-1w", days: -7 },
    { label: "+1w", days: +7 },
    { label: "+1m", days: +DAYS_MONTH },
    { label: "+4m", days: +DAYS_MONTH * 4 },
    { label: "+1y", days: +DAYS_YEAR },
    { label: "+3y", days: +DAYS_YEAR * 3 },
    { label: "+10y", days: +DAYS_YEAR * 10 },
    { label: "+30y", days: +DAYS_YEAR * 30 },
  ];

  /**
   * ゲージの目盛り (``.my-gauge-label``) を ``.my-gauge-bar`` の中へ描く
   * (TODO-078)。読み込み時に一度だけ呼べばよい (目盛りの位置は日付に
   * よらない)。
   *
   * 帯はヘッダーとフッターの直上に 1 つずつあるので、見つかった帯すべてに
   * 描く (TODO-187)。検索モードでは ``.my-gauge-bar`` が無いので、
   * そのときは何もしない。
   */
  window.ytsched.dispGaugeMarks = () => {
    for (const elGaugeBar of document.querySelectorAll(".my-gauge-bar")) {
      for (const mark of GAUGE_MARKS) {
        const elMark = document.createElement("div");
        elMark.className = "my-gauge-label";
        elMark.style.left = `${(50 + ytsched.days2xPercent(mark.days)).toFixed(2)}%`;
        elMark.textContent = mark.label;
        elGaugeBar.appendChild(elMark);
      }
    }
  };

  /**
   * ``date_str`` を含む週の月曜 (Localtime) を返す (TODO-049)。
   *
   * @param {String} date_str   'YYYY-mm-dd' or 'YYYY/mm/dd'
   *
   * @return {Date} monday
   */
  window.ytsched.mondayOf = (date_str) => {
    const d = new Date(date_str.split("/").join("-"));
    let wday = d.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
      wday = 7; // Sun: 0 --> 7
    }
    return ytsched.shiftDays(d, 1 - wday);
  };

  /**
   * 今週からの差を、針に出す文字にする (TODO-066)。今週のときは ``±0``。
   *
   * 単位は差の大きさで切り替える (TODO-072)。1 ヶ月に届かないうちは
   * 週数 (``+3w``)、1 ヶ月から 1 年までは月数 (``+1.2m``)、1 年からは
   * 年数 (``+1.2y``)。月と年は小数点以下 1 桁。
   *
   * 以前は Python 側 (``main_handler.py`` の ``calc_gauge_label()``) にも
   * 同じ区切り・同じ書き方の関数があったが、二重に持つのをやめて
   * JavaScript 側だけに寄せた (TODO-078)。
   *
   * @param {number} days   今週の月曜からの日数 (7 の倍数)
   *
   * @return {String} label
   */
  window.ytsched.gaugeDiffLabel = (days) => {
    if (days === 0) {
      return "\u00b10";
    }

    const sign = days > 0 ? "+" : "-";
    const abs_days = Math.abs(days);

    if (abs_days < DAYS_MONTH) {
      return `${sign}${abs_days / 7}w`;
    }
    if (abs_days < DAYS_YEAR) {
      return `${sign}${(abs_days / DAYS_MONTH).toFixed(1)}m`;
    }
    return `${sign}${(abs_days / DAYS_YEAR).toFixed(1)}y`;
  };

  /**
   * 針をすべてのゲージへ同じ位置・同じラベルで置く (TODO-187)。
   * ゲージはヘッダーとフッターの直上に 1 つずつあり、上下が必ず同じ
   * 見た目になるように、まとめてここで書き換える。
   *
   * @param {number} rel_days   今週の月曜からの日数
   */
  const setGaugeNeedles = (rel_days) => {
    const left = `${50 + ytsched.days2xPercent(rel_days)}%`;
    // どちらも月曜なので、7 で割り切れる
    const label = ytsched.gaugeDiffLabel(Math.round(rel_days / 7) * 7);

    for (const elGaugeR of ytsched.ytState.elGaugeRs) {
      elGaugeR.style.left = left;

      const elLabel = elGaugeR.querySelector(".my-gauge-r-label");
      if (elLabel) {
        elLabel.textContent = label;
      }
    }
  };

  /**
   * ``.my-gauge-r-no-transition`` を、すべての針に付ける・外す
   * (TODO-187)。
   *
   * @param {boolean} flag   true なら付ける、false なら外す
   */
  const setGaugeNoTransition = (flag) => {
    for (const elGaugeR of ytsched.ytState.elGaugeRs) {
      elGaugeR.classList.toggle("my-gauge-r-no-transition", flag);
    }
  };

  /**
   * 針の位置 (``left``) を計算してセットする。``transition`` は
   * 掛けたまま (TODO-049)。針の上のラベル (今週からの差) も、
   * ここで書き換える。位置は入れ物 (``.my-gauge-r``) が持っているので、
   * ラベルは黙って一緒に動く (TODO-066)。
   *
   * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい。
   *   月曜へ丸めてから、今週の月曜との差を見る)
   */
  const setGaugePosition = (date_str) => {
    const monday = ytsched.mondayOf(date_str);
    const this_monday = ytsched.mondayOf(
      ytsched.getLocaltimeDateString(new Date()),
    );

    setGaugeNeedles(ytsched.calcDays(this_monday, monday));
  };

  // 次にページを読み込んだとき、針を置き始める位置 (週の月曜)。
  // ページの読み直しをまたいで残るのはこれだけなので、読み直しのあと
  // 針をどこから動かして見せるかは、ここに書いてある値で決まる
  // (TODO-180)。
  //
  // 以前は「直前に見ていた週」(``ytsched_gauge_monday``) を持ち、それを
  // 出発点に流用していた (TODO-049)。ドラッグで飛んだときは「直前に見て
  // いた週」と「針の出発点」が違うので、意味を出発点のほうに寄せた
  const GAUGE_START_KEY = "ytsched_gauge_start";

  /**
   * ``sessionStorage`` から針の出発点を読む。
   *
   * Safari の「すべての Cookie をブロック」設定や、``allow-same-origin``
   * の無い ``<iframe>`` では ``sessionStorage`` へのアクセスが
   * ``SecurityError`` を投げる。読めなければ「出発点は不明」として
   * ``null`` を返すだけにする (TODO-049)。
   *
   * @return {String | null}
   */
  const getGaugeStart = () => {
    try {
      return sessionStorage.getItem(GAUGE_START_KEY);
    } catch (e) {
      console.log(`getGaugeStart: ${e}`);
      return null;
    }
  };

  /**
   * ``sessionStorage`` へ針の出発点を書く。書けなくても黙って諦める
   * (TODO-049。理由は ``getGaugeStart()`` を参照)。
   *
   * @param {String} monday_str   'YYYY-mm-dd'
   */
  const setGaugeStart = (monday_str) => {
    try {
      sessionStorage.setItem(GAUGE_START_KEY, monday_str);
    } catch (e) {
      console.log(`setGaugeStart: ${e}`);
    }
  };

  /**
   * ``transition`` を効かせずに、いったんその位置へ針を置く。
   *
   * レイアウトを確定させるのに ``getBoundingClientRect()`` を使う
   * (TODO-060)。確定しないまま ``transition`` が戻ると、CSS の初期値
   * (``left: 50%``、つまり中央) から補間が始まってしまう。
   * 針が ``<svg>`` だったころは ``offsetHeight`` が ``undefined`` を
   * 返してレイアウトが確定せず、これで踏んだ (いまは針とラベルを
   * まとめた ``<div>``。TODO-066)。
   *
   * 針は上下に 1 つずつあるので、レイアウトの確定もそれぞれに対して
   * 行う (TODO-187)。
   *
   * @param {String} date_str   'YYYY-mm-dd'
   */
  const placeGaugeWithoutTransition = (date_str) => {
    setGaugeNoTransition(true);
    setGaugePosition(date_str);
    for (const elGaugeR of ytsched.ytState.elGaugeRs) {
      elGaugeR.getBoundingClientRect(); // 強制的にレイアウトを確定させる
    }
    setGaugeNoTransition(false);
  };

  // ページを読み込んでから、一度でも針を置いたか (TODO-180)。
  // ``sessionStorage`` の出発点を使うのは、読み込んだあとの 1 回だけ。
  // 2 回目からは針が今いる位置から動かせばよい
  let gaugePlaced = false;

  /**
   * ゲージの針を動かす。
   *
   * ドラッグ中は針に触らず、出発点の記録だけを済ませて返す (TODO-178)。
   * ドラッグの途中で setActiveWeek() を通ると、追従で dispGauge() が
   * 呼ばれて針が勝手に動く。
   *
   * ページを読み込んでから初めての呼び出しでは、``sessionStorage`` に
   * 残っている出発点 (``GAUGE_START_KEY``) へ ``transition`` を効かせず
   * に針を置いてから、次のフレームで今の週へ動かす (TODO-049)。
   * ``transition`` だけでは針の初期値が "auto" のままで補間が起きず、
   * 動いて見えない。出発点が今の週と同じなら、動かす先が無いので
   * そのまま置く。``sessionStorage`` が使えない環境でも、針の位置を
   * 合わせること自体は続ける (``getGaugeStart()``/``setGaugeStart()``
   * が例外を握りつぶす)。
   *
   * 2 回目からは、針が今いる位置から目的地へ動かす。以前はここを
   * 「針が ``style.left`` を持っているか」で見分けていたが (TODO-179)、
   * 読み直した直後かどうかを当てるには間接的で、ページの読み直しを
   * はさむドラッグで見分けを誤っていた (TODO-180)。
   *
   * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい)
   */
  window.ytsched.dispGauge = (date_str) => {
    // 検索モードでは帯が出ないので、針が 1 つも無い (TODO-058・TODO-187)
    if (ytsched.ytState.elGaugeRs.length === 0) {
      return;
    }

    if (!date_str) {
      for (const elGaugeR of ytsched.ytState.elGaugeRs) {
        elGaugeR.style.display = "none";
      }
      return;
    }

    const monday_str = ytsched.getLocaltimeDateString(
      ytsched.mondayOf(date_str),
    );

    // ドラッグ中は針に触らない (TODO-178)。読み直しになったときの
    // 出発点だけは、追従した先の週にしておく
    if (gaugeBarDragStart) {
      setGaugeStart(monday_str);
      return;
    }

    if (!gaugePlaced) {
      gaugePlaced = true;
      const start_str = getGaugeStart();
      setGaugeStart(monday_str);

      if (start_str && start_str !== monday_str) {
        placeGaugeWithoutTransition(start_str);
        requestAnimationFrame(() => {
          setGaugePosition(monday_str);
        });
        return;
      }

      // 動かす先が無いので、そのまま置く。``setGaugePosition()`` を直に
      // 呼ぶと、針の ``left`` が CSS の初期値 (``left: 50%``) のままな
      // ので、中央から目的地まで transition が掛かる (TODO-060)
      placeGaugeWithoutTransition(monday_str);
      return;
    }

    setGaugeStart(monday_str);
    setGaugePosition(monday_str);
  };

  // ドラッグの状態 (TODO-178)
  let gaugeBarDragStart = null; // { clientX, t, pointerId, elBar } または null
  let gaugeBarDragMonday = null; // ドラッグ中の現在の週の月曜 ('YYYY-mm-dd')
  let gaugeBarFollowTimeoutId = null; // 一定時間止まったあとの追従タイマー
  let gaugeBarHistoryPushed = false; // ドラッグ中に履歴を積んだか

  /**
   * 帯の clientX からその位置の週の月曜を計算する (TODO-178)。
   * down / move / up で使い回す。
   *
   * 帯はヘッダーとフッターの直上に 1 つずつあるので、矩形は
   * pointerdown で触れた帯のものを使う (TODO-187)。上の帯で決め打ちに
   * すると、下の帯をドラッグしたときに位置が合わない。
   *
   * @param {number} clientX
   * @param {Element} el_bar   触れた帯 (``.my-gauge-bar``)
   * @return {String | null}   週の月曜 ('YYYY-mm-dd')、帯が無ければ null
   */
  const mondayFromClientX = (clientX, el_bar) => {
    if (!el_bar) {
      return null;
    }

    const rect = el_bar.getBoundingClientRect();
    const x_percent = ((clientX - rect.left) / rect.width) * 100 - 50;
    const days = ytsched.xPercent2days(x_percent);

    const this_monday = ytsched.mondayOf(
      ytsched.getLocaltimeDateString(new Date()),
    );
    const target_date = ytsched.shiftDays(this_monday, Math.round(days));
    const monday = ytsched.mondayOf(
      ytsched.getLocaltimeDateString(target_date),
    );

    return ytsched.getLocaltimeDateString(monday);
  };

  /**
   * 現在のドラッグの週が先読み済み (DOM にある) かどうかを調べる
   * (TODO-178)。週表示と月間表示で判定方法が違う。
   *
   * @return {boolean}
   */
  const gaugeBarDragWeekIsLoaded = () => {
    if (!gaugeBarDragMonday) {
      return false;
    }

    if (ytsched.view_month) {
      // 月間表示: 月間パネルが DOM にあるか (TODO-178)
      return ytsched.hasBlockOfDate(gaugeBarDragMonday);
    }

    // 週間表示: weekOffsetOfDate() が見つかるか
    return ytsched.weekOffsetOfDate(gaugeBarDragMonday) !== null;
  };

  const DEF_GAUGE_FOLLOW_MSEC = 500;

  /**
   * 一定時間止まったあとの追従タイマーを張る (TODO-178)。
   * 待ち時間は ``ytsched.gauge_follow_msec`` (main.html)。
   * pointerdown と、pointermove で移動先の週が変わったときに呼ばれる
   * (TODO-186)。
   */
  const startGaugeBarFollowTimer = () => {
    clearTimeout(gaugeBarFollowTimeoutId);
    if (gaugeBarDragWeekIsLoaded()) {
      const followMsec =
        Number(ytsched.gauge_follow_msec) || DEF_GAUGE_FOLLOW_MSEC;
      gaugeBarFollowTimeoutId = setTimeout(() => {
        if (gaugeBarDragMonday && gaugeBarDragWeekIsLoaded()) {
          const push_flag = !gaugeBarHistoryPushed;
          if (push_flag) {
            gaugeBarHistoryPushed = true;
          }
          ytsched.scrollToDate(
            location.pathname,
            gaugeBarDragMonday,
            "top",
            "instant",
            push_flag,
          );
        }
      }, followMsec);
    }
  };

  /**
   * ドラッグが始まった (TODO-178)。帯の上を pointerdown したら、
   * 状態を持つ。window への capture委譲で拾う。既にドラッグ中なら何もしない。
   *
   * @param {PointerEvent} event
   */
  window.ytsched.gaugeBarPointerDownHdr = (event) => {
    const el =
      event.target && event.target.closest
        ? event.target.closest(".my-gauge-bar")
        : null;

    if (!el) {
      return;
    }

    // 左ボタン以外は何もしない
    if (event.button !== 0) {
      return;
    }

    // 既にドラッグ中なら何もしない(2 本目の指など)
    if (gaugeBarDragStart) {
      return;
    }

    event.preventDefault(); // マウスでドラッグ中に文字が選択されないように
    gaugeBarDragStart = {
      clientX: event.clientX,
      t: Date.now(),
      pointerId: event.pointerId,
      // 触れた帯。pointermove / pointerup でも同じ帯の矩形を使う
      // (TODO-187)
      elBar: el,
    };
    gaugeBarDragMonday = mondayFromClientX(event.clientX, el);
    gaugeBarHistoryPushed = false; // ドラッグ開始時に履歴フラグをリセット

    // transition を外す (ドラッグ中は指に追従するため)
    setGaugeNoTransition(true);

    // 一定時間止まったら追従
    startGaugeBarFollowTimer();
  };

  /**
   * ドラッグ中に針を動かす (TODO-178)。
   *
   * @param {PointerEvent} event
   */
  window.ytsched.gaugeBarPointerMoveHdr = (event) => {
    if (!gaugeBarDragStart) {
      return;
    }

    // pointerId が異なれば何もしない(2 本目の指など)
    if (event.pointerId !== gaugeBarDragStart.pointerId) {
      return;
    }

    // ボタンが離れていたら後始末する (ウィンドウ外で離した場合など)
    if (!(event.buttons & 1)) {
      gaugeBarDragStart = null;
      gaugeBarDragMonday = null;
      gaugeBarHistoryPushed = false;
      clearTimeout(gaugeBarFollowTimeoutId);
      setGaugeNoTransition(false);
      ytsched.dispGauge(ytsched.ytState.activeMonday);
      return;
    }

    const prev_monday = gaugeBarDragMonday;
    gaugeBarDragMonday = mondayFromClientX(
      event.clientX,
      gaugeBarDragStart.elBar,
    );
    if (!gaugeBarDragMonday) {
      return;
    }

    // 針だけを動かす (dispGauge は呼ばない)
    const this_monday = ytsched.mondayOf(
      ytsched.getLocaltimeDateString(new Date()),
    );
    const target_monday = ytsched.mondayOf(gaugeBarDragMonday);
    const rel_days = ytsched.calcDays(this_monday, target_monday);

    setGaugeNeedles(rel_days);

    // 一定時間止まったら追従 (TODO-178)。
    // 張り直すのは移動先の週が変わったときだけ (TODO-186)。指を押さえた
    // ままでも微細な揺れで pointermove が出続けるので、毎回張り直すと
    // タイマーが発火しない
    if (gaugeBarDragMonday !== prev_monday) {
      startGaugeBarFollowTimer();
    }
  };

  /**
   * ドラッグが終わった (TODO-178)。指を離したら、最後の週へ移動する。
   *
   * @param {PointerEvent} event
   */
  window.ytsched.gaugeBarPointerUpHdr = (event) => {
    if (!gaugeBarDragStart) {
      return;
    }

    // pointerId が異なれば何もしない(別の指など)
    if (event.pointerId !== gaugeBarDragStart.pointerId) {
      return;
    }

    clearTimeout(gaugeBarFollowTimeoutId);
    gaugeBarFollowTimeoutId = null;

    // transition を戻す
    setGaugeNoTransition(false);

    gaugeBarDragStart = null;

    if (!gaugeBarDragMonday) {
      gaugeBarHistoryPushed = false;
      return;
    }

    // 移り先が先読みの範囲の外だと、``scrollToDate()`` はページを
    // 読み直す。針は読み直しで消えるので、離した位置を出発点として
    // 残しておく (TODO-180)。読み直した先では出発点と目的地が同じに
    // なり、針は動かずにそこへ出る。読み直しにならなければ、この
    // あとの ``dispGauge()`` が同じ値で上書きする
    setGaugeStart(
      ytsched.getLocaltimeDateString(ytsched.mondayOf(gaugeBarDragMonday)),
    );

    // 最後の週へ移動 (TODO-178)
    // ドラッグ 1 回で履歴は 1 つだけ積む
    const push_flag = !gaugeBarHistoryPushed;
    ytsched.scrollToDate(
      location.pathname,
      gaugeBarDragMonday,
      "top",
      "smooth",
      push_flag,
    );
    gaugeBarDragMonday = null;
    gaugeBarHistoryPushed = false;
  };

  /**
   * ドラッグが割り込まれた (TODO-178)。針を元の週へ戻す。
   *
   * @param {PointerEvent} event
   */
  window.ytsched.gaugeBarPointerCancelHdr = (event) => {
    if (!gaugeBarDragStart) {
      return;
    }

    // pointerId が異なれば何もしない(別の指など)
    if (event.pointerId !== gaugeBarDragStart.pointerId) {
      return;
    }

    clearTimeout(gaugeBarFollowTimeoutId);
    gaugeBarFollowTimeoutId = null;

    // transition を戻す
    setGaugeNoTransition(false);

    gaugeBarDragStart = null;
    gaugeBarDragMonday = null;
    gaugeBarHistoryPushed = false;

    // 針を現在の週へ戻す (TODO-178)
    ytsched.dispGauge(ytsched.ytState.activeMonday);
  };
})();
