/**
 *   (c) 2026 ytani01
 */

// キーボード (TODO-083)
//
// 外へ出すもの:
//   keyHdr() -- main-page.js が window の keydown に登録する
//   followKeyboard() は visualViewport / window のリスナーとしてこのファイルで
//     登録し、isTyping() は keyHdr() だけで使う
// 外から使うもの:
//   moveToMonday() (week.js)          -- keyHdr (← →)
//   getLocaltimeDateString() (nav.js) -- keyHdr (Home)
//   scrollToDate() (nav.js)           -- keyHdr (Home)
//   url_prefix (base.html の <script>) -- keyHdr が moveToMonday / scrollToDate へ渡す
// keyHdr 内の today_str はこの関数のローカル変数で、main.html の today_str とは別物

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
  if (!vv) {
    return;
  }
  let offset = 0;
  if (vv.scale <= 1.01) {
    const gap = window.innerHeight - vv.height - vv.offsetTop;
    offset = Math.max(0, Math.round(gap));
  }
  const els = document.getElementsByClassName("my-follow-keyboard");
  for (const el of els) {
    el.style.transform = `translateY(${-offset}px)`;
  }
};

if (window.visualViewport) {
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
  if (!el) {
    return false;
  }
  const tag = el.tagName.toLowerCase();
  if (tag === "input" || tag === "textarea" || tag === "select") {
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
  if (isTyping()) {
    if (event.key === "Escape") {
      document.activeElement.blur();
    }
    return;
  }

  if (event.ctrlKey || event.altKey || event.metaKey) {
    return;
  }

  switch (event.key) {
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
      if (el_search) {
        el_search.focus();
      }
      break;
    }
  }
};
