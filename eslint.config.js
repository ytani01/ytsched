import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    files: ["src/ytsched/webroot/static/js/**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: { ...globals.browser },
    },
    rules: {
      // グローバル関数や ytState をファイルをまたいで共有しているのが
      // 今の構成。TODO-097 で /* global */ /* exported */ を入れたあと、
      // 別項目でこの 2 つを有効化する。
      "no-undef": "off",
      "no-unused-vars": "off",
    },
  },
];
