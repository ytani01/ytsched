/**
 *   (c) 2026 ytani01
 */

// edit.html だけで使う関数・リスナー登録 (TODO-089)。
//
// 外へ出すもの:
//   submitCmd()    -- edit.html の各ボタンの onmousedown、detail の onchange
//   update_wday()  -- edit.html の #date の onchange
//   setElDate()    -- edit.html の日付ボタンの onmousedown
//   changeElDate() -- edit.html の日付ボタンの onmousedown
//   onloadEdit() は window の load でこのファイルが登録し、changeDetailHeight()
//     も別の load ハンドラから呼ぶ。mkInput() / wdayList / busyFlag は
//     このファイル内だけで使う
// 外から使うもの:
//   ytState (state.js)            -- onloadEdit が ytState.elLoadingSpinner をセット
//   loadingSpinner() (spinner.js) -- submitCmd・onloadEdit

(() => {
const ytsched = window.ytsched;
const wdayList = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const mkInput = (cmd) => {
  const input = document.createElement("input");
  input.setAttribute("type", "hidden");
  input.setAttribute("name", "cmd");
  input.setAttribute("value", cmd);
  return input;
};

let busyFlag = false;

window.ytsched.submitCmd = (cmd) => {
  if (busyFlag) {
    return;
  }
  busyFlag = true;
  console.log(`cmd=${cmd}`);
  const form = document.forms["input_form"];
  form.appendChild(mkInput(cmd));
  ytsched.loadingSpinner(true);
  form.submit();
};

window.ytsched.update_wday = (el_date) => {
  if (el_date === undefined) {
    el_date = document.getElementById("date");
  }
  const d1 = new Date(el_date.value);

  const el_wday = document.getElementById("wday");
  el_wday.innerHTML = wdayList[d1.getDay()];
};

window.ytsched.setElDate = (date_value, el_date) => {
  let d1 = new Date(); // today
  if (date_value) {
    d1 = new Date(date_value);
  }
  if (el_date === undefined) {
    el_date = document.getElementById("date");
  }
  el_date.value = d1.toISOString().replace(/T.*$/, "");

  ytsched.update_wday(el_date);
};

window.ytsched.changeElDate = (d, el_date) => {
  if (el_date === undefined) {
    el_date = document.getElementById("date");
  }
  let d1 = new Date(el_date.value);
  d1.setDate(d1.getDate() + d);

  ytsched.setElDate(d1, el_date);
};

const changeDetailHeight = () => {
  const el_detail = document.getElementById("detail");
  const detail_y = el_detail.parentElement.offsetTop;

  const el_id = document.getElementById("div_id");
  const id_h = el_id.offsetHeight;

  const win_h = document.documentElement.clientHeight;
  let detail_h = win_h - detail_y - id_h - 7 - 150;
  if (detail_h < 100) {
    detail_h = 100;
  }

  el_detail.style.height = `${detail_h}px`;
};

const onloadEdit = () => {
  ytsched.ytState.elLoadingSpinner = document.getElementById("loadingSpinner");
  ytsched.loadingSpinner(false);
};

window.addEventListener("load", function () {
  changeDetailHeight();
});
window.addEventListener("load", onloadEdit);
})();
