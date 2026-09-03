/**
 *   (c) 2026 ytani01
 */

// main.html だけで使う関数・リスナー登録 (TODO-083)。テンプレートの
// 値は #main の data 属性から読み込む。
//
// 外へ出すもの:
//   homeButtonHdr() -- main.html の #home_button の onMouseDown
//   changeSearchN() -- main.html の #search_n_in の onchange (検索モード)
//   window.ytsched.view_month -- onloadHdr() が #main の data-view から
//     入れる。week.js・nav.js・swipe.js が読む (TODO-137)
//   onloadHdr()・keyHdr (keyboard.js)・popstateHdr (nav.js)・swipe.js の各
//     ハンドラと、gauge.js の gaugeBarPointer* ハンドラを、このファイル末尾で
//     window のイベントに登録する (TODO-178)。
//     ページ送り関連 (startAutoPageTurn / stopAutoPageTurn /
//     pageTurnPointerDownHdr / pageTurnPointerUpHdr / pageTurnPointerCancelHdr)
//     と homeTapPointerDownHdr (TODO-165) は、このファイル内だけで使う
// 外から使うもの:
//   search_str0 / search_date_to / today_str / auto_turn_msec
//     (main.html の <script>)
//   url_prefix (base.html の <script>)
//   ytState (state.js)  -- elLoadingSpinner・elMain・elWeekWrap・
//                          activeWeekOffset・activeMonday・elGaugeR0
//   loadingSpinner() (spinner.js)             -- onloadHdr
//   doGet() / doPost() / scrollToDate() (nav.js)
//   getLocaltimeDateString() (nav.js)         -- homeButtonHdr
//   mondayOf() (gauge.js)                     -- homeButtonHdr
//   popstateHdr() (nav.js)                    -- popstate に登録
//   layoutWeeks() / moveToMonday() / moveActiveDate() (week.js)
//   dispGauge() / dispGaugeMarks() (gauge.js) -- onloadHdr
//   keyHdr() (keyboard.js)                    -- keydown に登録
//   swipe.js の touch* / mouse* の 7 ハンドラ -- 各イベントに登録

(() => {
  const ytsched = window.ytsched;
  let clickCount = 0;

  // 検索画面はホームボタンのシングルタップでもページを読み直す。その
  // 前後でダブルタップの判定を引き継ぐための sessionStorage のキー
  // (TODO-165)
  const SEARCH_HOME_TAP_KEY = "ytsched_search_home_tap";

  // 検索画面でダブルタップと見なす間隔 (msec)。ページの読み直しをまたぐ
  // ぶん、通常表示の 350 では届かない。フッターの ◀▶ (TODO-123) と
  // 揃えて 1000 にする
  const SEARCH_HOME_DOUBLE_TAP_MSEC = 1000;

  /**
   * 検索画面で直前にホームボタンを押した時刻を読む。
   *
   * ``sessionStorage`` が使えないときは、ダブルタップを引き継がない
   * だけにする (gauge.js の ``getGaugeMonday()`` と同じ考え方)。
   *
   * @return {number}   押した記録が無ければ 0
   */
  const getSearchHomeTapMsec = () => {
    try {
      return Number(sessionStorage.getItem(SEARCH_HOME_TAP_KEY)) || 0;
    } catch (e) {
      console.log(`getSearchHomeTapMsec: ${e}`);
      return 0;
    }
  };

  /**
   * 検索画面でホームボタンを押した時刻を残す。``0`` なら記録を消す。
   *
   * @param {number} msec
   */
  const setSearchHomeTapMsec = (msec) => {
    try {
      if (msec) {
        sessionStorage.setItem(SEARCH_HOME_TAP_KEY, String(msec));
      } else {
        sessionStorage.removeItem(SEARCH_HOME_TAP_KEY);
      }
    } catch (e) {
      console.log(`setSearchHomeTapMsec: ${e}`);
    }
  };

  /**
   * 既定のトップ画面 (今週の週間表示) を読み直す (TODO-165)。
   *
   * **``search_str`` を空にして POST する。** 検索モードかどうかは
   * サーバが ``conf.json`` の ``SearchStr`` で決めているので、``doGet``
   * で読み直しても検索結果が返ってしまう。検索結果の日付欄
   * (``date-post``) と同じ道を通して検索語を消す。
   *
   * ``MainHandler.post()`` はリダイレクト先へ ``sde_align`` を引き継ぐ
   * ので、先頭に合わせるのもそのまま効く。``view`` は ``conf.json`` へ
   * 保存されない (``get_view()``) ので、月間表示からも週間表示へ戻る。
   *
   * @param {String} monday_str
   */
  const reloadHome = (monday_str) => {
    // search_str は URL に載せない (TODO-050)
    ytsched.doPost(ytsched.url_prefix, {
      date: monday_str,
      search_str: "",
      sde_align: "top",
    });
  };

  /**
   * ホームボタン以外を押したら、検索画面のダブルタップの記録を捨てる
   * (TODO-165)。
   *
   * 記録はページの読み直しをまたいで残るので、消さないと「ホーム →
   * 別の操作 → ホーム」が 1 秒に収まったときまでダブルタップと判定して
   * しまう。フッターの ◀▶ が ``pageTurnPointerDownHdr()`` でしている
   * 後始末 (TODO-123) と揃える。
   */
  const homeTapPointerDownHdr = (event) => {
    if (
      event.target &&
      event.target.closest &&
      event.target.closest('[data-action="home"]')
    ) {
      return;
    }
    setSearchHomeTapMsec(0);
  };

  window.ytsched.homeButtonHdr = () => {
    // シングル・ダブルとも、今日ではなく今週の月曜日へ移動する
    // (TODO-105)。週間表示では週の頭が見えているほうが分かりやすい
    const monday_str = ytsched.getLocaltimeDateString(
      ytsched.mondayOf(ytsched.today_str),
    );

    if (ytsched.search_str0) {
      // 検索画面ではシングルタップ自体がページの読み直しを伴う
      // （検索結果は日付範囲が限られていて、通常表示のように前後の週を
      // 先読みしていないため）。読み直しで clickCount が消えてしまうので、
      // タップした時刻を sessionStorage へ残し、読み直した先のページで
      // 2 回目かどうかを判定する (TODO-165)。
      //
      // 1 回目を 350 ミリ秒遅らせて 2 回目を待つやり方 (TODO-164) では、
      // それより遅い 2 回目のタップが読み直しに飲まれてしまい、実機の指
      // では成立しなかった (成立したのはタップ間隔 270 ミリ秒まで)
      const now = Date.now();
      if (now - getSearchHomeTapMsec() < SEARCH_HOME_DOUBLE_TAP_MSEC) {
        // 記録は消さずに残す。トップ画面の読み込みが終わる前に 3 回目を
        // 叩かれたとき、消してあると「1 回目」に戻ってしまい、検索語つき
        // の POST が 2 回目の遷移を上書きして検索画面へ引き戻される
        reloadHome(monday_str);
        return;
      }
      setSearchHomeTapMsec(now);

      // 1 回目は待たずに読み直す (検索語はそのまま)。
      // search_str は URL に載せない (TODO-050)
      ytsched.doPost(ytsched.url_prefix, {
        date: monday_str,
        search_str: document.getElementById("search_str").value,
      });
      return;
    }

    if (!clickCount) {
      // single click
      ++clickCount;
      setTimeout(function () {
        clickCount = 0;
      }, 350);
      ytsched.scrollToDate(ytsched.url_prefix, monday_str, "top");
    } else {
      // double click
      clickCount = 0;

      // データを読み直す (TODO-069)。前後数ヶ月ぶんを DOM に持つ
      // ようになったので、抱えたまま古くなる。ダブルタップが、
      // 手で取り直す道
      reloadHome(monday_str);
    }
  };

  const actionElement = (event) => {
    if (!event.target || !event.target.closest) {
      return null;
    }
    return event.target.closest("[data-action]");
  };

  const actionMouseDownHdr = (event) => {
    const el = actionElement(event);
    if (!el) {
      return;
    }
    switch (el.dataset.action) {
      case "search-prev":
        ytsched.doGetDate(
          ytsched.url_prefix,
          el.dataset.date,
          Number(el.dataset.days),
        );
        break;
      case "date-post":
        ytsched.doPost(ytsched.url_prefix, {
          date: el.dataset.date,
          search_str: "",
        });
        break;
      case "date-edit":
        ytsched.doGet(`${ytsched.url_prefix}edit/`, {
          date: el.dataset.date,
          sde_id: "",
        });
        break;
      case "month-cal":
        ytsched.doPost(ytsched.url_prefix, {
          date: el.dataset.date,
          month_cal: el.dataset.monthCal,
        });
        break;
      case "scroll-date":
        ytsched.scrollToDate(ytsched.url_prefix, el.dataset.date);
        break;
      case "week-date":
        // 月間表示の日付セル。その日を含む週の週間表示へ (TODO-137)。
        // ``view`` は付けない (週間表示で開く)
        ytsched.doGet(ytsched.url_prefix, {
          date: el.dataset.date,
          sde_align: "top",
        });
        break;
      case "month-view":
        // 週間表示のミニカレンダーの "YYYY/MM"。その月を含む 6 ヶ月
        // ブロックの月間表示へ (TODO-137)
        ytsched.doGet(ytsched.url_prefix, {
          date: el.dataset.date,
          view: "month",
        });
        break;
      case "edit-sde":
        ytsched.doGet(`${ytsched.url_prefix}edit/`, {
          date: el.dataset.date,
          sde_id: el.dataset.sdeId,
          todo_flag: el.dataset.todoFlag,
        });
        break;
      case "home":
        ytsched.homeButtonHdr();
        break;
      case "submit-form":
        ytsched.doSubmit(el.dataset.formId);
        break;
      case "clear-search":
        document.getElementById("search_str").value = "";
        break;
    }
  };

  const actionChangeHdr = (event) => {
    const el = actionElement(event);
    if (!el) {
      return;
    }
    switch (el.dataset.action) {
      case "search-date":
        ytsched.doGetDate(ytsched.url_prefix, el.value);
        break;
      case "search-n":
        ytsched.changeSearchN(el.value);
        break;
      case "submit-form":
        ytsched.doSubmit(el.dataset.formId);
        break;
    }
  };

  const onloadHdr = (event) => {
    console.log(`onloadHdr(${event}`);
    ytsched.ytState.elLoadingSpinner =
      document.getElementById("loadingSpinner");
    ytsched.loadingSpinner(false);

    ytsched.ytState.elMain = document.getElementById("main"); // declared in state.js
    ytsched.ytState.elWeekWrap = document.getElementById("week_wrap"); // declared in state.js
    ytsched.search_str0 = ytsched.ytState.elMain.dataset.searchStr0;
    // 検索モードのときだけ #main に付く。検索の基準日 (date_to)。
    // フッターの ＜ ＞ が、月曜へ丸めずにこれを ±7 日する (TODO-116)
    ytsched.search_date_to = ytsched.ytState.elMain.dataset.searchDateTo;
    ytsched.today_str = ytsched.ytState.elMain.dataset.today;
    // 月間表示かどうか (TODO-137)。week.js・nav.js・swipe.js の各分岐が
    // これを見て、週送りを 6 ヶ月単位に切り替える
    ytsched.view_month = ytsched.ytState.elMain.dataset.view === "month";
    ytsched.auto_turn_msec = Number(
      ytsched.ytState.elMain.dataset.autoTurnMsec,
    );
    ytsched.ytState.elMain.addEventListener("mousedown", actionMouseDownHdr);
    ytsched.ytState.elMain.addEventListener("change", actionChangeHdr);
    document
      .querySelector("footer")
      .addEventListener("mousedown", actionMouseDownHdr);
    document
      .querySelector("footer")
      .addEventListener("change", actionChangeHdr);

    // 表示中の週の月曜 (検索表示なら結果の一番古い日)。サーバが
    // #week_wrap の data-monday に入れて渡す (TODO-093)
    ytsched.ytState.activeMonday = ytsched.ytState.elWeekWrap.dataset.monday;

    // 読み込んだ直後は、真ん中の週 (offset 0) を見ている。
    // サーバも同じ形で描いているので並べ直す必要は無いが、
    // ``my-week-near`` はサーバが付けないのでここで付ける (TODO-069)
    ytsched.ytState.activeWeekOffset = 0; // declared in state.js
    ytsched.layoutWeeks();

    const elMenuBar = document.getElementById("menu_bar");
    const menu_bar_height = elMenuBar.offsetHeight;
    document.body.style.paddingBottom = `${menu_bar_height}px`;

    // 週バーは position: fixed なので、その高さぶんを空ける
    // (TODO-055)。body_h を測るより先に入れること。
    // 検索モードでは週バーが無いので、そのときは 0 のまま
    const elWeekBar = document.getElementById("week_bar");
    if (elWeekBar) {
      document.body.style.paddingTop = `${elWeekBar.offsetHeight}px`;
    }

    const body_h = document.body.clientHeight;
    const win_h = document.documentElement.clientHeight;

    ytsched.ytState.elGaugeR0 = document.getElementById("gauge_r"); // declared in state.js
    // 目盛りの位置は日付によらないので、ここで一度だけ描く (TODO-078)
    ytsched.dispGaugeMarks();

    // 検索画面での自動送りは、1 回ごとにページを読み直す。その前の画面が
    // 残した方向があれば、ここから続きを始める (TODO-123)。
    if (ytsched.search_date_to) {
      const direction = getSearchAutoTurnDirection();
      if (direction !== null) {
        startAutoPageTurn(direction);
      }
    }

    if (body_h < win_h) {
      console.log(`body_h=${body_h} < win_h=${win_h}`);
      // 中身が画面より短いときは、#main を画面の高さまで伸ばして、
      // フッターとの間に body の地 (白) が残らないようにする (TODO-176)。
      // #main の地の色は my.css の #main で指定してある
      const fill_h = ytsched.ytState.elMain.offsetHeight + win_h - body_h;
      ytsched.ytState.elMain.style.minHeight = `${fill_h}px`;
      // ゲージの都合で画面が出ないのはおかしいので、dispGauge() より
      // 先に visible にする (TODO-049 reviewer 指摘 1)
      ytsched.ytState.elMain.style.visibility = "visible";
      ytsched.dispGauge(ytsched.ytState.activeMonday);
      return;
    }

    const el_sde_align = document.getElementById("sde_align");
    // 検索モードでは検索の基準日、そうでなければリクエストされた日
    // (#cur_day、week.js の setActiveWeek() が書き換える前の初期値)
    // を使う。activeMonday はその週の月曜であり、リクエストされた
    // 特定の日とは限らない (TODO-162 reviewer 指摘)。
    const date =
      ytsched.search_date_to || document.getElementById("cur_day").value;
    // 読み直したあとの位置合わせは一度で移す。"auto" は CSS の
    // scroll-behavior に従うので、Bootstrap 5 の :root の指定で
    // アニメーションになってしまう (TODO-041)
    // 読み直した直後なので、履歴には積まない (TODO-050)
    ytsched.scrollToDate(
      location.pathname,
      date,
      el_sde_align.value,
      "instant",
      false,
    );

    // 週表示になり、スクロールでの追加読み込みが無くなったので、
    // 検索の有無によらず一度だけゲージを合わせる (TODO-049)
    ytsched.dispGauge(ytsched.ytState.activeMonday);
  }; // onloadHdr()

  window.ytsched.changeSearchN = (val) => {
    console.log(`changeSearchN: val=${val}`);
    // search_n は URL に載せない (TODO-050)
    ytsched.doPost(ytsched.url_prefix, {
      date: ytsched.ytState.activeMonday,
      search_n: val,
    });
  };

  // フッターの ◀▶ のダブルタップで、自動ページ送りを始める (TODO-084)。
  // ボタンは ``onmousedown`` を持たず ``data-page-turn="-1"/"1"`` を持つ
  // だけなので、ボタンがまだ DOM に無い時点でこのスクリプトが評価されても
  // 困らないよう、``pointerdown``/``pointerup`` を window に委譲して拾う

  // ページ送りボタンを押した位置と時刻 (押していなければ null)
  let pageTurnStart = null;

  // 直前にタップしたボタンの向きと時刻 (ダブルタップの判定に使う)
  let lastPageTurnDirection = null;
  let lastPageTurnTapMsec = 0;

  // 自動ページ送りの setInterval の id (走っていなければ null)
  let autoTurnTimerId = null;

  // 検索画面での移動によるページ離脱かどうか。離脱では sessionStorage の
  // 状態を消さず、読み直した先へ引き継ぐ (TODO-123)。
  let pageIsUnloading = false;

  // 検索画面は 1 回送るごとにページを読み直す。その前後でダブルタップと
  // 自動送りの状態を引き継ぐための sessionStorage のキー (TODO-123)。
  const SEARCH_AUTO_TURN_DIRECTION_KEY = "ytsched_search_auto_turn_direction";
  const SEARCH_PAGE_TURN_TAP_KEY = "ytsched_search_page_turn_tap";

  // ダブルタップと見なす間隔 (msec)。homeButtonHdr() のダブルクリック判定
  // (350) と揃える
  const PAGE_TURN_DOUBLE_TAP_MSEC = 350;

  // 検索画面では 1 回目のタップでページを読み直すため、次の画面で
  // 2 回目を受け取るまでには通常のダブルタップ判定より時間がかかる。
  const SEARCH_PAGE_TURN_DOUBLE_TAP_MSEC = 1000;

  // ボタンの上から始めた横の払いを、週送りとして拾わないための、
  // 動いたと見なす最小の距離 (px)
  const PAGE_TURN_MOVE_PX = 30;

  /**
   * 検索画面の自動送りの方向を読む。sessionStorage が使えないときは
   * 自動送りを引き継がないだけにする。
   *
   * @return {number | null}
   */
  const getSearchAutoTurnDirection = () => {
    try {
      const direction = Number(
        sessionStorage.getItem(SEARCH_AUTO_TURN_DIRECTION_KEY),
      );
      return direction === -1 || direction === 1 ? direction : null;
    } catch (e) {
      console.log(`getSearchAutoTurnDirection: ${e}`);
      return null;
    }
  };

  /** @param {number} direction */
  const setSearchAutoTurnDirection = (direction) => {
    try {
      sessionStorage.setItem(SEARCH_AUTO_TURN_DIRECTION_KEY, String(direction));
    } catch (e) {
      console.log(`setSearchAutoTurnDirection: ${e}`);
    }
  };

  /** 検索画面の自動送りとダブルタップの記録を消す。 */
  const clearSearchPageTurnState = () => {
    try {
      sessionStorage.removeItem(SEARCH_AUTO_TURN_DIRECTION_KEY);
      sessionStorage.removeItem(SEARCH_PAGE_TURN_TAP_KEY);
    } catch (e) {
      console.log(`clearSearchPageTurnState: ${e}`);
    }
  };

  /** 走っていれば自動ページ送りを止める。走っていなければ何もしない。 */
  const stopAutoPageTurn = () => {
    if (autoTurnTimerId !== null) {
      clearInterval(autoTurnTimerId);
      autoTurnTimerId = null;
    }
    clearSearchPageTurnState();
  };

  /**
   * 自動ページ送りを始める。
   *
   * ``auto_turn_msec`` ごとに日付を動かす。検索画面では、ページを
   * 読み直したあとも続けられるよう方向を sessionStorage に残す。
   *
   * @param {number} direction
   */
  const startAutoPageTurn = (direction) => {
    if (autoTurnTimerId !== null) {
      clearInterval(autoTurnTimerId);
    }
    if (ytsched.search_date_to) {
      setSearchAutoTurnDirection(direction);
    }
    autoTurnTimerId = setInterval(() => {
      ytsched.moveActiveDate(direction, ytsched.url_prefix);
    }, ytsched.auto_turn_msec);
  };

  /**
   * ページ送りボタンを押したときの、位置と時刻を覚える。
   *
   * ボタンの外を押したときは、走っていた自動ページ送りを止める
   * (画面の他の場所をタップ・クリックしたら止める、の分岐。capture で
   * 拾う)。
   */
  const pageTurnPointerDownHdr = (event) => {
    const el =
      event.target && event.target.closest
        ? event.target.closest("[data-page-turn]")
        : null;

    if (!el) {
      pageTurnStart = null;
      stopAutoPageTurn();
      return;
    }

    pageTurnStart = { x: event.clientX, y: event.clientY, t: Date.now() };
  };

  /**
   * ページ送りボタンを離したときに決める。
   *
   * - 自動ページ送りが走っていれば、止めるだけ (週は送らない)
   * - 押した位置から ``PAGE_TURN_MOVE_PX`` 以上動いていれば、何もしない
   *   (ボタンの上から始めた横の払いを、週送りとして拾わないため)
   * - それ以外は 1 週送る。直前のタップが同じボタンで
   *   ``PAGE_TURN_DOUBLE_TAP_MSEC`` 以内なら、続けて自動ページ送りを
   *   始める
   */
  const pageTurnPointerUpHdr = (event) => {
    const start = pageTurnStart;
    pageTurnStart = null;
    if (!start) {
      return;
    }

    const el =
      event.target && event.target.closest
        ? event.target.closest("[data-page-turn]")
        : null;
    if (!el) {
      return;
    }

    if (autoTurnTimerId !== null) {
      stopAutoPageTurn();
      return;
    }

    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    if (Math.hypot(dx, dy) >= PAGE_TURN_MOVE_PX) {
      return;
    }

    const direction = Number(el.dataset.pageTurn);

    // 検索モードではページを読み直すので、ダブルタップの時刻も
    // sessionStorage へ残す。2 回目はページを動かす前に自動送りを始め、
    // 読み直した先で続ける (TODO-123)。
    if (ytsched.search_date_to) {
      const now = Date.now();
      let lastTap = null;
      try {
        lastTap = JSON.parse(sessionStorage.getItem(SEARCH_PAGE_TURN_TAP_KEY));
      } catch (e) {
        console.log(`getSearchPageTurnTap: ${e}`);
      }
      if (
        lastTap &&
        lastTap.direction === direction &&
        now - lastTap.time < SEARCH_PAGE_TURN_DOUBLE_TAP_MSEC
      ) {
        startAutoPageTurn(direction);
      } else {
        try {
          sessionStorage.setItem(
            SEARCH_PAGE_TURN_TAP_KEY,
            JSON.stringify({ direction: direction, time: now }),
          );
        } catch (e) {
          console.log(`setSearchPageTurnTap: ${e}`);
        }
      }
      ytsched.moveActiveDate(direction, ytsched.url_prefix);
      return;
    }

    ytsched.moveActiveDate(direction, ytsched.url_prefix);

    const now = Date.now();
    if (
      lastPageTurnDirection === direction &&
      now - lastPageTurnTapMsec < PAGE_TURN_DOUBLE_TAP_MSEC
    ) {
      startAutoPageTurn(direction);
      lastPageTurnDirection = null;
      lastPageTurnTapMsec = 0;
      return;
    }
    lastPageTurnDirection = direction;
    lastPageTurnTapMsec = now;
  };

  /** 途中で割り込まれたとき (念のため。swipe.js の touchCancelHdr と同じ考え方) */
  const pageTurnPointerCancelHdr = () => {
    pageTurnStart = null;
  };

  window.addEventListener("load", onloadHdr);
  // キーボードでの操作は一覧だけ (TODO-050)
  window.addEventListener("keydown", ytsched.keyHdr);
  // 画面内で完結した移動から戻ってきたとき (TODO-050)
  window.addEventListener("popstate", ytsched.popstateHdr);
  // 左右のスワイプで週を送るのも一覧だけ (TODO-054)。
  // touchmove だけ passive: false (TODO-057)。横の動きと判定した
  // あと preventDefault() で縦スクロールを止めないと、指に追従
  // できない。他の 3 つは縦スクロールを邪魔しないので passive のまま
  window.addEventListener("touchstart", ytsched.touchStartHdr, {
    passive: true,
  });
  window.addEventListener("touchmove", ytsched.touchMoveHdr, {
    passive: false,
  });
  window.addEventListener("touchend", ytsched.touchEndHdr, { passive: true });
  window.addEventListener("touchcancel", ytsched.touchCancelHdr, {
    passive: true,
  });
  // PC のマウスの左右ドラッグでも週を送る (TODO-064)。
  // mousedown だけ capture で拾って伝播を止める。日付セルなどの
  // onmousedown は押した瞬間に遷移してしまい、そのままでは
  // セルの上からドラッグを始められない。動かずに離したときは、
  // mouseUpHdr が止めておいた onmousedown を自前で呼ぶ
  window.addEventListener("mousedown", ytsched.mouseDownHdr, true);
  window.addEventListener("mousemove", ytsched.mouseMoveHdr);
  window.addEventListener("mouseup", ytsched.mouseUpHdr);
  // ゲージの帯のドラッグ・タップ (TODO-178)。window への委譲で capture で拾う
  // (既存のボタン操作と同じパターン)。move と up / cancel は bubble で拾う
  window.addEventListener("pointerdown", ytsched.gaugeBarPointerDownHdr, true);
  window.addEventListener("pointermove", ytsched.gaugeBarPointerMoveHdr);
  window.addEventListener("pointerup", ytsched.gaugeBarPointerUpHdr);
  window.addEventListener("pointercancel", ytsched.gaugeBarPointerCancelHdr);
  // フッターの ◀▶ のダブルタップで自動ページ送り (TODO-084)。
  // pointerdown は capture で拾う (画面の他の場所を押したら止める分岐が、
  // ボタン側の分岐より先に効いてよい)
  window.addEventListener("pointerdown", pageTurnPointerDownHdr, true);
  // 検索画面のホームボタンのダブルタップ (TODO-165)。ボタン以外を
  // 押したら記録を捨てる。こちらも capture で拾う
  window.addEventListener("pointerdown", homeTapPointerDownHdr, true);
  window.addEventListener("pointerup", pageTurnPointerUpHdr);
  window.addEventListener("pointercancel", pageTurnPointerCancelHdr);
  // 止まる条件: ボタンをもう一度タップ (pageTurnPointerUpHdr) / 画面の
  // 他の場所をタップ (pageTurnPointerDownHdr) / キーを押した / 画面が
  // 隠れた
  window.addEventListener("keydown", stopAutoPageTurn);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && !pageIsUnloading) {
      stopAutoPageTurn();
    }
  });
  window.addEventListener("beforeunload", () => {
    pageIsUnloading = true;
    if (autoTurnTimerId !== null) {
      clearInterval(autoTurnTimerId);
      autoTurnTimerId = null;
    }
  });
})();
