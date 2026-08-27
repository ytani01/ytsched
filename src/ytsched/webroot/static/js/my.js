/**
 *   (c) 2026 ytani01
 */

let elLoadingSpinner;
let elMain;
let elGaugeR0;
// 前週・今週・次週をまとめたラッパー (TODO-057)。指の追従・週送りの
// アニメーションで動かす
let elWeekWrap;

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
 * bfcache (戻る/進むで復元されるキャッシュ)から戻ってきたときは
 * ``load``が起きないので、``doGet()``などで出したスピナーが
 * 出たままになる (TODO-068)。``pageshow``で消す。
 *
 * ``elLoadingSpinner``は各ページの ``onloadHdr()``が入れているが、
 * 復元されたときの値を当てにせず、ここで取り直す。
 */
window.addEventListener("pageshow", (event) => {
    if (! event.persisted) {
        return;
    }
    elLoadingSpinner = document.getElementById("loadingSpinner");
    if (elLoadingSpinner) {
        loadingSpinner(false);
    }
});

// 横ゲージ (TODO-058)。以前は ``main_handler.py`` にも同じ定数・同じ式が
// あったが、二重に持つのをやめて JavaScript 側だけに寄せた (TODO-078)
const DAYS_YEAR = 365.25;
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
const days2xPercent = (days) => {
    // console.log(`days=${days}`);
    let xPercent = 50.0 * Math.log10(1 + Math.abs(days) / DAYS_GAUGE_K)
          / Math.log10(1 + DAYS_GAUGE_MAX / DAYS_GAUGE_K);
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
const xPercent2days = (xPercent) => {
    const abs_xPercent = Math.abs(xPercent);
    const exponent = abs_xPercent / 50.0
          * Math.log10(1 + DAYS_GAUGE_MAX / DAYS_GAUGE_K);
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
    { label: "-3m", days: -DAYS_MONTH * 3 },
    { label: "-1m", days: -DAYS_MONTH },
    { label: "-1w", days: -7 },
    { label: "+1w", days: +7 },
    { label: "+1m", days: +DAYS_MONTH },
    { label: "+3m", days: +DAYS_MONTH * 3 },
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
 * 検索モードでは週バーごと ``.my-gauge-bar`` が無いので、そのときは
 * 何もしない。
 */
const dispGaugeMarks = () => {
    const elGaugeBar = document.querySelector(".my-gauge-bar");
    if ( ! elGaugeBar ) {
        return;
    }

    for (const mark of GAUGE_MARKS) {
        const elMark = document.createElement("div");
        elMark.className = "my-gauge-label";
        elMark.style.left = `${(50 + days2xPercent(mark.days)).toFixed(2)}%`;
        elMark.textContent = mark.label;
        elGaugeBar.appendChild(elMark);
    }
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
const gaugeDiffLabel = (days) => {
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
 * 針の位置 (``left``) を計算してセットする。``transition`` は
 * 掛けたまま (TODO-049)。針の上のラベル (今週からの差) も、
 * ここで書き換える。位置は入れ物 (``#gauge_r``) が持っているので、
 * ラベルは黙って一緒に動く (TODO-066)。
 *
 * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい。
 *   月曜へ丸めてから、今週の月曜との差を見る)
 */
const setGaugePosition = (date_str) => {
    const monday = mondayOf(date_str);
    const this_monday = mondayOf(getLocaltimeDateString(new Date()));
    const top_rel_days = calcDays(this_monday, monday);

    elGaugeR0.style.left = `${50 + days2xPercent(top_rel_days)}%`;

    // どちらも月曜なので、7 で割り切れる
    const elLabel = document.getElementById("gauge_r_label");
    if (elLabel) {
        elLabel.textContent = gaugeDiffLabel(Math.round(top_rel_days / 7) * 7);
    }
};

// 直前に見ていた週の月曜 (TODO-049)。ページを読み直したあと、
// この位置からいまの週へ針を動かして見せるために使う
const GAUGE_MONDAY_KEY = "ytsched_gauge_monday";

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
const getGaugeMonday = () => {
    try {
        return sessionStorage.getItem(GAUGE_MONDAY_KEY);
    } catch (e) {
        console.log(`getGaugeMonday: ${e}`);
        return null;
    }
};

/**
 * ``sessionStorage`` へ今の週の月曜を書く。書けなくても黙って諦める
 * (TODO-049。理由は ``getGaugeMonday()`` を参照)。
 *
 * @param {String} monday_str   'YYYY-mm-dd'
 */
const setGaugeMonday = (monday_str) => {
    try {
        sessionStorage.setItem(GAUGE_MONDAY_KEY, monday_str);
    } catch (e) {
        console.log(`setGaugeMonday: ${e}`);
    }
};

/**
 * ``transition`` を効かせずに、いったんその位置へ針を置く。
 *
 * レイアウトを確定させるのに ``getBoundingClientRect()`` を使う
 * (TODO-060)。確定しないまま ``transition`` が戻ると、CSS の初期値
 * (``left: 50%``、つまり中央) から補間が始まってしまう。
 * ``#gauge_r`` が ``<svg>`` だったころは ``offsetHeight`` が
 * ``undefined`` を返してレイアウトが確定せず、これで踏んだ
 * (いまは針とラベルをまとめた ``<div>``。TODO-066)。
 *
 * @param {String} date_str   'YYYY-mm-dd'
 */
const placeGaugeWithoutTransition = (date_str) => {
    elGaugeR0.classList.add("my-gauge-r-no-transition");
    setGaugePosition(date_str);
    elGaugeR0.getBoundingClientRect(); // 強制的にレイアウトを確定させる
    elGaugeR0.classList.remove("my-gauge-r-no-transition");
};

/**
 * ゲージの針を動かす。
 *
 * ``sessionStorage`` に前回表示していた週の月曜を持っていれば、まず
 * ``transition`` を効かせずにその位置へ針を置き、次のフレームで
 * 今の週へ動かす (TODO-049)。ページを読み直すたびに呼ばれるので、
 * ``transition`` だけでは針の初期値が "auto" のままで補間が起きず、
 * 動いて見えない。``sessionStorage`` が使えない環境でも、針の位置を
 * 合わせること自体は続ける (``getGaugeMonday()``/``setGaugeMonday()``
 * が例外を握りつぶす)。
 *
 * @param {String} date_str   'YYYY-mm-dd' (週の中の何日でもよい)
 */
const dispGauge = (date_str) => {
    // 検索モードでは週バーごと帯が出ないので、gauge_r が無い (TODO-058)
    if ( ! elGaugeR0 ) {
        return;
    }

    if ( ! date_str ) {
        elGaugeR0.style.display = "none";
        return;
    }

    const monday_str = getLocaltimeDateString(mondayOf(date_str));
    const prev_monday_str = getGaugeMonday();
    setGaugeMonday(monday_str);

    if (prev_monday_str && prev_monday_str !== monday_str) {
        placeGaugeWithoutTransition(prev_monday_str);
        requestAnimationFrame(() => {
            setGaugePosition(monday_str);
        });
        return;
    }

    // 動かす先が無いので、そのまま置く。``setGaugePosition()`` を直に
    // 呼ぶと、針の ``left`` が CSS の初期値 (``left: 50%``) のままな
    // ので、中央から目的地まで transition が掛かる (TODO-060)
    placeGaugeWithoutTransition(monday_str);
};

/**
 * ゲージの帯 (``.my-gauge-bar``) をタップ・クリックしたら、その位置が
 * 指す週の月曜へ移る (TODO-074)。ドラッグでの追従は無く、タップした
 * 瞬間の位置だけを見る。範囲の頭打ちも無い (逆算した先へそのまま飛ぶ)。
 *
 * ``.my-gauge-bar`` に ``onmousedown`` 属性で登録してある。ここが
 * 呼ばれるまでの経路は、既存のボタン (``moveToMonday()`` など) と同じ
 * (``mouseDownHdr()`` / ``mouseUpHdr()`` を参照)。マウスは、押した位置
 * から動かずに離すとクリックと見なされ、``mouseUpHdr()`` がここへ
 * ``mouseup`` の event を渡して呼ぶ。動いていない前提なので、
 * ``event.clientX`` は押したときと同じ位置を指す。タッチも、動きが
 * 無ければブラウザが作る合成 ``mousedown``/``mouseup`` がそのまま
 * 素通りして同じ経路を通る (``mouseDownHdr()`` の
 * ``MOUSE_AFTER_TOUCH_MSEC`` を参照)。どちらの経路でも
 * ``target``/``currentTarget`` が指す要素は食い違うことがあるので、
 * それには頼らず ``.my-gauge-bar`` 自体を取り直す (検索モードでは
 * 週バーごと出ないので見つからない。TODO-058 と同じ前提)。
 *
 * 帯の左端を 0%・右端を 100% として、中央 (50%) からの割合を
 * ``xPercent2days()`` に渡し、今週の月曜からの日数を出す。
 *
 * @param {Event} event
 */
const gaugeBarClickHdr = (event) => {
    const el_bar = document.querySelector(".my-gauge-bar");
    if ( ! el_bar ) {
        return;
    }

    const rect = el_bar.getBoundingClientRect();
    const x_percent = (event.clientX - rect.left) / rect.width * 100 - 50;
    const days = xPercent2days(x_percent);

    const this_monday = mondayOf(getLocaltimeDateString(new Date()));
    const target_date = shiftDays(this_monday, Math.round(days));
    const monday = mondayOf(getLocaltimeDateString(target_date));

    // パスは onloadHdr() と同じく location.pathname でよい (TODO-074)
    scrollToDate(location.pathname, getLocaltimeDateString(monday));
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
 *
 * **まず週を移してから、日付へ寄せる** (TODO-069)。前後数ヶ月ぶんを
 * DOM に持つようになったので、``date-YYYY-mm-dd`` は表示していない週
 * にもある。週を移さずにスクロールだけすると、隠れている週へ寄せて
 * しまう。
 *
 * **週が分からなくても、そこで読み直しに倒さない。** 検索モードでは
 * 週の区切りに合わないので panel が月曜を持たず、
 * ``weekOffsetOfDate()`` はいつも null になる。「週が分からない」は
 * 「持っている範囲の外」ではないので、``scrollToDate()`` と同じく、
 * スクロールを試してから決める。
 */
const popstateHdr = (event) => {
    const date = new URL(location.href).searchParams.get("date");
    console.log(`popstateHdr:date=${date}`);

    if ( ! date ) {
        location.reload();
        return;
    }

    const offset = weekOffsetOfDate(date);
    if ( offset !== null && offset !== activeWeekOffset ) {
        setActiveWeek(offset, false);
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

    // 表示していない週の日付なら、まず週を移す (TODO-069)。
    // ``date-YYYY-mm-dd`` は前後数ヶ月ぶんの週すべてにあるので、
    // 週を移さずにスクロールすると、隠れている週へ寄せてしまう。
    // URL はこのあとこの関数が ``date`` で書き換えるので、ここでは
    // 積まない
    const offset = weekOffsetOfDate(date);
    if ( offset !== null && offset !== activeWeekOffset ) {
        setActiveWeek(offset, false);
    }

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

// 滑らせるアニメーションの長さ (msec)。CSS の
// ``.my-week-wrap-sliding`` の transition と合わせる (TODO-057)
const SWIPE_SLIDE_MSEC = 200;

// いま見ている週が、最初に描かれた週から何週ぶん離れているか
// (TODO-069)。``.my-week-panel`` の ``data-offset`` と同じ数え方で、
// 読み込んだ直後は 0
let activeWeekOffset = 0;

/**
 * ``offset`` の週の ``.my-week-panel`` を返す (TODO-069)。
 *
 * 読み込んだ範囲の外なら null。
 *
 * @param {number} offset
 * @return {Element | null}
 */
const weekPanelOf = (offset) => {
    if ( ! elWeekWrap ) {
        return null;
    }
    return elWeekWrap.querySelector(
        `.my-week-panel[data-offset="${offset}"]`);
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
    if ( ! elWeekWrap || ! date_str ) {
        return null;
    }
    const monday = getLocaltimeDateString(mondayOf(date_str));
    const panel = elWeekWrap.querySelector(
        `.my-week-panel[data-monday="${monday}"]`);
    if ( ! panel ) {
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
    return !! (weekPanelOf(activeWeekOffset - 1)
               || weekPanelOf(activeWeekOffset + 1));
};

/**
 * 週の並べ直し (TODO-069)。
 *
 * ``activeWeekOffset`` の週だけを通常フロー (``my-week-cur``) に
 * 残し、他は ``left`` で左右へ振り分ける。**通常フローに残す週を
 * 差し替えるのは、body の高さをその週に合わせるため**
 * (``position: absolute`` の週は高さを決めない)。
 *
 * 隣の 2 週にだけ ``my-week-near`` を付ける。指の追従中に見える
 * ようにするのはこの 2 週だけで、前後数ヶ月ぶんを全部見せない。
 */
const layoutWeeks = () => {
    if ( ! elWeekWrap ) {
        return;
    }
    const panels = elWeekWrap.querySelectorAll(".my-week-panel");
    for ( const panel of panels ) {
        const offset = Number(panel.dataset.offset);
        const rel = offset - activeWeekOffset;

        panel.classList.toggle("my-week-cur", rel === 0);
        panel.classList.toggle("my-week-near", Math.abs(rel) === 1);
        panel.style.left = `${rel * 100}%`;
    }
};

/**
 * いま見ている週を ``offset`` の週にする (TODO-069)。
 *
 * ページを読み直さずに、DOM の中だけで週を移る。並べ直したうえで、
 * 週に付いて回るもの (``#cur_day``・``#date``・``#date_from``・
 * ヘッダのゲージ) を、その週の月曜に揃える。
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
    if ( ! panel ) {
        return false;
    }

    activeWeekOffset = offset;
    layoutWeeks();

    // 滑らせ終わった位置から、ずらした分を戻す。並べ直しで見た目の
    // 位置は変わらないので、transition を掛けずに戻す
    elWeekWrap.classList.remove("my-week-wrap-sliding");
    elWeekWrap.classList.remove("my-week-wrap-dragging");
    elWeekWrap.style.transform = "";

    const monday = panel.dataset.monday;

    for ( const id of ["cur_day", "date", "date_from"] ) {
        const el = document.getElementById(id);
        if ( el ) {
            el.value = monday;
        }
    }

    if ( push_flag ) {
        pushDateInUrl(monday);
    }

    dispGauge(monday);
    scrollToId(`date-${monday}`, "top", "instant");

    return true;
};

// 走っている ``slideWeekWrap()`` の後始末 (リスナーを外し、タイマーを
// 消す)。呼び出しが重なったとき、次の呼び出しの先頭で使う (TODO-057)。
let cancelActiveSlide = null;

/**
 * ``elWeekWrap`` を ``target_x`` (px) まで滑らせてから ``on_done`` を
 * 呼ぶ (TODO-057)。
 *
 * 指の追従で途中まで動いていれば、その位置から続けて滑らせる
 * (``elWeekWrap.style.transform`` を見る)。追従無しの呼び出し
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
    if ( ! elWeekWrap || ! hasAdjacentWeek() ) {
        on_done();
        return;
    }

    if ( cancelActiveSlide ) {
        cancelActiveSlide();
        cancelActiveSlide = null;
    }

    elWeekWrap.classList.add("my-week-wrap-dragging");
    if ( ! elWeekWrap.style.transform ) {
        elWeekWrap.style.transform = "translateX(0px)";
    }
    void elWeekWrap.offsetWidth; // 強制的にレイアウトし、transition を効かせる

    let done = false;
    let timeoutId;
    const cleanup = () => {
        elWeekWrap.removeEventListener("transitionend", onEnd);
        clearTimeout(timeoutId);
    };
    const finish = () => {
        if ( done ) {
            return;
        }
        done = true;
        cancelActiveSlide = null;
        cleanup();
        elWeekWrap.classList.remove("my-week-wrap-sliding");
        on_done();
    };
    const onEnd = (event) => {
        if ( event.target !== elWeekWrap || event.propertyName !== "transform" ) {
            return;
        }
        finish();
    };

    cancelActiveSlide = () => {
        done = true;
        cleanup();
    };

    elWeekWrap.addEventListener("transitionend", onEnd);
    timeoutId = setTimeout(finish, SWIPE_SLIDE_MSEC + 100);

    elWeekWrap.classList.add("my-week-wrap-sliding");
    elWeekWrap.style.transform = `translateX(${target_x}px)`;
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
const moveToMonday = (direction=1, path) => {
    const el_cur_day = document.getElementById("cur_day");
    let cur_day = new Date(el_cur_day.value);
    console.log(`moveToMonday:path=${path}`);
    console.log(`moveToMonday:cur_day=${getLocaltimeString(cur_day)}`);

    let wday = cur_day.getDay(); // 0:Sun, 1:Mon, ..
    if (wday == 0) {
        wday = 7; // Sun: 0 --> 7
    }

    // まず ``cur_day`` をその週の月曜まで戻してから、前後へ 7 日
    // ずらす (TODO-063)。週の途中の日付から直に前の月曜を求めると、
    // 同じ週の月曜になって週が送れない
    const days = (1 - wday) + (direction > 0 ? 7 : -7);
    console.log(`moveToMonday:days=${days}`);

    let d1 = new Date(el_cur_day.value);
    d1 = shiftDays(d1, days);
    d1_str = getLocaltimeDateString(d1);
    console.log(`moveToMonday:d1_str=${d1_str}`);

    const win_w = document.documentElement.clientWidth;
    const target_x = direction > 0 ? -win_w : win_w;
    const next_offset = activeWeekOffset + direction;
    console.log(`moveToMonday:next_offset=${next_offset}`);

    slideWeekWrap(target_x, () => {
        if ( setActiveWeek(next_offset) ) {
            return;
        }
        doGet(path, {date: d1_str, sde_align: "top"});
    });
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

// 横に動いたと見なす最小の距離 (px)
const SWIPE_MIN_X = 60;

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
 * ``elWeekWrap`` が無いとき (このページに無い) も何もしない。
 */
const cancelSwipeDrag = () => {
    if ( ! swipeDragging ) {
        return;
    }
    swipeDragging = false;
    slideWeekWrap(0, () => {
        if ( elWeekWrap ) {
            elWeekWrap.style.transform = "";
            elWeekWrap.classList.remove("my-week-wrap-dragging");
        }
    });
};

/**
 * 動いている間、隣の週を指・マウスに追従させる (TODO-057)。
 *
 * 横の動きと判定するまでは何もしない (縦スクロールを邪魔しないため)。
 * 判定したあとは ``elWeekWrap`` に ``translateX()`` を掛ける。
 *
 * **追従しているかどうかを返す。** タッチではこれが true のときだけ
 * ``preventDefault()`` して縦スクロールを止める。
 *
 * @param {number} dx
 * @param {number} dy
 * @return {boolean}
 */
const swipeDragTo = (dx, dy) => {
    if ( ! swipeDragging ) {
        if ( Math.abs(dx) < SWIPE_MIN_X
             || Math.abs(dx) < Math.abs(dy) * SWIPE_X_PER_Y ) {
            return false;
        }
        if ( ! hasAdjacentWeek() ) {
            return false;
        }
        swipeDragging = true;
        if ( elWeekWrap ) {
            elWeekWrap.classList.add("my-week-wrap-dragging");
        }
    }

    if ( elWeekWrap ) {
        elWeekWrap.style.transform = `translateX(${dx}px)`;
    }
    return true;
};

/**
 * 離したときに、週を送るかどうかを決める (TODO-057)。
 *
 * **縦の動きが優勢なら送らない。** 1 週間分が画面に収まらない週では
 * 上下にスクロールするので、その動きを週送りと取り違えないようにする。
 *
 * **画面幅の 1/3 以上動いたか、速く払ったとき**に送る。それ以外は
 * 追従していた分を 0 へ戻す。左へ払ったら次の週、右へ払ったら前の週。
 *
 * @param {number} dx
 * @param {number} dy
 * @param {number} elapsed_msec
 * @return {boolean}   送ったら true
 */
const swipeFinish = (dx, dy, elapsed_msec) => {
    if ( Math.abs(dx) < SWIPE_MIN_X
         || Math.abs(dx) < Math.abs(dy) * SWIPE_X_PER_Y ) {
        cancelSwipeDrag();
        return false;
    }

    const win_w = document.documentElement.clientWidth;
    const velocity = elapsed_msec > 0
          ? Math.abs(dx) / elapsed_msec : Infinity;

    if ( Math.abs(dx) < win_w / 3 && velocity < SWIPE_FAST_PX_PER_MSEC ) {
        cancelSwipeDrag();
        return false;
    }

    console.log(`swipeFinish:dx=${dx}, dy=${dy}, velocity=${velocity}`);
    swipeDragging = false;
    moveToMonday(dx < 0 ? 1 : -1, url_prefix);
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
 */
const touchStartHdr = (event) => {
    lastTouchMsec = Date.now();
    swipeStart = null;
    cancelSwipeDrag(); // 前の指が離れ損なっていたときの後始末 (念のため)

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
const touchMoveHdr = (event) => {
    lastTouchMsec = Date.now();

    if ( event.touches.length !== 1 ) {
        swipeStart = null;
        cancelSwipeDrag();
        return;
    }

    if ( ! swipeStart ) {
        return;
    }

    const touch = event.touches[0];
    const dx = touch.clientX - swipeStart.x;
    const dy = touch.clientY - swipeStart.y;

    if ( swipeDragTo(dx, dy) ) {
        event.preventDefault();
    }
};

/**
 * 指が離れたとき (TODO-054)。
 *
 * 送るかどうかの判定は ``swipeFinish()`` に任せる。
 */
const touchEndHdr = (event) => {
    lastTouchMsec = Date.now();

    const start = swipeStart;
    swipeStart = null;

    if ( ! start ) {
        return;
    }
    if ( event.changedTouches.length !== 1 ) {
        cancelSwipeDrag();
        return;
    }

    const touch = event.changedTouches[0];
    swipeFinish(touch.clientX - start.x, touch.clientY - start.y,
                Date.now() - start.t);
};

/**
 * 途中で割り込まれたとき (TODO-054)。
 */
const touchCancelHdr = () => {
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
 */
const mouseDownHdr = (event) => {
    if ( Date.now() - lastTouchMsec < MOUSE_AFTER_TOUCH_MSEC ) {
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

    if ( event.button !== 0 ) {
        return;
    }

    const el = event.target;
    if ( ! el || ! el.closest ) {
        return;
    }
    if ( el.closest("input, textarea, select, label, a") ) {
        return;
    }

    event.stopPropagation();
    event.preventDefault(); // ドラッグ中に文字が選択されないように

    mouseDownEl = el.closest("[onmousedown]");
    swipeStart = {x: event.clientX, y: event.clientY, t: Date.now()};
};

/**
 * マウスを動かしている間 (TODO-064)。
 *
 * ボタンが離れていたら (ウィンドウの外で離したときなど) 後始末する。
 * ``mouseup`` はウィンドウの外では来ないので、ここで気づくしかない。
 */
const mouseMoveHdr = (event) => {
    if ( ! swipeStart ) {
        return;
    }
    if ( ! (event.buttons & 1) ) {
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
const mouseUpHdr = (event) => {
    const start = swipeStart;
    const el = mouseDownEl;
    swipeStart = null;
    mouseDownEl = null;

    if ( ! start ) {
        return;
    }
    if ( event.button !== 0 ) {
        cancelSwipeDrag();
        return;
    }

    // 追従を始めていなければ、どれだけ動いていてもクリックと見なす
    // (TODO-064)。「少しだけ動いた」を除いてしまうと、押してから
    // 離すまでに手がぶれただけのときに、クリックとしても週送りとしても
    // 扱われず、黙って何も起きない範囲ができる。マウスには縦スクロール
    // のためのドラッグが無いので、追従していない動きはクリックでよい
    if ( ! swipeDragging ) {
        if ( el && typeof el.onmousedown === "function" ) {
            // 渡しているのは ``mouseup`` の event。今のテンプレートの
            // ``onmousedown`` は event を見ていないので困らないが、
            // 見るものを足すときはここを思い出すこと
            el.onmousedown(event);
        }
        return;
    }

    swipeFinish(event.clientX - start.x, event.clientY - start.y,
                Date.now() - start.t);
};
