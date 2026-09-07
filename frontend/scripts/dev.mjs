import { build } from "esbuild";
import { spawn } from "node:child_process";
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const css = await readFile(path.join(root, "src/styles.css"), "utf8");
const result = await build({
  entryPoints: [path.join(root, "src/main.tsx")],
  bundle: true,
  write: false,
  format: "iife",
  platform: "browser",
  target: ["es2020"],
  define: { "process.env.NODE_ENV": '"development"' },
  sourcemap: "inline",
});
const js = result.outputFiles[0].text.replace(/<\/script/gi, "<\\/script");
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>TOLTI AIs · Shared workspace</title><style>${css}</style><script>window.__DEV__=true</script></head><body><div id="root"></div><script>${js}</script></body></html>`;
await writeFile(path.join(root, "dist", "index.html"), html);

const server = spawn("npx", ["serve", "dist", "-l", "5173"], {
  cwd: root,
  stdio: "inherit",
});

process.on("SIGINT", () => {
  server.kill("SIGINT");
  process.exit(0);
});
