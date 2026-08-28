/**
 *   (c) 2026 ytani01
 */

// スピナー (TODO-083)
//
// 外へ出すもの:
//   loadingSpinner() -- nav.js (doSubmit / doGet / doPost)・main-page.js
//     (onloadHdr)・edit-page.js (submitCmd / onloadEdit) から呼ぶ。
//     ほかに window の pageshow リスナーをこのファイルで登録する
// 外から使うもの:
//   ytState (state.js) -- ytState.elLoadingSpinner

/**
 *
 */
const loadingSpinner = (on) => {
    if (on) {
        ytState.elLoadingSpinner.style.display = "block";
    } else {
        ytState.elLoadingSpinner.style.display = "none";
    }
};

/**
 * bfcache (戻る/進むで復元されるキャッシュ)から戻ってきたときは
 * ``load``が起きないので、``doGet()``などで出したスピナーが
 * 出たままになる (TODO-068)。``pageshow``で消す。
 *
 * ``ytState.elLoadingSpinner``は各ページの ``load`` ハンドラ
 * (``onloadHdr()`` / ``onloadEdit()``)が入れているが、
 * 復元されたときの値を当てにせず、ここで取り直す。
 */
window.addEventListener("pageshow", (event) => {
    if (! event.persisted) {
        return;
    }
    ytState.elLoadingSpinner = document.getElementById("loadingSpinner");
    if (ytState.elLoadingSpinner) {
        loadingSpinner(false);
    }
});
