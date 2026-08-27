/**
 *   (c) 2026 ytani01
 */

// main.html だけで使う関数・リスナー登録 (TODO-083)。テンプレートの
// 値 (``search_str0`` / ``today_str``) は main.html の <script> で
// 定数にしてから、この後ろで読み込まれる

let clickCount = 0;

const homeButtonHdr = (event) => {
  if( !clickCount ) { // single click
                       ++clickCount;
	     setTimeout(function() {clickCount = 0;}, 350 );
    console.log("single click");

    console.log(`search_str0=${search_str0}`);
    if ( search_str0 ) {
      const el_search = document.getElementById("search_str");
      const search_str = el_search.value;
      console.log(`search_str=${search_str}`);
      // search_str は URL に載せない (TODO-050)
      doPost(url_prefix,
             {
               date: today_str,
               search_str: search_str
             } );
    }
    scrollToDate(url_prefix, today_str, 'top');

  } else { // double click
    //event.preventDefault() ;
	     clickCount = 0;
	     console.log( "double click" ) ;

    // データを読み直す (TODO-069)。前後数ヶ月ぶんを DOM に持つ
    // ようになったので、抱えたまま古くなる。ダブルタップが、
    // 手で取り直す道
    doGet(url_prefix,
           {date: today_str, sde_align: 'top'} );
  }
};

const onloadHdr = (event) => {
  console.log(`onloadHdr(${event}`);
  ytState.elLoadingSpinner = document.getElementById("loadingSpinner");
  loadingSpinner(false);

  ytState.elMain = document.getElementById("main"); // declared in state.js
  ytState.elWeekWrap = document.getElementById("week_wrap"); // declared in state.js

  // 読み込んだ直後は、真ん中の週 (offset 0) を見ている。
  // サーバも同じ形で描いているので並べ直す必要は無いが、
  // ``my-week-near`` はサーバが付けないのでここで付ける (TODO-069)
  ytState.activeWeekOffset = 0; // declared in state.js
  layoutWeeks();

  const elMenuBar = document.getElementById("menu_bar");
  const menu_bar_height = elMenuBar.offsetHeight;
  document.body.style.paddingBottom = `${menu_bar_height}px`;

  // 週バーは position: fixed なので、その高さぶんを空ける
  // (TODO-055)。body_h を測るより先に入れること。
  // 検索モードでは週バーが無いので、そのときは 0 のまま
  const elWeekBar = document.getElementById("week_bar");
  if ( elWeekBar ) {
    document.body.style.paddingTop = `${elWeekBar.offsetHeight}px`;
  }

  const body_h = document.body.clientHeight;
  const win_h = document.documentElement.clientHeight;

  ytState.elGaugeR0 = document.getElementById("gauge_r"); // declared in state.js
  // 目盛りの位置は日付によらないので、ここで一度だけ描く (TODO-078)
  dispGaugeMarks();

  if ( body_h < win_h ) {
    console.log(`body_h=${body_h} < win_h=${win_h}`);
    // ゲージの都合で画面が出ないのはおかしいので、dispGauge() より
    // 先に visible にする (TODO-049 reviewer 指摘 1)
    ytState.elMain.style.visibility = "visible";
    const date_from_str = document.getElementById("date_from").value;
    dispGauge(date_from_str);
    return;
  }

  const el_sde_align = document.getElementById("sde_align");
  const el_date = document.getElementById("date");
  // 読み直したあとの位置合わせは一度で移す。"auto" は CSS の
  // scroll-behavior に従うので、Bootstrap 5 の :root の指定で
  // アニメーションになってしまう (TODO-041)
  // 読み直した直後なので、履歴には積まない (TODO-050)
  scrollToDate(location.pathname,
               el_date.value, el_sde_align.value,
               "instant", false);

  // 週表示になり、スクロールでの追加読み込みが無くなったので、
  // 検索の有無によらず一度だけゲージを合わせる (TODO-049)
  const date_from_str = document.getElementById("date_from").value;
  dispGauge(date_from_str);
}; // onloadHdr()

const changeSearchN = (val) => {
  console.log(`changeSearchN: val=${val}`);
  // search_n は URL に載せない (TODO-050)
  doPost(url_prefix, {date: document.getElementById("cur_day").value, search_n: val} );
};

window.addEventListener('load', onloadHdr);
// キーボードでの操作は一覧だけ (TODO-050)
window.addEventListener('keydown', keyHdr);
// 画面内で完結した移動から戻ってきたとき (TODO-050)
window.addEventListener('popstate', popstateHdr);
// 左右のスワイプで週を送るのも一覧だけ (TODO-054)。
// touchmove だけ passive: false (TODO-057)。横の動きと判定した
// あと preventDefault() で縦スクロールを止めないと、指に追従
// できない。他の 3 つは縦スクロールを邪魔しないので passive のまま
window.addEventListener('touchstart', touchStartHdr, {passive: true});
window.addEventListener('touchmove', touchMoveHdr, {passive: false});
window.addEventListener('touchend', touchEndHdr, {passive: true});
window.addEventListener('touchcancel', touchCancelHdr, {passive: true});
// PC のマウスの左右ドラッグでも週を送る (TODO-064)。
// mousedown だけ capture で拾って伝播を止める。日付セルなどの
// onmousedown は押した瞬間に遷移してしまい、そのままでは
// セルの上からドラッグを始められない。動かずに離したときは、
// mouseUpHdr が止めておいた onmousedown を自前で呼ぶ
window.addEventListener('mousedown', mouseDownHdr, true);
window.addEventListener('mousemove', mouseMoveHdr);
window.addEventListener('mouseup', mouseUpHdr);
