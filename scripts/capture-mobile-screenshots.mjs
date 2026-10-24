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
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
  ".ico": "image/x-icon",
  ".txt": "text/plain",
  ".xml": "application/xml",
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

async function capture(root, label, outDir, pages) {
  const server = serveDir(root);
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port;
  const base = `http://127.0.0.1:${port}`;

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  const page = await context.newPage();

  const imageReport = [];

  for (const { path, name } of pages) {
    await page.goto(`${base}${path}`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      const delay = (ms) => new Promise((r) => setTimeout(r, ms));
      for (let y = 0; y < document.body.scrollHeight; y += 400) {
        window.scrollTo(0, y);
        await delay(80);
      }
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(600);
    await page.screenshot({
      path: join(outDir, `${label}-${name}-390-dpr3.png`),
      fullPage: true,
    });

    const imgs = await page.evaluate(() =>
      [...document.querySelectorAll("img")].map((img) => ({
        alt: img.alt.slice(0, 60),
        currentSrc: img.currentSrc,
        src: img.getAttribute("src"),
        srcset: img.srcset,
        sizes: img.sizes,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        clientWidth: img.clientWidth,
        clientHeight: img.clientHeight,
      }))
    );
    imageReport.push({ page: path, images: imgs });
  }

  await browser.close();
  server.close();
  return imageReport;
}

const root = fileURLToPath(new URL("..", import.meta.url));
const outDir = join(root, "docs", "mobile-image-verify");
const pages = [{ path: "/", name: "hem" }, { path: "/foretag/", name: "foretag" }];

const beforeRoot = process.argv[2];
const afterRoot = process.argv[3] || root;

await import("fs/promises").then((fs) => fs.mkdir(outDir, { recursive: true }));

const beforeReport = await capture(beforeRoot, "before", outDir, pages);
const afterReport = await capture(afterRoot, "after", outDir, pages);

const report = {
  viewport: { width: 390, height: 844, deviceScaleFactor: 3 },
  before: beforeReport,
  after: afterReport,
};
await import("fs/promises").then((fs) =>
  fs.writeFile(join(outDir, "image-candidates.json"), JSON.stringify(report, null, 2))
);
console.log("Wrote screenshots and", join(outDir, "image-candidates.json"));
