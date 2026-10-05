import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = path.join(rootDir, "dist");

async function listFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const absolute = path.join(directory, entry.name);
    return entry.isDirectory() ? listFiles(absolute) : [absolute];
  }));
  return nested.flat();
}

await access(outputDir);
const htmlFiles = (await listFiles(outputDir)).filter((file) => file.endsWith(".html"));
const errors = [];
const routes = new Set(htmlFiles.map((file) => {
  const relative = path.relative(outputDir, file).split(path.sep).join("/");
  return "/" + relative.replace(/index\.html$/, "");
}));

for (const file of htmlFiles) {
  const html = await readFile(file, "utf8");
  const relative = path.relative(outputDir, file);
  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/)?.[1] || '';
  const photos = Array.from(main.matchAll(/<img\b[^>]*src="([^"]+)"/g), match => match[1].split(/[?#]/)[0]);
  if (new Set(photos).size !== photos.length) errors.push(`${relative}: repeated content image`);

  const required = ["<html lang=", "<title>", "rel=\"canonical\"", "hreflang=\"en\"", "hreflang=\"es\"", "<header", "<footer"];
  for (const token of required) if (!html.includes(token)) errors.push(`${relative}: missing ${token}`);
  if (/{{ETA_[A-Z_]+}}/.test(html)) errors.push(`${relative}: unresolved template token`);
  if (/wa\.me\/\d/.test(html)) errors.push(`${relative}: hard-coded WhatsApp number`);
  if (!html.includes("data-page-id=")) errors.push(`${relative}: missing analytics page context`);
  const internalLinks = Array.from(html.matchAll(/href="(\/[^"?#]*)(?:[?#][^"]*)?"/g), (match) => match[1]);
  for (const link of internalLinks) {
    if (link.startsWith("/assets/") || /\.[a-z0-9]{2,12}$/i.test(link)) continue;
    const normalized = link.endsWith("/") ? link : link + "/";
    if (!routes.has(normalized)) errors.push(`${relative}: broken internal route ${link}`);
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`Validated ${htmlFiles.length} compiled HTML pages.`);
}
