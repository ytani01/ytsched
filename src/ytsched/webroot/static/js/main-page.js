/**
 *   (c) 2026 ytani01
 */

// main.html だけで使う関数・リスナー登録 (TODO-083)。テンプレートの
// 値 (``search_str0`` / ``today_str``) は main.html の <script> で
// 定数にしてから、この後ろで読み込まれる
//
// 外へ出すもの:
//   homeButtonHdr() -- main.html の #home_button の onMouseDown
//   changeSearchN() -- main.html の #search_n_in の onchange (検索モード)
//   onloadHdr()・keyHdr (keyboard.js)・popstateHdr (nav.js)・swipe.js の各
//     ハンドラを、このファイル末尾で window のイベントに登録する。
//     ページ送り関連 (startAutoPageTurn / stopAutoPageTurn /
//     pageTurnPointerDownHdr / pageTurnPointerUpHdr / pageTurnPointerCancelHdr)
//     はこのファイル内だけで使う
// 外から使うもの:
//   search_str0 / today_str / auto_turn_msec (main.html の <script>)
//   url_prefix (base.html の <script>)
//   ytState (state.js)  -- elLoadingSpinner・elMain・elWeekWrap・
//                          activeWeekOffset・activeMonday・elGaugeR0
//   loadingSpinner() (spinner.js)             -- onloadHdr
//   doGet() / doPost() / scrollToDate() (nav.js)
//   getLocaltimeDateString() (nav.js)         -- homeButtonHdr
//   mondayOf() (gauge.js)                     -- homeButtonHdr
//   popstateHdr() (nav.js)                    -- popstate に登録
//   layoutWeeks() / moveToMonday() (week.js)
//   dispGauge() / dispGaugeMarks() (gauge.js) -- onloadHdr
//   keyHdr() (keyboard.js)                    -- keydown に登録
//   swipe.js の touch* / mouse* の 7 ハンドラ -- 各イベントに登録

(() => {
const ytsched = window.ytsched;
let clickCount = 0;

window.ytsched.homeButtonHdr = () => {
  // シングル・ダブルとも、今日ではなく今週の月曜日へ移動する
  // (TODO-105)。週間表示では週の頭が見えているほうが分かりやすい
  const monday_str = ytsched.getLocaltimeDateString(ytsched.mondayOf(ytsched.today_str));

  if (!clickCount) {
    // single click
    ++clickCount;
    setTimeout(function () {
      clickCount = 0;
    }, 350);
    console.log("single click");

    console.log(`search_str0=${ytsched.search_str0}`);
    if (ytsched.search_str0) {
      const el_search = document.getElementById("search_str");
      const search_str = el_search.value;
      console.log(`search_str=${search_str}`);
      // search_str は URL に載せない (TODO-050)
      ytsched.doPost(ytsched.url_prefix, {
        date: monday_str,
        search_str: search_str,
      });
    }
    ytsched.scrollToDate(ytsched.url_prefix, monday_str, "top");
  } else {
    // double click
    //event.preventDefault() ;
    clickCount = 0;
    console.log("double click");

    // データを読み直す (TODO-069)。前後数ヶ月ぶんを DOM に持つ
    // ようになったので、抱えたまま古くなる。ダブルタップが、
    // 手で取り直す道
    ytsched.doGet(ytsched.url_prefix, { date: monday_str, sde_align: "top" });
  }
};

const onloadHdr = (event) => {
  console.log(`onloadHdr(${event}`);
  ytsched.ytState.elLoadingSpinner = document.getElementById("loadingSpinner");
  ytsched.loadingSpinner(false);

  ytsched.ytState.elMain = document.getElementById("main"); // declared in state.js
  ytsched.ytState.elWeekWrap = document.getElementById("week_wrap"); // declared in state.js

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

  if (body_h < win_h) {
    console.log(`body_h=${body_h} < win_h=${win_h}`);
    // ゲージの都合で画面が出ないのはおかしいので、dispGauge() より
    // 先に visible にする (TODO-049 reviewer 指摘 1)
    ytsched.ytState.elMain.style.visibility = "visible";
    ytsched.dispGauge(ytsched.ytState.activeMonday);
    return;
  }

  const el_sde_align = document.getElementById("sde_align");
  const el_date =
    document.getElementById("header_date") ||
    document.getElementById("footer_date");
  // 読み直したあとの位置合わせは一度で移す。"auto" は CSS の
  // scroll-behavior に従うので、Bootstrap 5 の :root の指定で
  // アニメーションになってしまう (TODO-041)
  // 読み直した直後なので、履歴には積まない (TODO-050)
  ytsched.scrollToDate(
    location.pathname,
    el_date.value,
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

// ダブルタップと見なす間隔 (msec)。homeButtonHdr() のダブルクリック判定
// (350) と揃える
const PAGE_TURN_DOUBLE_TAP_MSEC = 350;

// ボタンの上から始めた横の払いを、週送りとして拾わないための、
// 動いたと見なす最小の距離 (px)
const PAGE_TURN_MOVE_PX = 30;

/** 走っていれば自動ページ送りを止める。走っていなければ何もしない。 */
const stopAutoPageTurn = () => {
  if (autoTurnTimerId === null) {
    return;
  }
  clearInterval(autoTurnTimerId);
  autoTurnTimerId = null;
};

/**
 * 自動ページ送りを始める。
 *
 * ``auto_turn_msec`` ごとに ``moveToMonday()`` を呼ぶだけ。読み込んだ
 * 範囲の外へ出ると ``moveToMonday()`` が ``doGet()`` してページごと
 * 読み直すので、そこで自動的に止まる (window ごと作り直されるため)。
 *
 * @param {number} direction
 */
const startAutoPageTurn = (direction) => {
  stopAutoPageTurn();
  autoTurnTimerId = setInterval(() => {
    ytsched.moveToMonday(direction, ytsched.url_prefix);
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
  ytsched.moveToMonday(direction, ytsched.url_prefix);

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
window.addEventListener("touchstart", ytsched.touchStartHdr, { passive: true });
window.addEventListener("touchmove", ytsched.touchMoveHdr, { passive: false });
window.addEventListener("touchend", ytsched.touchEndHdr, { passive: true });
window.addEventListener("touchcancel", ytsched.touchCancelHdr, { passive: true });
// PC のマウスの左右ドラッグでも週を送る (TODO-064)。
// mousedown だけ capture で拾って伝播を止める。日付セルなどの
// onmousedown は押した瞬間に遷移してしまい、そのままでは
// セルの上からドラッグを始められない。動かずに離したときは、
// mouseUpHdr が止めておいた onmousedown を自前で呼ぶ
window.addEventListener("mousedown", ytsched.mouseDownHdr, true);
window.addEventListener("mousemove", ytsched.mouseMoveHdr);
window.addEventListener("mouseup", ytsched.mouseUpHdr);
// フッターの ◀▶ のダブルタップで自動ページ送り (TODO-084)。
// pointerdown は capture で拾う (画面の他の場所を押したら止める分岐が、
// ボタン側の分岐より先に効いてよい)
window.addEventListener("pointerdown", pageTurnPointerDownHdr, true);
window.addEventListener("pointerup", pageTurnPointerUpHdr);
window.addEventListener("pointercancel", pageTurnPointerCancelHdr);
// 止まる条件: ボタンをもう一度タップ (pageTurnPointerUpHdr) / 画面の
// 他の場所をタップ (pageTurnPointerDownHdr) / キーを押した / 画面が
// 隠れた
window.addEventListener("keydown", stopAutoPageTurn);
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    stopAutoPageTurn();
  }
});
})();
