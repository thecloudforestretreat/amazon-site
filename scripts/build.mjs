import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const sourceDir = path.join(rootDir, "src");
const outputDir = path.join(rootDir, "dist");
const environment = process.env.ETA_ENV === "production" ? "production" : "staging";

const coreCssFiles = [
  "tokens.css",
  "base.css",
  "layout.css",
  "components.css",
  "header.css",
  "footer.css"
];

async function listFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const absolute = path.join(directory, entry.name);
    return entry.isDirectory() ? listFiles(absolute) : [absolute];
  }));
  return nested.flat();
}

async function copyIfPresent(from, to) {
  try {
    await cp(from, to, { recursive: true });
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
}

async function compilePages() {
  const pagesDir = path.join(sourceDir, "pages");
  const pages = (await listFiles(pagesDir)).filter((file) => file.endsWith(".html"));
  const includes = {
    en: {
      header: await readFile(path.join(sourceDir, "includes", "header.en.html"), "utf8"),
      footer: await readFile(path.join(sourceDir, "includes", "footer.en.html"), "utf8")
    },
    es: {
      header: await readFile(path.join(sourceDir, "includes", "header.es.html"), "utf8"),
      footer: await readFile(path.join(sourceDir, "includes", "footer.es.html"), "utf8")
    }
  };
  const commonHead = await readFile(path.join(sourceDir, "includes", "head.html"), "utf8");

  for (const page of pages) {
    const relative = path.relative(pagesDir, page);
    const language = relative.split(path.sep)[0] === "es" ? "es" : "en";
    const outputRelative = language === "es" ? relative : relative.replace(/^en\//, "");
    const destination = path.join(outputDir, outputRelative);
    let html = await readFile(page, "utf8");
    html = html
      .replaceAll("{{ETA_HEAD}}", commonHead.trim())
      .replaceAll("{{ETA_HEADER}}", includes[language].header.trim())
      .replaceAll("{{ETA_FOOTER}}", includes[language].footer.trim())
      .replaceAll("{{ETA_ENVIRONMENT}}", environment);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, html);
  }
}

async function buildCss() {
  const cssDir = path.join(sourceDir, "assets", "css");
  const coreCss = await Promise.all(coreCssFiles.map((file) => readFile(path.join(cssDir, file), "utf8")));
  const outputCssDir = path.join(outputDir, "assets", "css");
  await mkdir(outputCssDir, { recursive: true });
  await writeFile(outputCssDir + "/core.css", coreCss.join("\n\n"));
  await copyIfPresent(path.join(cssDir, "clusters"), path.join(outputCssDir, "clusters"));
}

async function writeEnvironmentFiles() {
  const isStaging = environment === "staging";
  const headers = isStaging
    ? "/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Content-Type-Options: nosniff\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
    : "/*\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Content-Type-Options: nosniff\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n";
  const robots = isStaging
    ? "User-agent: *\nDisallow: /\n"
    : "User-agent: *\nAllow: /\n\nSitemap: https://experiencetheamazon.com/sitemap.xml\n";
  await writeFile(path.join(outputDir, "_headers"), headers);
  await writeFile(path.join(outputDir, "robots.txt"), robots);
}

async function writeRuntimeConfig() {
  const configPath = path.join(outputDir, "assets", "js", "site-config.js");
  const config = (await readFile(configPath, "utf8")).replaceAll("{{ETA_ENVIRONMENT}}", environment);
  await writeFile(configPath, config);
}

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });
await copyIfPresent(path.join(rootDir, "assets", "logo"), path.join(outputDir, "assets", "logo"));
await copyIfPresent(path.join(sourceDir, "assets", "js"), path.join(outputDir, "assets", "js"));
await copyIfPresent(path.join(sourceDir, "assets", "icons"), path.join(outputDir, "assets", "icons"));
for (const file of ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png", "apple-touch-icon.png", "android-chrome-192x192.png", "android-chrome-512x512.png", "site.webmanifest"]) {
  await copyIfPresent(path.join(rootDir, file), path.join(outputDir, file));
}
await buildCss();
await compilePages();
await writeRuntimeConfig();
await writeEnvironmentFiles();
console.log(`Built ${environment} site in ${outputDir}`);
