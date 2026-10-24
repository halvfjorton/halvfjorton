import { chromium } from "playwright";
import { createServer } from "http";
import { readFile } from "fs/promises";
import { join, extname } from "path";
import { fileURLToPath } from "url";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "application/javascript",
  ".webp": "image/webp",
  ".jpg": "image/jpeg",
  ".woff2": "font/woff2",
  ".ico": "image/x-icon",
  ".svg": "image/svg+xml",
  ".json": "application/json",
  ".webmanifest": "application/manifest+json",
};

function serveDir(root) {
  return createServer(async (req, res) => {
    try {
      let path = decodeURIComponent(req.url.split("?")[0]);
      if (path === "/") path = "/index.html";
      if (path.endsWith("/")) path = `${path}index.html`;
      const filePath = join(root, path);
      const data = await readFile(filePath);
      res.writeHead(200, { "Content-Type": MIME[extname(filePath)] || "application/octet-stream" });
      res.end(data);
    } catch {
      res.writeHead(404);
      res.end("Not found");
    }
  });
}

const root = fileURLToPath(new URL("..", import.meta.url));
const outDir = join(root, "docs", "mobile-image-verify");
const server = serveDir(root);
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;
const base = `http://127.0.0.1:${port}`;

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
});
const page = await context.newPage();

await page.goto(`${base}/konserter/`, { waitUntil: "networkidle" });
const card = page.locator(".event-ticket").first();
await card.screenshot({ path: join(outDir, "konserter-card-390-dpr3.png") });

await page.goto(`${base}/julkonsert/`, { waitUntil: "networkidle" });
await page.locator(".event-ticket").first().screenshot({
  path: join(outDir, "julkonsert-page-390-dpr3.png"),
});

await browser.close();
server.close();
console.log("Wrote konserter card and julkonsert page screenshots");
