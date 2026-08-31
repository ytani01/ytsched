/**
 *   (c) 2026 ytani01
 */

// スワイプとマウス (TODO-083)

// swipeStart / swipeDragging / swipeMiniCal / lastTouchMsec / mouseDownEl は、
// swipe.js だけで閉じる状態 (TODO-083)
//
// 外へ出すもの:
//   touchStartHdr / touchMoveHdr / touchEndHdr / touchCancelHdr /
//   mouseDownHdr / mouseMoveHdr / mouseUpHdr
//     -- main-page.js が window の touch* / mouse* イベントに登録する
//   cancelSwipeDrag / swipeDragTo / swipeFinish と、定数 (SWIPE_MIN_X /
//   SWIPE_X_PER_Y / SWIPE_EDGE_PX / SWIPE_FAST_PX_PER_MSEC /
//   MOUSE_AFTER_TOUCH_MSEC)・上記の状態はこのファイル内だけで使う
// 外から使うもの:
//   window.ytsched.ytState (state.js) -- elWeekWrap
//   slideWeekWrap() (week.js)  -- cancelSwipeDrag
//   hasAdjacentWeek() (week.js) -- swipeDragTo
//   moveActiveDate() (week.js) -- swipeFinish
//   moveActiveMonth() (week.js) -- swipeFinish (始点がミニカレンダーの
//     上だったとき、TODO-136)
//   window.ytsched.search_date_to (main.html の <script>) -- swipeDragTo
//     (検索モードでは追従表示をしないまま swipeDragging を立てる、TODO-117)
//   window.ytsched.url_prefix (base.html の <script>) -- swipeFinish が
//     moveActiveDate / moveActiveMonth へ渡す
//   window.ytsched.view_month (main-page.js の onloadHdr()) --
//     touchStartHdr・mouseDownHdr (月間表示では swipeMiniCal を立てない。
//     TODO-137)

(() => {
  const ytsched = window.ytsched;

  /**
   * 左右のスワイプ・ドラッグで週を送るための、始点を覚えておく場所
   * (TODO-054, TODO-064)。
   *
   * 指が触れている間 (マウスならボタンを押している間) だけ
   * ``{x, y, t}`` が入る。触れていないとき、途中で 2 本目の指が触れた
   * とき、``touchcancel`` が来たときは ``null``。
   */
  let swipeStart = null;

  // 横の動きと判定して、隣の週を指・マウスに追従させているか (TODO-057)
  let swipeDragging = false;

  // 始点がミニカレンダー (``.my-mini-cal``) の上だったか (TODO-136)。
  // そうなら、離したときに週ではなく月を送る
  let swipeMiniCal = false;

  // 横に動いたと見なす最小の距離 (px)
  const SWIPE_MIN_X = 50;

  // 横の動きが縦の何倍あれば横スワイプと見なすか
  const SWIPE_X_PER_Y = 1.5;

  // 画面の左右の端から、これだけの幅では受け付けない (px)
  const SWIPE_EDGE_PX = 30;

  // これより速く払ったら、画面幅の 1/3 に届いていなくても送る (px/msec)。
  // ``SWIPE_MAX_MSEC`` (指に追従させる前の、触れていた時間の上限) の
  // 代わり (TODO-057)
  const SWIPE_FAST_PX_PER_MSEC = 0.5;

  // タッチのあと、これだけの間に来た ``mousedown`` はタッチ由来と
  // 見なして素通しさせる (msec) (TODO-064)
  const MOUSE_AFTER_TOUCH_MSEC = 700;

  // 最後にタッチのイベントを見た時刻 (TODO-064)。ブラウザはタッチの
  // あとに ``mousedown`` を作って投げてくるので、それを見分けるため
  let lastTouchMsec = 0;

  // マウスで押した時点の、``onmousedown`` を持つ要素 (TODO-064)。
  // ドラッグにならずに離したときに、この要素の ``onmousedown`` を呼ぶ
  let mouseDownEl = null;

  /**
   * 指・マウスが離れたときに、追従していた分を 0 へ戻す (TODO-057)。
   *
   * 追従していなければ (``swipeDragging`` が false) 何もしない。
   * ``ytState.elWeekWrap`` が無いとき (このページに無い) も何もしない。
   */
  const cancelSwipeDrag = () => {
    if (!swipeDragging) {
      return;
    }
    swipeDragging = false;
    ytsched.slideWeekWrap(0, () => {
      if (ytsched.ytState.elWeekWrap) {
        ytsched.ytState.elWeekWrap.style.transform = "";
        ytsched.ytState.elWeekWrap.classList.remove("my-week-wrap-dragging");
      }
    });
  };
  /**
   * 動いている間、隣の週を指・マウスに追従させる (TODO-057)。
   *
   * 横の動きと判定するまでは何もしない (縦スクロールを邪魔しないため)。
   * 判定したあとは ``ytState.elWeekWrap`` に ``translateX()`` を掛ける。
   *
   * **検索モードでは追従させない (TODO-117)。** 週パネルが 1 枚しか無く
   * ``hasAdjacentWeek()`` が常に false になるので、そこだけ見送って
   * ``swipeDragging`` を立てる。追従表示 (``translateX`` / クラス付与) は
   * しないが、``swipeDragging`` が立つことで ``mouseUpHdr()`` が
   * クリックではなくドラッグと見なし、離したときに ``swipeFinish()`` へ
   * 届くようになる (タッチは ``touchend`` が ``swipeDragging`` を見ずに
   * 常に ``swipeFinish()`` を呼ぶので、この分岐が無くても届いていた)。
   *
   * **ミニカレンダーの上で始まったときも追従させない (TODO-136)。**
   * 週ではなく月を送るので、週パネルを ``translateX`` で追従させる
   * 意味が無い。検索モードと同じ理由で ``hasAdjacentWeek()`` も見ない
   * (読み込み範囲の端からでも、月へは送れるようにする)。
   *
   * **追従しているかどうかを返す。** タッチではこれが true のときだけ
   * ``preventDefault()`` して縦スクロールを止める。
   *
   * @param {number} dx
   * @param {number} dy
   * @return {boolean}
   */
  const swipeDragTo = (dx, dy) => {
    if (!swipeDragging) {
      if (
        Math.abs(dx) < SWIPE_MIN_X ||
        Math.abs(dx) < Math.abs(dy) * SWIPE_X_PER_Y
      ) {
        return false;
      }
      if (
        !ytsched.search_date_to &&
        !swipeMiniCal &&
        !ytsched.hasAdjacentWeek()
      ) {
        return false;
      }
      swipeDragging = true;
      if (
        !ytsched.search_date_to &&
        !swipeMiniCal &&
        ytsched.ytState.elWeekWrap
      ) {
        ytsched.ytState.elWeekWrap.classList.add("my-week-wrap-dragging");
      }
    }

    if (
      !ytsched.search_date_to &&
      !swipeMiniCal &&
      ytsched.ytState.elWeekWrap
    ) {
      ytsched.ytState.elWeekWrap.style.transform = `translateX(${dx}px)`;
    }
    return true;
  };

  /**
   * 離したときに、週 (または月・ミニカレンダーの上なら TODO-136) を
   * 送るかどうかを決める (TODO-057)。
   *
   * **縦の動きが優勢なら送らない。** 1 週間分が画面に収まらない週では
   * 上下にスクロールするので、その動きを週送りと取り違えないようにする。
   *
   * **画面幅の 1/3 以上動いたか、速く払ったとき**に送る。それ以外は
   * 追従していた分を 0 へ戻す。左へ払ったら次へ、右へ払ったら前へ。
   *
   * @param {number} dx
   * @param {number} dy
   * @param {number} elapsed_msec
   * @return {boolean}   送ったら true
   */
  const swipeFinish = (dx, dy, elapsed_msec) => {
    if (
      Math.abs(dx) < SWIPE_MIN_X ||
      Math.abs(dx) < Math.abs(dy) * SWIPE_X_PER_Y
    ) {
      cancelSwipeDrag();
      return false;
    }

    const win_w = document.documentElement.clientWidth;
    const velocity = elapsed_msec > 0 ? Math.abs(dx) / elapsed_msec : Infinity;

    if (Math.abs(dx) < win_w / 3 && velocity < SWIPE_FAST_PX_PER_MSEC) {
      cancelSwipeDrag();
      return false;
    }

    console.log(`swipeFinish:dx=${dx}, dy=${dy}, velocity=${velocity}`);
    swipeDragging = false;
    if (swipeMiniCal) {
      ytsched.moveActiveMonth(dx < 0 ? 1 : -1, ytsched.url_prefix);
    } else {
      ytsched.moveActiveDate(dx < 0 ? 1 : -1, ytsched.url_prefix);
    }
    return true;
  };

  /**
   * 指が触れたとき (TODO-054)。
   *
   * 次の 3 つは、始めた時点で見送る。
   *
   * - **2 本以上の指。** ピンチで拡大しているときに週が変わらないように
   * - **画面の左右の端から始まったもの。** iOS Safari の画面端スワイプ
   *   (戻る/進む) に取られるので、こちらでも拾うと二重に効く
   * - **入力欄の上で始まったもの。** 検索欄の中で文字を選ぼうとした
   *   ときに週が変わらないように
   * - **ページ送りボタン (``[data-page-turn]``) の上で始まったもの。**
   *   ボタン側は ``pointerdown``/``pointerup`` (main-page.js) で拾うので、
   *   ここで拾うと週送りが二重に効く (TODO-084)
   */
  window.ytsched.touchStartHdr = (event) => {
    lastTouchMsec = Date.now();
    swipeStart = null;
    cancelSwipeDrag(); // 前の指が離れ損なっていたときの後始末 (念のため)

    if (event.touches.length !== 1) {
      return;
    }

    const el = event.target;
    if (
      el &&
      el.closest &&
      el.closest("input, textarea, select, [data-page-turn]")
    ) {
      return;
    }

    const touch = event.touches[0];
    const win_w = document.documentElement.clientWidth;
    if (
      touch.clientX < SWIPE_EDGE_PX ||
      touch.clientX > win_w - SWIPE_EDGE_PX
    ) {
      return;
    }

    // 月間表示では立てない (TODO-137)。画面全体がミニカレンダーなので、
    // 立てると 1 ヶ月送り (moveActiveMonth()、TODO-136) になってしまう
    swipeMiniCal = !!(
      el &&
      el.closest &&
      el.closest(".my-mini-cal") &&
      !ytsched.view_month
    );
    swipeStart = { x: touch.clientX, y: touch.clientY, t: Date.now() };
  };

  /**
   * 指が動いている間 (TODO-057)。
   *
   * 追従は ``swipeDragTo()`` に任せ、追従を始めたときだけ
   * ``preventDefault()`` で縦スクロールを止める。
   *
   * 指が増えたときは、``touchStartHdr`` が先頭で ``swipeStart`` を
   * 捨てるので、2 本目が触れた時点で見送りは決まっている。ここはその
   * **念のための二重の確認**で、``touchstart`` を取りこぼした場合に
   * だけ効く (TODO-054)。
   */
  window.ytsched.touchMoveHdr = (event) => {
    lastTouchMsec = Date.now();

    if (event.touches.length !== 1) {
      swipeStart = null;
      cancelSwipeDrag();
      return;
    }

    if (!swipeStart) {
      return;
    }

    const touch = event.touches[0];
    const dx = touch.clientX - swipeStart.x;
    const dy = touch.clientY - swipeStart.y;

    if (swipeDragTo(dx, dy)) {
      event.preventDefault();
    }
  };

  /**
   * 指が離れたとき (TODO-054)。
   *
   * 送るかどうかの判定は ``swipeFinish()`` に任せる。
   */
  window.ytsched.touchEndHdr = (event) => {
    lastTouchMsec = Date.now();

    const start = swipeStart;
    swipeStart = null;

    if (!start) {
      return;
    }
    if (event.changedTouches.length !== 1) {
      cancelSwipeDrag();
      return;
    }

    const touch = event.changedTouches[0];
    swipeFinish(
      touch.clientX - start.x,
      touch.clientY - start.y,
      Date.now() - start.t,
    );
  };
  /**
   * 途中で割り込まれたとき (TODO-054)。
   */
  window.ytsched.touchCancelHdr = () => {
    lastTouchMsec = Date.now();
    swipeStart = null;
    cancelSwipeDrag();
  };

  /**
   * マウスのボタンを押したとき (TODO-064)。
   *
   * **``window`` に capture で登録する。** 一覧の日付セル・スケジュール
   * 項目・ボタンは ``onmousedown`` で**押した瞬間に**遷移するので、その
   * まま通すとセルの上でドラッグを始められない。capture で
   * ``stopPropagation()`` すると target まで伝播せず、要素の
   * ``onmousedown`` は発火しない。動かずに離したときに ``mouseUpHdr``
   * が自前で呼ぶ。
   *
   * 次の 3 つは、始めた時点で見送る (伝播を止めず、今までどおり動く)。
   *
   * - **タッチ由来の ``mousedown``。** ブラウザはタッチのあとにこれを
   *   作って投げてくる。タッチでの挙動は変えない
   * - **左ボタン以外。**
   * - **入力欄・ラベル・リンクの上。** 検索欄で文字を選べるように。
   *   ラベルはメニューの開閉 (``menu-sw``) に使っている
   * - **ページ送りボタン (``[data-page-turn]``) の上。** ``pointerdown``
   *   を邪魔しないよう、``stopPropagation()``/``preventDefault()`` の前で
   *   返す (TODO-084)
   */
  window.ytsched.mouseDownHdr = (event) => {
    if (
      !event.isTrusted ||
      Date.now() - lastTouchMsec < MOUSE_AFTER_TOUCH_MSEC
    ) {
      return;
    }

    // ウィンドウの外でボタンを離していたときの後始末 (念のため)。
    // ``mouseup`` はウィンドウの外では来ないので、``swipeDragging``
    // が true のまま残る
    // ことがある。残っていると、次に動かさずにクリックしただけで
    // 「追従していた」と見なされ、その回のクリックが効かない
    swipeStart = null;
    mouseDownEl = null;
    cancelSwipeDrag();

    if (event.button !== 0) {
      return;
    }

    const el = event.target;
    if (!el || !el.closest) {
      return;
    }
    if (el.closest("input, textarea, select, label, a, [data-page-turn]")) {
      return;
    }

    event.stopPropagation();
    event.preventDefault(); // ドラッグ中に文字が選択されないように

    mouseDownEl = el.closest("[data-action]");
    // 月間表示では立てない (TODO-137、touchStartHdr と同じ理由)
    swipeMiniCal = !!(el.closest(".my-mini-cal") && !ytsched.view_month);
    swipeStart = { x: event.clientX, y: event.clientY, t: Date.now() };
  };

  /**
   * マウスを動かしている間 (TODO-064)。
   *
   * ボタンが離れていたら (ウィンドウの外で離したときなど) 後始末する。
   * ``mouseup`` はウィンドウの外では来ないので、ここで気づくしかない。
   */
  window.ytsched.mouseMoveHdr = (event) => {
    if (!swipeStart) {
      return;
    }
    if (!(event.buttons & 1)) {
      swipeStart = null;
      mouseDownEl = null;
      cancelSwipeDrag();
      return;
    }

    swipeDragTo(event.clientX - swipeStart.x, event.clientY - swipeStart.y);
  };

  /**
   * マウスのボタンを離したとき (TODO-064)。
   *
   * **追従を始めていなければクリック**と見なし、``mouseDownHdr`` が
   * 止めておいた ``onmousedown`` を呼ぶ。追従していれば、週を送るか
   * どうかを ``swipeFinish()`` が決める。
   */
  window.ytsched.mouseUpHdr = (event) => {
    const start = swipeStart;
    const el = mouseDownEl;
    swipeStart = null;
    mouseDownEl = null;

    if (!start) {
      return;
    }
    if (event.button !== 0) {
      cancelSwipeDrag();
      return;
    }

    // 追従を始めていなければ、どれだけ動いていてもクリックと見なす
    // (TODO-064)。「少しだけ動いた」を除いてしまうと、押してから
    // 離すまでに手がぶれただけのときに、クリックとしても週送りとしても
    // 扱われず、黙って何も起きない範囲ができる。マウスには縦スクロール
    // のためのドラッグが無いので、追従していない動きはクリックでよい
    if (!swipeDragging) {
      if (el) {
        el.dispatchEvent(
          new MouseEvent("mousedown", {
            bubbles: true,
            clientX: event.clientX,
            clientY: event.clientY,
          }),
        );
      }
      return;
    }

    swipeFinish(
      event.clientX - start.x,
      event.clientY - start.y,
      Date.now() - start.t,
    );
  };
})();
