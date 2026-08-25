/**
 *   (c) 2021 Yoichi Tanibayashi
 */

let elLoadingSpinner;
let elMain;
let elGageR0;
let scrollHdrTimer = 0;

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

/**
 * @param {number} days
 *
 * @return {number} yOffset
 */
const days2yOffset = (days) => {
    const dd = 0.6;
    const a = 70;
    const b = 0;

    // console.log(`days=${days}`);
    if (days == 0) {
        return 0;
    }
    
    const yOffset = Math.round(Math.log10(Math.abs(days) + dd) * a + b);
    if (days < 0) {
        return -yOffset;
    }
    return yOffset;
};

/**
 * @param {String} date_str   'YYYY-mm-dd'
 */
const dispGage = (date_str) => {
    if ( ! date_str ) {
        elGageR0.style.display = "none";
        return;
    }

    // console.log(`date_str=${date_str}`);
    const top_rel_days = getDaysFromToday(date_str);

    //
    // gage
    //
    const centerY = document.documentElement.clientHeight / 2 + 40;
    const yOffset = days2yOffset(top_rel_days);
    // console.log(`centerY=${centerY}, yOffset=${yOffset}`);
    const gageBottom = centerY - yOffset;

    // console.log(`dispGage: gageBottom=${gageBottom}`);
    elGageR0.style.bottom = `${gageBottom}px`;
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
 * 画面の一番上に表示されている日付を取得
 *
 * @return {String} date_str: "YYYY-MM-DD"
 */
const getTopDateString = () => {
    const el_date_from = document.getElementById("date_from");
    const win_top = window.pageYOffset;

    let el_date = document.getElementById(`date-${el_date_from.value}`);
    while ( el_date.offsetTop < win_top ) {
        const d1 = new Date(el_date.id.replace('date-',''));
        const d1_str = getLocaltimeDateString(shiftDays(d1, 1));
        el_date = document.getElementById(`date-${d1_str}`);
    }
    // console.log(`getTopDateString: el_date.id=${el_date.id}`);
    return el_date.id.replace('date-', '');
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
 * 今日からの日数
 *
 * !! Important !!
 *
 * new Date()の日付の区切り文字は、
 * '/' だとJST, '-'だとUTCと見なされるが、
 *
 * ここでは、どちらもLocaltimeと見なす。
 *
 * (ex.)
 * new Date('2021/01/01') - new Date('2021-01-01T00:00:00.000Z')
 * 2021/01/01,00:00:00(JST) - 2021/01/01,00:00:00(UTC) = -9h
 *
 * @param {String} date_str  ex. "2021-01-01" or "2021/01/01"
 *
 * @return {number} days
 */
const getDaysFromToday = (date_str) => {
    const d_date = new Date(date_str.split('/').join('-'));
    const d_today = new Date(getLocaltimeDateString(new Date()));
    const days = calcDays(d_today, d_date);
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
    scrollFlag = false;
    if ( scrollToId(`date-${date}`, "top", "auto") ) {
        const el_cur_day = document.getElementById("cur_day");
        if ( el_cur_day ) {
            el_cur_day.value = date;
        }
        scrollFlag = true;
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

let scrollFlag = false;

/**
 *
 */
const scrollHdr = (event) => {
    if ( ! scrollFlag ) {
        console.log(`scrollHdr:event=${event}, scrollFlag=${scrollFlag}`);
        return;
    }

    const top_date_str = getTopDateString();
    const rel_days = getDaysFromToday(top_date_str);

    const el_search = document.getElementById("search_str");
    if (el_search.value != "") {
        return;
    }

    const win_h = document.documentElement.clientHeight;
    const body_h = document.body.clientHeight;
    const d_top = window.pageYOffset;
    const d_bottom = body_h - d_top - win_h;
    console.log(`scrollHdr:d_top=${d_top}, d_bottom=${d_bottom}`);
    
    if (d_top < 50) {
      scrollFlag = false;
      el = document.getElementById("date_from");
      date = el.value;
      console.log(`date=${date}`);
      doGet(`${url_prefix}`, {date: date, sde_align: "top"});
    }
    if (d_bottom < 80) {
      scrollFlag = false;
      el = document.getElementById("date_to");
      date = el.value;
      console.log(`date=${date}`);
      doGet(`${url_prefix}`, {date: date, sde_align: "bottom"});
    }
};

/**
 *
 */
const scrollHdr0 = (event) => {
    const top_date_str = getTopDateString();
    dispGage(top_date_str);
    
    if (scrollHdrTimer > 0) {
        clearTimeout(scrollHdrTimer);
    }
    scrollHdrTimer = setTimeout(scrollHdr, 100);
};

/**
 *
 */
const scrollToId = (id, sde_align = "top", behavior = "smooth") => {
    scrollFlag = false;
    console.log(`scrollToId:id=${id}`);
    

    const body_h = document.body.clientHeight;
    const win_h = document.documentElement.clientHeight;

    elMain.style.visibility = "visible";
    if (body_h <= win_h) {
        console.log(`body_h=${body_h} < win_h=${win_h}`);
        return true;
    }

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

    scrollFlag = true;
    return true;
};

/**
 *
 */
const scrollToDate = (path, date, sde_align="top", behavior="smooth", push_flag=true) => {
    scrollFlag = false;
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
        scrollFlag = true;
        return true;
    }

    console.log(`path=${path}`);
    doGet(path, {date: date, sde_align: sde_align});
    return false;
};

/**
 * [Important!]
 * スクロールによる自動読み込みより先に、自動読み込みをトリガー
 *
 * @param {number} direction
 * @param {String} path
 * @param {String} behavior
 */
const moveToMonday = (direction=1, path, behavior="smooth") => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${getLocaltimeString(cur_day)}`);

    let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }

    let days;
    let days2;
    if ( direction > 0 ) {
        days = 8 - wday;
        days2 = days + 21;
    } else {
        days = 1 - wday;
        if (days == 0) {
            days = -7; // Mon
        }
        days2 = days - 14;
    }
    console.log(`moveToMonday:days=${days}, days2=${days2}`);
    
    let d1 = new Date(el_cur_day.value);
    d1 = shiftDays(d1, days);
    d1_str = getLocaltimeDateString(d1);
    console.log(`moveToMonday:d1_str=${d1_str}`);

    let d2 = new Date(el_cur_day.value);
    d2 = shiftDays(d2, days2);
    d2_str = getLocaltimeDateString(d2);
    console.log(`moveToMonday:d2_str=${d2_str}`);

    el_d2 = document.getElementById(`date-${d2_str}`);
    if ( ! el_d2 ) {
        doGet(path, {date: d1_str, sde_align: "top"});
        return;
    }

    el_cur_day.value = d1_str;
    pushDateInUrl(d1_str);
    scrollFlag = false;
    scrollToId(`date-${d1_str}`);
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
