// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "reactpy_jupyter/static",
    lib: {
      entry: ["src/index.js"],
      formats: ["es"],
    },
  },
});
