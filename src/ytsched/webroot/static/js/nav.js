/**
 *   (c) 2026 ytani01
 */

// URL と遷移 (TODO-083)
//
// 外へ出すもの:
//   shiftDays()              -- gauge.js (mondayOf)・week.js (weekOffsetOfDate)
//   getLocaltimeString()     -- week.js (setActiveWeek)
//   getLocaltimeDateString() -- gauge.js・week.js・keyboard.js・main-page.js の
//                               日付計算から
//   calcDays()               -- gauge.js (setGaugePosition)
//   doGet()    -- main.html・sde.html・edit.html の onmousedown / onchange、
//                week.js (moveToMonday)・main-page.js から
//   doPost()   -- main.html の onmousedown、main-page.js から
//   doSubmit() / doGetDate() -- main.html の onmousedown / onchange
//   scrollToId()    -- week.js (setActiveWeek)
//   scrollToDate()  -- gauge.js (gaugeBarClickHdr)・keyboard.js (keyHdr)・
//                      main-page.js (homeButtonHdr / onloadHdr)
//   pushDateInUrl() -- week.js (setActiveWeek)
//   popstateHdr()   -- main-page.js が window の popstate に登録する
//   mkUrl() / replaceDateInUrl() はこのファイル内だけで使う
// 外から使うもの:
//   ytState (state.js)            -- elMain・activeWeekOffset・activeMonday
//   loadingSpinner() (spinner.js) -- doSubmit・doGet・doPost
//   weekOffsetOfDate() (week.js)  -- popstateHdr・scrollToDate
//   setActiveWeek() (week.js)     -- popstateHdr・scrollToDate
// week.js は base.html でこのあとに読み込まれるが、呼ぶのは実行時なので前方参照でよい

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
  const offset_msec = (d.getTimezoneOffset() / 60) * 3600 * 1000;
  const localtime_msec = utc_msec - offset_msec;
  const local_d = new Date(localtime_msec);
  const localtime_str = local_d.toISOString().slice(0, -1);
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
  return getLocaltimeString(d).replace(/T.*$/, "");
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
  const days = (d_to - d_from) / (24 * 60 * 60 * 1000);
  return days;
};

/**
 *
 */
const doSubmit = (id) => {
  loadingSpinner(true);
  const el = document.getElementById(id);
  // 表示中の週の月曜を hidden の cur_day に載せてから送る (TODO-093)
  for (const cd of el.querySelectorAll('[name="cur_day"]')) {
    cd.value = ytState.activeMonday;
  }
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
  if (!query) {
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
  history.pushState({ date: date }, "", url.toString());
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
  history.replaceState({ date: date }, "", url.toString());
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

  if (!date) {
    location.reload();
    return;
  }

  const offset = weekOffsetOfDate(date);
  if (offset !== null && offset !== ytState.activeWeekOffset) {
    setActiveWeek(offset, false);
  }

  // 画面内にあればスクロールで済ませる。無ければ読み直す
  if (scrollToId(`date-${date}`, "top", "auto")) {
    ytState.activeMonday = date;
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
  let d1 = new Date(date.split("-").join("/"));
  d1 = shiftDays(d1, days);
  d1_str = getLocaltimeDateString(d1);
  console.log(`date=${date}, d1_str=${d1_str}`);

  data_obj = { date: d1_str };
  if (sde_align) {
    data_obj.sde_align = sde_align;
  }
  doGet(path, data_obj);
};

/**
 *
 */
const scrollToId = (id, sde_align = "top", behavior = "smooth") => {
  console.log(`scrollToId:id=${id}`);

  ytState.elMain.style.visibility = "visible";

  // 目的の要素が DOM にあるかどうかを、「1 画面に収まっているか」
  // より先に見る (TODO-049)。週表示になり、予定の少ない週では
  // 1 画面に収まる (body_h <= win_h) ことが増えた。それだけで
  // 「スクロールで用が足りた」= true を返すと、DOM に無い日
  // (表示中の週の外) を指されたときも true になり、呼び出し元の
  // scrollToDate() が doGet() での読み直しを飛ばしてしまう
  // (URL だけ書き換わって画面が変わらない不具合になった)。
  const el = document.getElementById(id);
  const el_search = document.getElementById("search_str");
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
    scrollTo({ left: 0, top: top_of_el - scroll_offset, behavior: behavior });
  }
  if (sde_align == "bottom") {
    scrollTo({
      left: 0,
      top: bottom_of_el - win_h + menu_bar_h + scroll_offset,
      behavior: behavior,
    });
  }

  return true;
};

/**
 *
 */
const scrollToDate = (
  path,
  date,
  sde_align = "top",
  behavior = "smooth",
  push_flag = true,
) => {
  console.log(`scrollToDate:date=${date}, sde_align=${sde_align}`);

  // 表示していない週の日付なら、まず週を移す (TODO-069)。
  // ``date-YYYY-mm-dd`` は前後数ヶ月ぶんの週すべてにあるので、
  // 週を移さずにスクロールすると、隠れている週へ寄せてしまう。
  // URL はこのあとこの関数が ``date`` で書き換えるので、ここでは
  // 積まない
  const offset = weekOffsetOfDate(date);
  if (offset !== null && offset !== ytState.activeWeekOffset) {
    setActiveWeek(offset, false);
  }

  if (scrollToId(`date-${date}`, sde_align, behavior)) {
    ytState.activeMonday = date;
    // 読み直した直後 (``push_flag``が偽) は履歴に積まない。
    // 読み直しそのもので 1つ増えているため (TODO-050)
    if (push_flag) {
      pushDateInUrl(date);
    } else {
      replaceDateInUrl(date);
    }
    return true;
  }

  console.log(`path=${path}`);
  doGet(path, { date: date, sde_align: sde_align });
  return false;
};
