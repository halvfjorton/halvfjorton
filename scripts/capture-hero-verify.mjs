import { chromium } from "playwright";
import { createServer } from "http";
import { readFile, mkdir, writeFile } from "fs/promises";
import { join, extname } from "path";
import { fileURLToPath } from "url";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "application/javascript",
  ".webp": "image/webp",
  ".jpg": "image/jpeg",
  ".woff2": "font/woff2",
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

const PAGES = [
  { path: "/", label: "home", selector: ".alt-hero__slide:first-child img" },
  { path: "/brollop/", label: "brollop", selector: ".alt-service-hero__img" },
  { path: "/foretag/", label: "foretag", selector: ".alt-service-hero__img" },
  { path: "/fest-och-mingel/", label: "mingel", selector: ".alt-service-hero__img" },
];

async function auditRoot(root, label) {
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
  const heroes = [];
  for (const { path, label: pageLabel, selector } of PAGES) {
    await page.goto(`${base}${path}`, { waitUntil: "networkidle" });
    const img = page.locator(selector).first();
    const data = await img.evaluate((el) => ({
      currentSrc: el.currentSrc,
      naturalWidth: el.naturalWidth,
      naturalHeight: el.naturalHeight,
      sizes: el.sizes,
      srcset: el.srcset,
    }));
    heroes.push({ page: pageLabel, ...data });
    if (pageLabel === "home") {
      const box = await img.boundingBox();
      if (box) {
        await page.screenshot({
          path: join(outDir, `${label}-home-hero-crop-390-dpr3.png`),
          clip: { x: 0, y: 0, width: 390, height: Math.min(520, 844) },
        });
      }
    }
  }
  await browser.close();
  server.close();
  return heroes;
}

const root = fileURLToPath(new URL("..", import.meta.url));
const outDir = join(root, "docs", "hero-dpr-verify");
const beforeRoot = process.argv[2];
const afterRoot = process.argv[3] || root;
await mkdir(outDir, { recursive: true });

const report = {
  viewport: { width: 390, height: 844, deviceScaleFactor: 3 },
  before: await auditRoot(beforeRoot, "before"),
  after: await auditRoot(afterRoot, "after"),
};
await writeFile(join(outDir, "hero-candidates.json"), JSON.stringify(report, null, 2));
console.log("Wrote", join(outDir, "hero-candidates.json"));
