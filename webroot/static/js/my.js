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
 * 画面の一番下に表示されている日付を取得
 *
 * @return {String} date_str: "YYYY-MM-DD"
 */
const getBottomDateString = () => {
    const el_date_to = document.getElementById("date_to");
    const win_bottom = window.pageYOffset
          + document.documentElement.clientHeight;

    let el_date = document.getElementById(`date-${el_date_to.value}`);
    // console.log(`getBottomDate: el_date.id=${el_date.id}`);
    while ( el_date.offsetTop + el_date.offsetHeight > win_bottom ) {
        const d1 = new Date(el_date.id.replace('date-',''));
        const d1_str = getLocaltimeDateString(shiftDays(d1, -1));
        el_date = document.getElementById(`date-${d1_str}`);
    }
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
 * formタグを新たに生成し、
 * hiddenタイプの inputタグを生成して、
 * POSTする。
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
 * @param {String} path
 * @param {String} date   'YYYY-mm-dd'
 * @param {number} days
 * @param {String} sde_align
 */
const doPostDate = (path, date, days = 0, sde_align = undefined) => {
    console.log(`doPostDate: sde_align=${sde_align}`);

    // dateをJSTとみなすために、区切りを '/'に変換
    let d1 = new Date(date.split('-').join('/'));
    d1 = shiftDays(d1, days);
    d1_str = getLocaltimeDateString(d1);
    console.log(`date=${date}, d1_str=${d1_str}`);

    data_obj = {date: d1_str};
    if ( sde_align ) {
        data_obj.sde_align = sde_align;
    }
    doPost(path, data_obj);
};

/**
 *
 */
const doGet = (path, data) => {
    let url = `${location.protocol}//${location.host}${path}?`;

    for (let param in data) {
        url += `${param}=${data[param]}&`;
    }
    url = url.replace(/&$/, '');
    console.log(`url=${url}`);
    window.location.href=url;
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
        doPost('/ytsched/', {date: date, sde_align: "top"});
    }
    if (d_bottom < 80) {
        scrollFlag = false;
        el = document.getElementById("date_to");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, sde_align: "bottom"});
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
        scrollFlag = true;
        return true;
    }

    console.log(`path=${path}`);
    doPost(path, {date: date, sde_align: sde_align});
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
        doPost(path, {date: d1_str, sde_align: "top"});
        return;
    }

    el_cur_day.value = d1_str;
    scrollFlag = false;
    scrollToId(`date-${d1_str}`);
};

/**
 * TBD
 */
const editStr = (el0) => {
    console.log(`el0=${el0}`);
    let value = el0.innerHTML;
    console.log(`value=${value}`);
    const el_input = document.createElement("input");
    el_input.type="text";
    el_input.value = value;
    console.log(`el_input=${el_input.type}`);

    el0.replaceChildren(el_input);
    el0.onclick="";
    el0.onchange= () => {
        console.log(`value=${el_input.value}`);
    };
};
