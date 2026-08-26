/**
 *   (c) 2021 Yoichi Tanibayashi
 */

let elLoadingSpinner;
let elMain;
let elGageR0;

/**
 *
 */
const loadingSpinner = (on) => {
    if (on) {
        elLoadingSpinner.style.display = "block";
    } else {
        elLoadingSpinner.style.display = "none";
    }
};

// 横ゲージ (TODO-058)。``main_handler.py`` の ``DAYS_YEAR`` と同じ値
const DAYS_YEAR = 365.25;
const DAYS_GAGE_MAX = DAYS_YEAR * 30;
// 中心の近くをどれだけ詰めるか (TODO-059)。``main_handler.py`` の
// ``DAYS_GAGE_K`` と同じ値
const DAYS_GAGE_K = 10.0;

/**
 * 今週の中心からの左右のずれを、ゲージの幅に対する割合 (%) で返す。
 * Python 側 (``main_handler.py`` の ``days2x_percent()``) と同じ式・
 * 同じ頭打ち (TODO-058)。
 *
 * @param {number} days
 *
 * @return {number} xPercent
 */
const days2xPercent = (days) => {
    // console.log(`days=${days}`);
    let xPercent = 50.0 * Math.log10(1 + Math.abs(days) / DAYS_GAGE_K)
          / Math.log10(1 + DAYS_GAGE_MAX / DAYS_GAGE_K);
    xPercent = Math.min(xPercent, 50.0);

    if (days < 0) {
        return -xPercent;
    }
    return xPercent;
};

/**
 * ``date_str`` を含む週の月曜 (Localtime) を返す (TODO-049)。
 *
 * @param {String} date_str   'YYYY-mm-dd' or 'YYYY/mm/dd'
 *
 * @return {Date} monday
 */
const mondayOf = (date_str) => {
    const d = new Date(date_str.split('/').join('-'));
    let wday = d.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }
    return shiftDays(d, 1 - wday);
};

/**
 * 針の位置 (``left``) を計算してセットする。``transition`` は
 * 掛けたまま (TODO-049)。
 *
 * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい。
 *   月曜へ丸めてから、今週の月曜との差を見る)
 */
const setGagePosition = (date_str) => {
    const monday = mondayOf(date_str);
    const this_monday = mondayOf(getLocaltimeDateString(new Date()));
    const top_rel_days = calcDays(this_monday, monday);

    elGageR0.style.left = `${50 + days2xPercent(top_rel_days)}%`;
};

// 直前に見ていた週の月曜 (TODO-049)。ページを読み直したあと、
// この位置からいまの週へ針を動かして見せるために使う
const GAGE_MONDAY_KEY = "ytsched_gage_monday";

/**
 * ``sessionStorage`` から直前の週の月曜を読む。
 *
 * Safari の「すべての Cookie をブロック」設定や、``allow-same-origin``
 * の無い ``<iframe>`` では ``sessionStorage`` へのアクセスが
 * ``SecurityError`` を投げる。読めなければ「前の週は不明」として
 * ``null`` を返すだけにする (TODO-049)。
 *
 * @return {String | null}
 */
const getGageMonday = () => {
    try {
        return sessionStorage.getItem(GAGE_MONDAY_KEY);
    } catch (e) {
        console.log(`getGageMonday: ${e}`);
        return null;
    }
};

/**
 * ``sessionStorage`` へ今の週の月曜を書く。書けなくても黙って諦める
 * (TODO-049。理由は ``getGageMonday()`` を参照)。
 *
 * @param {String} monday_str   'YYYY-mm-dd'
 */
const setGageMonday = (monday_str) => {
    try {
        sessionStorage.setItem(GAGE_MONDAY_KEY, monday_str);
    } catch (e) {
        console.log(`setGageMonday: ${e}`);
    }
};

/**
 * ``transition`` を効かせずに、いったんその位置へ針を置く。
 *
 * **レイアウトを確定させるのに ``offsetHeight`` は使えない** (TODO-060)。
 * 針は ``<svg>`` (``SVGSVGElement``) で、``offsetHeight`` は
 * ``HTMLElement`` のものなので、読んでも ``undefined`` が返るだけで
 * レイアウトは確定しない。位置が反映されないまま ``transition`` が
 * 戻り、CSS の初期値 (``left: 50%``、つまり中央) から補間が始まって
 * しまう。``getBoundingClientRect()`` は SVG でも効く。
 *
 * @param {String} date_str   'YYYY-mm-dd'
 */
const placeGageWithoutTransition = (date_str) => {
    elGageR0.classList.add("my-gage-r-no-transition");
    setGagePosition(date_str);
    elGageR0.getBoundingClientRect(); // 強制的にレイアウトを確定させる
    elGageR0.classList.remove("my-gage-r-no-transition");
};

/**
 * ゲージの針を動かす。
 *
 * ``sessionStorage`` に前回表示していた週の月曜を持っていれば、まず
 * ``transition`` を効かせずにその位置へ針を置き、次のフレームで
 * 今の週へ動かす (TODO-049)。ページを読み直すたびに呼ばれるので、
 * ``transition`` だけでは針の初期値が "auto" のままで補間が起きず、
 * 動いて見えない。``sessionStorage`` が使えない環境でも、針の位置を
 * 合わせること自体は続ける (``getGageMonday()``/``setGageMonday()``
 * が例外を握りつぶす)。
 *
 * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい)
 */
const dispGage = (date_str) => {
    // 検索モードでは週バーごと帯が出ないので、gage_r が無い (TODO-058)
    if ( ! elGageR0 ) {
        return;
    }

    if ( ! date_str ) {
        elGageR0.style.display = "none";
        return;
    }

    const monday_str = getLocaltimeDateString(mondayOf(date_str));
    const prev_monday_str = getGageMonday();
    setGageMonday(monday_str);

    if (prev_monday_str && prev_monday_str !== monday_str) {
        placeGageWithoutTransition(prev_monday_str);
        requestAnimationFrame(() => {
            setGagePosition(monday_str);
        });
        return;
    }

    // 動かす先が無いので、そのまま置く。``setGagePosition()`` を直に
    // 呼ぶと、針の ``left`` が CSS の初期値 (``left: 50%``) のままな
    // ので、中央から目的地まで transition が掛かる (TODO-060)
    placeGageWithoutTransition(monday_str);
};

/**
 * 日付をずらす
 *
 * @param {Date} d
 * @param {number} days
 *
 * @return {Date} d
 */
const shiftDays = (d, days) => {
    d.setDate(d.getDate() + days);
    return d;
};

/**
 * get Localtime string: "YYYY-mm-ddTHH:MM:SS.SSSZ"
 *
 * !! Important !!
 *
 * new Date()の日付の区切り文字が
 *   '/' だとJST(+09:00),
 *   '-' だとUTC
 * とみなされる！
 *
 * (ex.)
 * > (new Date("2021/01/01")).toISOString();
 * < "2020-12-31T15:00:00.000Z"
 * > (new Date("2021-01-01")).toISOString();
 * < "2021-01-01T00:00:00.000Z"
 *
 * ここでは、区切り文字を '-'に統一して、全てLocaltimeとみなす。
 *
 * `toLocaleDateString`が機能しない環境があるので、
 * あえて、面倒な変換を行う(!?)
 *
 * タイムゾーンの時差だけずらして、toISOString()を呼ぶ。
 * 末尾の 'Z'は削除する。
 *
 * @param {Date} d
 *
 * @return {String} localtime_str "2021-01-01T12:34:56.789"
 */
const getLocaltimeString = (d) => {
    const utc_msec = d.getTime();
    const offset_msec = d.getTimezoneOffset() / 60 * 3600 * 1000;
    const localtime_msec = utc_msec - offset_msec;
    const local_d = new Date(localtime_msec);
    const localtime_str = local_d.toISOString().slice(0,-1);
    return localtime_str;
};

/**
 * get Localtime date string: "YYYY-mm-dd"
 *
 * @param {Date} d
 *
 * @return {String} jst_date_str  ex. "2021-01-01"
 */
const getLocaltimeDateString = (d) => {
    return getLocaltimeString(d).replace(/T.*$/, '');
};

/**
 * 日数計算
 *
 * @param {Date} d_from
 * @param {Date} d_to
 *
 * @return {number} days
 */
const calcDays = (d_from, d_to) => {
    const days = (d_to - d_from) / (24 * 60 * 60* 1000);
    return days;
};

/**
 *
 */
const doSubmit = (id) => {
    loadingSpinner(true);
    const el = document.getElementById(id);
    el.submit();
};

/**
 * pathとクエリから URLを組み立てる (TODO-050)。
 *
 * 値が undefined・nullのものは入れない。
 *
 * @param {String} path
 * @param {Object} data   {param1_name: value1, param2_name: value2, ..}
 * @return {String}
 */
const mkUrl = (path, data) => {
    if (data === undefined) {
        return path;
    }

    const params = new URLSearchParams();
    for (let param in data) {
        const value = data[param];
        if (value === undefined || value === null) {
            continue;
        }
        params.append(param, value);
    }

    const query = params.toString();
    if (! query) {
        return path;
    }
    return `${path}?${query}`;
};

/**
 * クエリを組み立てて GETで移動する (TODO-050)。
 *
 * 以前は formを生成して POSTしていたが、URLが変わらないので、
 * 戻る/進む・リロード・ブックマークのどれも効かなかった。
 *
 * @param {String} path
 * @param {Object} data   {param1_name: value1, param2_name: value2, ..}
 */
const doGet = (path, data) => {
    loadingSpinner(true);
    location.href = mkUrl(path, data);
};

/**
 * formタグを生成して POSTする。
 *
 * **``conf.json``へ保存される値 (検索語・目標件数など) を送るときだけ
 * 使う** (TODO-050)。GETのクエリに載せると、ブックマークにも履歴にも
 * 検索語が残ってしまう。URLに持たせるのは日付だけと決めた。
 *
 * POSTを受けた ``MainHandler.post()``が、値を保存してから日付だけの
 * GETへ飛ばす (POST-Redirect-GET)ので、リロードしても再送信にならない。
 *
 * @param {String} path
 * @param {Object} data   {param1_name: value1, param2_name: value2, ..}
 */
const doPost = (path, data) => {
    loadingSpinner(true);

    const form = document.createElement("form");
    form.setAttribute("action", path);
    form.setAttribute("method", "POST");
    form.style.display = "none";
    document.body.appendChild(form);

    if (data !== undefined) {
        for (let param in data) {
            const input = document.createElement("input");
            input.setAttribute("type", "hidden");
            input.setAttribute("name", param);
            input.setAttribute("value", data[param]);
            form.appendChild(input);
        }
    }
    form.submit();
};

/**
 * 画面内のスクロールで移動したときに、URLの ``date``を書き換える
 * (TODO-050)。
 *
 * **履歴に積む (``pushState``)。** 読み直しを伴う移動と揃えて、
 * どちらで移動しても戻るで 1つずつ辿れるようにする。
 *
 * 最初は ``replaceState``にしていたが、それだと画面内で完結する移動が
 * 履歴に残らず、**戻るときに途中の日付を飛び越えてしまう**
 * (← を 8回押してから戻ると 3回分が 1つにまとまった)。
 *
 * @param {String} date   'YYYY-mm-dd'
 */
const pushDateInUrl = (date) => {
    const url = new URL(location.href);
    url.searchParams.set("date", date);
    history.pushState({date: date}, "", url.toString());
};

/**
 * URLの ``date``を書き換えるが、**履歴には積まない** (TODO-050)。
 *
 * ページを読み直した直後に使う。読み直しそのもので履歴は 1つ増えて
 * いるので、そこで ``pushState``すると**同じ日付が 2つ並び、戻るを
 * 1回押しても画面が変わらない**。
 *
 * @param {String} date   'YYYY-mm-dd'
 */
const replaceDateInUrl = (date) => {
    const url = new URL(location.href);
    url.searchParams.set("date", date);
    history.replaceState({date: date}, "", url.toString());
};

/**
 * 戻る/進むで呼ばれる (TODO-050)。
 *
 * ``pushDateInUrl()``で積んだ履歴へ戻ってきたときは、ページの
 * 読み直しが起きないので、ここで URLの ``date``まで動かす。
 * 読み込んである範囲の外なら、その URLで読み直す。
 */
const popstateHdr = (event) => {
    const date = new URL(location.href).searchParams.get("date");
    console.log(`popstateHdr:date=${date}`);

    if ( ! date ) {
        location.reload();
        return;
    }

    // 画面内にあればスクロールで済ませる。無ければ読み直す
    if ( scrollToId(`date-${date}`, "top", "auto") ) {
        const el_cur_day = document.getElementById("cur_day");
        if ( el_cur_day ) {
            el_cur_day.value = date;
        }
        return;
    }

    location.reload();
};

/**
 * @param {String} path
 * @param {String} date   'YYYY-mm-dd'
 * @param {number} days
 * @param {String} sde_align
 */
const doGetDate = (path, date, days = 0, sde_align = undefined) => {
    console.log(`doGetDate: sde_align=${sde_align}`);

    // dateをJSTとみなすために、区切りを '/'に変換
    let d1 = new Date(date.split('-').join('/'));
    d1 = shiftDays(d1, days);
    d1_str = getLocaltimeDateString(d1);
    console.log(`date=${date}, d1_str=${d1_str}`);

    data_obj = {date: d1_str};
    if ( sde_align ) {
        data_obj.sde_align = sde_align;
    }
    doGet(path, data_obj);
};

/**
 *
 */
const scrollToId = (id, sde_align = "top", behavior = "smooth") => {
    console.log(`scrollToId:id=${id}`);

    elMain.style.visibility = "visible";

    // 目的の要素が DOM にあるかどうかを、「1 画面に収まっているか」
    // より先に見る (TODO-049)。週表示になり、予定の少ない週では
    // 1 画面に収まる (body_h <= win_h) ことが増えた。それだけで
    // 「スクロールで用が足りた」= true を返すと、DOM に無い日
    // (表示中の週の外) を指されたときも true になり、呼び出し元の
    // scrollToDate() が doGet() での読み直しを飛ばしてしまう
    // (URL だけ書き換わって画面が変わらない不具合になった)。
    const el = document.getElementById(id);
    const el_search = document.getElementById('search_str');
    const search_str = el_search.value;

    if (el == null) {
        console.log(`scrollToId:scrollToID:el=${el}`);

        if (search_str) {
            return true;
        }
        return false;
    }

    const body_h = document.body.clientHeight;
    const win_h = document.documentElement.clientHeight;

    if (body_h <= win_h) {
        console.log(`body_h=${body_h} < win_h=${win_h}`);
        return true;
    }

    const top_of_el = el.offsetTop;
    const bottom_of_el = el.offsetTop + el.offsetHeight;
    const el_menu_bar = document.getElementById("menu_bar");
    const menu_bar_h = el_menu_bar.offsetHeight;

    console.log(`scrollToId:sde_align=${sde_align}`);

    const scroll_offset = 30;
    if (sde_align == "top") {
        scrollTo({left: 0,
                  top: top_of_el - scroll_offset,
                  behavior: behavior});
    }
    if (sde_align == "bottom") {
        scrollTo({left: 0,
                  top: bottom_of_el - win_h + menu_bar_h + scroll_offset,
                  behavior: behavior});
    }

    return true;
};

/**
 *
 */
const scrollToDate = (path, date, sde_align="top", behavior="smooth", push_flag=true) => {
    console.log(`scrollToDate:date=${date}, sde_align=${sde_align}`);

    const el_cur_day = document.getElementById("cur_day");

    if (scrollToId(`date-${date}`, sde_align, behavior)) {
        el_cur_day.value = date;
        // 読み直した直後 (``push_flag``が偽) は履歴に積まない。
        // 読み直しそのもので 1つ増えているため (TODO-050)
        if ( push_flag ) {
            pushDateInUrl(date);
        } else {
            replaceDateInUrl(date);
        }
        return true;
    }

    console.log(`path=${path}`);
    doGet(path, {date: date, sde_align: sde_align});
    return false;
};

/**
 * 週を送る (次/前の月曜へ移る)。
 *
 * 週表示では前後の週は DOM に無いので、常に読み直す (TODO-049)。
 *
 * @param {number} direction
 * @param {String} path
 */
const moveToMonday = (direction=1, path) => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${getLocaltimeString(cur_day)}`);

    let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }

    let days;
    if ( direction > 0 ) {
        days = 8 - wday;
    } else {
        days = 1 - wday;
        if (days == 0) {
            days = -7; // Mon
        }
    }
    console.log(`moveToMonday:days=${days}`);

    let d1 = new Date(el_cur_day.value);
    d1 = shiftDays(d1, days);
    d1_str = getLocaltimeDateString(d1);
    console.log(`moveToMonday:d1_str=${d1_str}`);

    doGet(path, {date: d1_str, sde_align: "top"});
};

/**
 * 画面下に固定したバーを、ソフトキーボードの上に出す (TODO-039)
 *
 * `.my-follow-keyboard` が付いた要素を、キーボードの高さだけ持ち上げる。
 *
 * Android Chrome は viewport の `interactive-widget=resizes-content` で
 * 本文が縮むので、ここで計算するずれは 0 になる。iOS Safari は縮まない
 * ので、この関数が効く。
 *
 * ピンチで拡大している間 (`scale > 1`) は、ずらす量を 0 に戻す。
 * 拡大中も `visualViewport` は小さくなるが、それはキーボードのせいでは
 * ないので、その分を持ち上げると位置が狂う。
 */
const followKeyboard = () => {
    const vv = window.visualViewport;
    if ( ! vv ) {
        return;
    }
    let offset = 0;
    if ( vv.scale <= 1.01 ) {
        const gap = window.innerHeight - vv.height - vv.offsetTop;
        offset = Math.max(0, Math.round(gap));
    }
    const els = document.getElementsByClassName("my-follow-keyboard");
    for ( const el of els ) {
        el.style.transform = `translateY(${-offset}px)`;
    }
};

if ( window.visualViewport ) {
    window.visualViewport.addEventListener("resize", followKeyboard);
    window.visualViewport.addEventListener("scroll", followKeyboard);
    window.addEventListener("load", followKeyboard);
}


/**
 * 入力欄にフォーカスがあるかどうか (TODO-050)。
 *
 * キーの割り当てを拾う前に見る。検索欄で ``/``が打てなくなったり、
 * 日付の入力欄で ←→ が週送りになったりしないようにする。
 */
const isTyping = () => {
    const el = document.activeElement;
    if ( ! el ) {
        return false;
    }
    const tag = el.tagName.toLowerCase();
    if ( tag === "input" || tag === "textarea" || tag === "select" ) {
        return true;
    }
    return el.isContentEditable === true;
};

/**
 * キーボードで操作する (TODO-050)。
 *
 * | キー    | 動き                          |
 * |---------|-------------------------------|
 * | ← / →   | 前の週へ / 次の週へ           |
 * | ↑ / ↓   | 今までどおりスクロール        |
 * | Home    | 今日へ                        |
 * | /       | 検索欄へ移る                  |
 * | Esc     | 検索欄から抜ける              |
 *
 * 一覧 (``main.html``) でだけ登録する。編集画面で ←→ が効くと、
 * 入力の途中で画面が変わってしまう。
 */
const keyHdr = (event) => {
    if ( isTyping() ) {
        if ( event.key === "Escape" ) {
            document.activeElement.blur();
        }
        return;
    }

    if ( event.ctrlKey || event.altKey || event.metaKey ) {
        return;
    }

    switch ( event.key ) {
    case "ArrowLeft":
        event.preventDefault();
        moveToMonday(-1, url_prefix);
        break;

    case "ArrowRight":
        event.preventDefault();
        moveToMonday(1, url_prefix);
        break;

    case "Home": {
        event.preventDefault();
        const today_str = getLocaltimeDateString(new Date());
        scrollToDate(url_prefix, today_str, "top");
        break;
    }

    case "/": {
        event.preventDefault();
        const el_search = document.getElementById("search_str");
        if ( el_search ) {
            el_search.focus();
        }
        break;
    }
    }
};

/**
 * 左右のスワイプで週を送るための、始点を覚えておく場所 (TODO-054)。
 *
 * 指が触れている間だけ ``{x, y, t}`` が入る。触れていないとき、
 * 途中で 2 本目の指が触れたとき、``touchcancel`` が来たときは ``null``。
 */
let swipeStart = null;

// 横に動いたと見なす最小の距離 (px)
const SWIPE_MIN_X = 60;

// 横の動きが縦の何倍あれば横スワイプと見なすか
const SWIPE_X_PER_Y = 1.5;

// これより長く触れていたら、スワイプと見なさない (msec)
const SWIPE_MAX_MSEC = 800;

// 画面の左右の端から、これだけの幅では受け付けない (px)
const SWIPE_EDGE_PX = 30;

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
 */
const touchStartHdr = (event) => {
    swipeStart = null;

    if ( event.touches.length !== 1 ) {
        return;
    }

    const el = event.target;
    if ( el && el.closest && el.closest("input, textarea, select") ) {
        return;
    }

    const touch = event.touches[0];
    const win_w = document.documentElement.clientWidth;
    if ( touch.clientX < SWIPE_EDGE_PX
         || touch.clientX > win_w - SWIPE_EDGE_PX ) {
        return;
    }

    swipeStart = {x: touch.clientX, y: touch.clientY, t: Date.now()};
};

/**
 * 指が増えていないかを、動いている間も見る (TODO-054)。
 *
 * ``touchstart`` は指が増えるたびに呼ばれ、``touchStartHdr`` が先頭で
 * ``swipeStart`` を捨てるので、2 本目が触れた時点で見送りは決まって
 * いる。ここはその**念のための二重の確認**で、``touchstart`` を
 * 取りこぼした場合にだけ効く。
 */
const touchMoveHdr = (event) => {
    if ( event.touches.length !== 1 ) {
        swipeStart = null;
    }
};

/**
 * 指が離れたとき (TODO-054)。
 *
 * **縦の動きが優勢なら何もしない。** 1 週間分が画面に収まらない週では
 * 上下にスクロールするので、その動きを週送りと取り違えないようにする。
 *
 * 左へ払ったら次の週、右へ払ったら前の週。画面の中身が指について
 * 動くわけではないが、週が変わるとゲージの針が ``transition`` で
 * 動くので、どちらへ移ったかはそれで分かる (TODO-049)。
 */
const touchEndHdr = (event) => {
    const start = swipeStart;
    swipeStart = null;

    if ( ! start ) {
        return;
    }
    if ( event.changedTouches.length !== 1 ) {
        return;
    }
    if ( Date.now() - start.t > SWIPE_MAX_MSEC ) {
        return;
    }

    const touch = event.changedTouches[0];
    const dx = touch.clientX - start.x;
    const dy = touch.clientY - start.y;

    if ( Math.abs(dx) < SWIPE_MIN_X ) {
        return;
    }
    if ( Math.abs(dx) < Math.abs(dy) * SWIPE_X_PER_Y ) {
        return;
    }

    console.log(`touchEndHdr:dx=${dx}, dy=${dy}`);
    moveToMonday(dx < 0 ? 1 : -1, url_prefix);
};

/**
 * 途中で割り込まれたとき (TODO-054)。
 */
const touchCancelHdr = () => {
    swipeStart = null;
};
