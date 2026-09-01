/**
 *   (c) 2026 ytani01
 */

// trash.html だけで使う選択・確認のリスナー登録 (TODO-141)。

(() => {
  window.addEventListener("load", () => {
    // ytsched.doGet() が loadingSpinner() を呼ぶので、他の画面と
    // 同じく elLoadingSpinner を用意しておく (TODO-149)。表示時は
    // 隠すのを忘れていて回りっぱなしになっていた (TODO-150)
    window.ytsched.ytState.elLoadingSpinner =
      document.getElementById("loadingSpinner");
    window.ytsched.loadingSpinner(false);

    // 日付欄を押したら、その日を含む週の週間表示へ移る (TODO-149)。
    // 月間表示の日付セルと同じ動き。sde_align=top でその日を上端に
    // 寄せる。view は付けない (週間表示で開く)
    document.querySelectorAll('[data-action="week-date"]').forEach((el) => {
      el.addEventListener("mousedown", () => {
        window.ytsched.doGet(window.ytsched.url_prefix, {
          date: el.dataset.date,
          sde_align: "top",
        });
      });
    });

    const form = document.querySelector("#trash-delete-form");
    const all = document.querySelector("#trash-select-all");
    const entries = [
      ...document.querySelectorAll(".my-trash-entry .my-trash-select"),
    ];
    const button = form.querySelector("button");

    const update = () => {
      const selected = entries.filter((entry) => entry.checked);
      form
        .querySelectorAll(".my-trash-selected-value")
        .forEach((entry) => entry.remove());
      selected.forEach((entry) => {
        for (const [name, value] of [
          ["sde_id", entry.dataset.sdeId],
          ["trashed_at", entry.dataset.trashedAt],
        ]) {
          const input = document.createElement("input");
          input.type = "hidden";
          input.name = name;
          input.value = value;
          input.className = "my-trash-selected-value";
          form.append(input);
        }
      });
      button.disabled = selected.length === 0;
      all.checked = selected.length === entries.length && entries.length > 0;
      all.indeterminate = false;
      form.dataset.confirm = `選択した ${selected.length} 件を完全に消します。よろしいですか?`;
    };

    entries.forEach((entry) => entry.addEventListener("change", update));
    all.addEventListener("change", () => {
      entries.forEach((entry) => {
        entry.checked = all.checked;
      });
      update();
    });
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
    update();
  });
})();
