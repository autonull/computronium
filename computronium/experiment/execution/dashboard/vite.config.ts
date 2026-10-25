import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  root: ".",
  base: "/static/js/",
  build: {
    outDir: "./templates/static/js",
    emptyOutDir: true,
    sourcemap: true,
    minify: "esbuild",
    rollupOptions: {
      input: "src/main.ts",
      output: {
        entryFileNames: "dashboard.js",
        chunkFileNames: "[name].js",
        assetFileNames: "[name].[ext]",
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:8080",
      "/ws": {
        target: "ws://localhost:8080",
        ws: true,
      },
    },
  },
  css: {
    postcss: {},
  },
});