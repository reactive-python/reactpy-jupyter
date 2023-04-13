// vite.config.js
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";

export default defineConfig({
  build: {
    outDir: "reactpy_jupyter/static",
    lib: {
      entry: ["src/index.js"],
      formats: ["es"],
    },
  },
  resolve: {
    alias: {
      react: "preact/compat",
      "react-dom": "preact/compat",
    },
  },
  plugins: [preact()],
});
