/**
 *   (c) 2026 ytani01
 */

// 横ゲージ (TODO-083)

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

    ytState.elGaugeR0.style.left = `${50 + days2xPercent(top_rel_days)}%`;

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
    ytState.elGaugeR0.classList.add("my-gauge-r-no-transition");
    setGaugePosition(date_str);
    ytState.elGaugeR0.getBoundingClientRect(); // 強制的にレイアウトを確定させる
    ytState.elGaugeR0.classList.remove("my-gauge-r-no-transition");
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
    if ( ! ytState.elGaugeR0 ) {
        return;
    }

    if ( ! date_str ) {
        ytState.elGaugeR0.style.display = "none";
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
