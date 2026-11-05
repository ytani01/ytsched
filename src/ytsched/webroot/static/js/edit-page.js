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
//   keyDownHdr() は onloadEdit が #input_form の keydown に登録する
//   onloadEdit() は window の load でこのファイルが登録する。
//     changeDetailHeight() は別の load ハンドラと、window の resize・
//     #detail の blur から呼ぶ。fillDetailHeight() (TODO-227) は、#detail の
//     入力中に画面が基準の高さ (baseHeight) より縮んでいる (Android の
//     キーボード表示) とき、#detail の focus・window の resize から呼ぶ。mkInput() / wdayList / busyFlag は
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

  // 「縮んでいる」かを見る基準の高さ。入力欄にフォーカスが無いときの
  // resize で更新する。キーボードはフォーカス中にしか出ないので、
  // そのときの変化はウィンドウの変更や画面の回転とみなせる (TODO-227)
  let baseHeight = 0;
  let lastHeight = 0;
  let detailFilled = false;

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
    detailFilled = false;
  };

  // 入力中に画面が縮んだら、#detail を上下のバーの間いっぱいに広げ、
  // 上端が上のバーのすぐ下に来るまでページを動かす (TODO-227)。
  const fillDetailHeight = () => {
    const el_detail = document.getElementById("detail");
    const top_h = document.querySelector(".my-edit-bar-top").offsetHeight;
    const bottom_h = document.querySelector(".my-edit-bar-bottom").offsetHeight;
    const win_h = document.documentElement.clientHeight;

    el_detail.style.height = `${Math.max(win_h - top_h - bottom_h, 100)}px`;
    detailFilled = true;
    window.scrollTo(
      0,
      el_detail.getBoundingClientRect().top + window.scrollY - top_h,
    );
  };

  const isDetailShrunk = () =>
    document.activeElement === document.getElementById("detail") &&
    document.documentElement.clientHeight < baseHeight;

  const resizeHdr = () => {
    if (baseHeight === 0) {
      return; // load の前は #detail がまだ無いことがある
    }
    const win_h = document.documentElement.clientHeight;
    if (!document.activeElement.matches("input, textarea, select")) {
      baseHeight = win_h;
    }
    if (isDetailShrunk()) {
      fillDetailHeight();
    } else if (win_h !== lastHeight) {
      // 幅だけの変化では、手で変えた高さを戻さない
      changeDetailHeight();
    }
    lastHeight = win_h;
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
      case "back":
        ytsched.doGet(ytsched.url_prefix, { date: el.dataset.date });
        break;
      case "submit-cmd":
        ytsched.submitCmd(el.dataset.cmd);
        break;
      case "date-change":
        ytsched.changeElDate(Number(el.dataset.days));
        break;
      case "date-today":
        ytsched.setElDate();
        break;
    }
  };

  const actionChangeHdr = (event) => {
    const el = actionElement(event);
    if (!el) {
      return;
    }
    if (el.dataset.action === "update-wday") {
      ytsched.update_wday(el);
    } else if (el.dataset.action === "update-detail") {
      ytsched.submitCmd("update");
    }
  };

  // Ctrl+Enter (Mac は Cmd+Enter も) で確定する (TODO-226)。
  // 変換中の Enter は IME の確定なので無視する
  const keyDownHdr = (event) => {
    if (event.key !== "Enter" || event.isComposing) {
      return;
    }
    if (event.ctrlKey || event.metaKey) {
      event.preventDefault();
      ytsched.submitCmd("fix");
    }
  };

  const onloadEdit = () => {
    ytsched.ytState.elLoadingSpinner =
      document.getElementById("loadingSpinner");
    ytsched.loadingSpinner(false);
    document
      .getElementById("edit_main")
      .addEventListener("mousedown", actionMouseDownHdr);
    document
      .getElementById("edit_main")
      .addEventListener("change", actionChangeHdr);
    document
      .getElementById("input_form")
      .addEventListener("keydown", keyDownHdr);
    const el_detail = document.getElementById("detail");
    el_detail.addEventListener("focus", () => {
      if (isDetailShrunk()) {
        fillDetailHeight();
      }
    });
    el_detail.addEventListener("blur", () => {
      // 広げていないときは、手で変えた高さを戻さない
      if (detailFilled) {
        changeDetailHeight();
      }
    });
    // ボタンバーが上下 2 か所にあるので、両方にリスナーを付ける (TODO-177)
    document.querySelectorAll(".my-edit-bar").forEach((el) => {
      el.addEventListener("mousedown", actionMouseDownHdr);
    });
  };

  window.addEventListener("load", function () {
    baseHeight = lastHeight = document.documentElement.clientHeight;
    changeDetailHeight();
  });
  window.addEventListener("resize", resizeHdr);
  window.addEventListener("load", onloadEdit);
})();
