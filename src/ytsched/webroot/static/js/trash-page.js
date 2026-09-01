/**
 *   (c) 2026 ytani01
 */

// trash.html だけで使う選択・確認のリスナー登録 (TODO-141)。

(() => {
  window.addEventListener("load", () => {
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
