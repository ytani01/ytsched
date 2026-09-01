/**
 *   (c) 2026 ytani01
 */

// trash.html だけで使うリスナー登録 (TODO-139)。
// ``data-confirm`` 属性を持つ <form> の送信をフックし、confirm() が
// キャンセルされたら送信しない（inline event handler は TODO-108 で
// 禁止しているため）。

(() => {
  const onSubmit = (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    const message = form.dataset.confirm;
    if (message === undefined) {
      return;
    }
    if (!window.confirm(message)) {
      event.preventDefault();
    }
  };

  window.addEventListener("load", () => {
    document.addEventListener("submit", onSubmit);
  });
})();
