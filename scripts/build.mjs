import { createHash } from "node:crypto";
import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const sourceDir = path.join(rootDir, "src");
const ecuadorRelease = process.env.ETA_SCOPE === "ecuador";
const peruRelease = process.env.ETA_SCOPE === "ecuador-peru";
const boliviaRelease = process.env.ETA_SCOPE === "ecuador-peru-bolivia";
const outputDir = path.resolve(rootDir, process.env.ETA_OUTPUT || (ecuadorRelease ? "dist-ecuador" : peruRelease ? "dist-release" : boliviaRelease ? "dist-bolivia-release" : "dist"));
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
      footer: await readFile(path.join(sourceDir, "includes", "footer.en.html"), "utf8"),
      ecuadorNav: await readFile(path.join(sourceDir, "includes", "ecuador-nav.en.html"), "utf8")
    },
    es: {
      header: await readFile(path.join(sourceDir, "includes", "header.es.html"), "utf8"),
      footer: await readFile(path.join(sourceDir, "includes", "footer.es.html"), "utf8"),
      ecuadorNav: await readFile(path.join(sourceDir, "includes", "ecuador-nav.es.html"), "utf8")
    }
  };
  const commonHead = await readFile(path.join(sourceDir, "includes", "head.html"), "utf8");

  for (const page of pages) {
    const relative = path.relative(pagesDir, page);
    if (ecuadorRelease && /^(?:en|es)\/(?:peru|bolivia)\//.test(relative)) continue;
    if (peruRelease && /^(?:en|es)\/bolivia\//.test(relative)) continue;
    if ((ecuadorRelease || peruRelease || boliviaRelease) && /^(?:en|es)\/brazil\//.test(relative)) continue;
    const language = relative.split(path.sep)[0] === "es" ? "es" : "en";
    const outputRelative = language === "es" ? relative : relative.replace(/^en\//, "");
    const destination = path.join(outputDir, outputRelative);
    let html = await readFile(page, "utf8");
    html = html
      .replaceAll("{{ETA_HEAD}}", commonHead.trim())
      .replaceAll("{{ETA_HEADER}}", includes[language].header.trim())
      .replaceAll("{{ETA_FOOTER}}", includes[language].footer.trim())
      .replaceAll("{{ETA_ECUADOR_NAV}}", includes[language].ecuadorNav.trim())
      .replaceAll("{{ETA_ENVIRONMENT}}", environment);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, html);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function compileEcuadorDestinations() {
  const destinations = JSON.parse(await readFile(path.join(sourceDir, "data", "ecuador-destinations.json"), "utf8"));
  const commonHead = (await readFile(path.join(sourceDir, "includes", "head.html"), "utf8")).trim();
  const shared = {
    en: {
      header: (await readFile(path.join(sourceDir, "includes", "header.en.html"), "utf8")).trim(),
      footer: (await readFile(path.join(sourceDir, "includes", "footer.en.html"), "utf8")).trim(),
      nav: (await readFile(path.join(sourceDir, "includes", "ecuador-nav.en.html"), "utf8")).trim()
    },
    es: {
      header: (await readFile(path.join(sourceDir, "includes", "header.es.html"), "utf8")).trim(),
      footer: (await readFile(path.join(sourceDir, "includes", "footer.es.html"), "utf8")).trim(),
      nav: (await readFile(path.join(sourceDir, "includes", "ecuador-nav.es.html"), "utf8")).trim()
    }
  };

  for (const destination of destinations) {
    for (const language of ["en", "es"]) {
      const content = destination[language];
      const prefix = language === "es" ? "/es" : "";
      const route = `${prefix}/ecuador/${destination.slug}/`;
      const alternateRoute = `${language === "en" ? "/es" : ""}/ecuador/${destination.slug}/`;
      const homeRoute = language === "es" ? "/es/" : "/";
      const labels = language === "es"
        ? { home: "Inicio", country: "Amazonía del Ecuador", answer: "Respuesta rápida", why: "Por qué elegirlo", expect: "Qué esperar", plan: "Cómo planificar", related: "Compara otros destinos", cta: "Planifica este viaje", question: "Preguntas frecuentes", back: "Ver guía de Ecuador" }
        : { home: "Home", country: "Ecuadorian Amazon", answer: "Quick answer", why: "Why choose it", expect: "What to expect", plan: "How to plan", related: "Compare other destinations", cta: "Plan this trip", question: "Frequently asked questions", back: "View Ecuador guide" };
      const faqSchema = content.faqs.map(([question, answer]) => ({ "@type": "Question", name: question, acceptedAnswer: { "@type": "Answer", text: answer } }));
      const schema = JSON.stringify({
        "@context": "https://schema.org",
        "@graph": [
          { "@type": "TouristDestination", name: content.name, description: content.description, containedInPlace: { "@type": "Country", name: "Ecuador" }, url: `https://experiencetheamazon.com${route}` },
          { "@type": "BreadcrumbList", itemListElement: [
            { "@type": "ListItem", position: 1, name: labels.home, item: `https://experiencetheamazon.com${homeRoute}` },
            { "@type": "ListItem", position: 2, name: labels.country, item: `https://experiencetheamazon.com${prefix}/ecuador/` },
            { "@type": "ListItem", position: 3, name: content.name, item: `https://experiencetheamazon.com${route}` }
          ] },
          { "@type": "FAQPage", mainEntity: faqSchema }
        ]
      });
      const related = destinations.filter((item) => item.slug !== destination.slug).map((item) => `<a href="${prefix}/ecuador/${item.slug}/"><span>${escapeHtml(item[language].name)}</span></a>`).join("");
      const faqs = content.faqs.map(([question, answer]) => `<details><summary>${escapeHtml(question)}</summary><p>${escapeHtml(answer)}</p></details>`).join("");
      const defaultGuideLabels = language === 'es'
        ? ['El paisaje', '¿Es para ti?', 'El viaje hasta aquí', 'Cuántos días', 'Fauna y actividades', 'Agua y temporadas', 'Tu lodge y tu guía', 'Qué llevar', 'Viajar con respeto', 'Compara destinos']
        : ['The landscape', 'Is it your kind of trip?', 'The journey here', 'How long to stay', 'Wildlife and activities', 'Water and seasons', 'Your lodge and guide', 'What to bring', 'Travel with respect', 'Compare destinations'];
      const guideLabels = content.sections?.map((section, index) => section.display?.nav || defaultGuideLabels[index] || section.heading) || defaultGuideLabels;
      const tripOptions = content.tripOptions || (language === 'es' ? [
        ['3 días', 'Una introducción breve', 'Los traslados pueden dejar solo un día completo de actividades. Compara los horarios de llegada y salida antes de reservar.'],
        ['4 días', 'Más tiempo para explorar', 'Un día adicional puede dar espacio para más salidas, si el itinerario incluye tiempo completo en la selva.'],
        ['5 días', 'Un ritmo más tranquilo', 'Más oportunidades para repetir salidas y ajustar planes al clima. Más tiempo no garantiza avistamientos.']
      ] : [
        ['3 days', 'A short introduction', 'Transfers may leave just one full activity day. Compare arrival and departure times before booking.'],
        ['4 days', 'More room to explore', 'An additional day can create space for more outings, if the itinerary includes full time in the forest.'],
        ['5 days', 'A less rushed rhythm', 'More opportunities for repeated outings and weather adjustments. Extra time does not guarantee sightings.']
      ]);
      const guideSections = (content.sections || []).map((section, index) => {
        const sentences = section.paragraphs.map(p => p.split(/(?<=[.!?])\s+/));
        const intro = section.display?.intro || sentences[0].slice(0, 2).join(' ');
        const points = section.display?.points || [sentences[0].slice(2, 4).join(' '), ...sentences[1].slice(0, 3)].filter(Boolean);
        const featured = [0, 3, 4, 9].includes(index);
        const scene = destination.sectionImages?.find(image => image.section === index) || (index === 0 ? destination.sectionImage : null);
        const photo = scene ? `<figure class="eta-guide-photo"><img src="${escapeHtml(scene.src)}" width="${scene.width}" height="${scene.height}" alt="${escapeHtml(language === 'es' ? scene.altEs : scene.altEn)}" loading="lazy" decoding="async"><figcaption>${scene.ownerSupplied ? escapeHtml(language === "es" ? scene.altEs : scene.altEn) : `${language === 'es' ? 'Foto' : 'Photo'}: <a href="${escapeHtml(scene.source)}">${escapeHtml(scene.credit)}</a>${scene.licenseUrl ? ` · <a href="${escapeHtml(scene.licenseUrl)}">${escapeHtml(scene.license)}</a> · ${language === "es" ? "Adaptada" : "Edited"}` : ""}`}</figcaption></figure>` : '';
        const trips = index === 3 ? `<div class="eta-trip-options">${tripOptions.map(([days, title, text]) => `<div class="eta-trip-option"><p class="eta-trip-days">${days}</p><h3>${title}</h3><p>${text}</p></div>`).join('')}</div>` : '';
        const comparison = index === 9 ? `<div class="eta-link-list">${related}</div>` : '';
        return `<article class="eta-destination-section${featured ? ' eta-guide-feature' : ''}${photo ? ' eta-guide-landscape' : ''}${photo && index === 4 ? ' eta-guide-landscape--reverse' : ''}${index === 4 ? ' eta-guide-wildlife' : ''}" id="section-${index + 1}">${photo}<div class="eta-guide-copy"><span class="eta-guide-number" aria-hidden="true">${String(index + 1).padStart(2, '0')}</span><h2>${escapeHtml(section.display?.heading || guideLabels[index] || section.heading)}</h2><p class="eta-guide-preview">${escapeHtml(intro)}</p>${trips || `<ul class="eta-guide-points">${points.map(point => `<li>${escapeHtml(point)}</li>`).join('')}</ul>`}${comparison}</div></article>`;
      }).join('');
      const guideLinks = (content.sections || []).map((section, index) => `<a href="#section-${index + 1}">${escapeHtml(guideLabels[index] || section.heading)}</a>`).join('');
      const sections = content.sections ? `<section class="eta-section eta-destination-guide-section"><div class="eta-shell eta-destination-guide"><aside class="eta-destination-toc"><h2>${language === 'es' ? 'En esta guía' : 'In this guide'}</h2><nav aria-label="${language === 'es' ? 'Secciones de la guía' : 'Guide sections'}">${guideLinks}</nav></aside><div class="eta-destination-body">${guideSections}</div></div></section>` : '';
      const sources = (destination.sources || []).map(source => `<li><a href="${escapeHtml(source.url)}" rel="noopener">${escapeHtml(source.title)}</a></li>`).join('');
      const review = destination.reviewedAt ? `<section class="eta-section--tight"><div class="eta-shell eta-reading"><h2>${language === 'es' ? 'Fuentes y criterios editoriales' : 'Sources and editorial approach'}</h2><p>${language === 'es' ? 'Revisión editorial' : 'Editorial review'}: <time datetime="${destination.reviewedAt}">${destination.reviewedAt}</time>.</p><ul>${sources}</ul><p>${language === 'es' ? 'Las fuentes oficiales describen el destino; las comparaciones de duración y las preguntas para lodges son criterios editoriales. Las fuentes aportan contexto del destino y no verifican servicios ni condiciones actuales. Confirma horarios y acceso con tu operador. Esta guía no representa una visita de primera mano ni una recomendación de un lodge concreto.' : 'Official sources describe the destination; trip-length comparisons and lodge questions are editorial guidance. Source material provides destination context and does not verify current services or conditions. Confirm schedules and access with your operator. This guide is not a first-hand visit report or an endorsement of a particular lodge.'}</p></div></section>` : '';
      const lodgeRoute = language === 'es' ? '/es/ecuador/lodges-en-la-amazonia/' : '/ecuador/amazon-lodges/';
      const heroVisual = destination.image
        ? `<figure class="eta-country-art eta-country-art--licensed"><img src="${escapeHtml(destination.image)}"${destination.imageWidth ? ` width="${destination.imageWidth}" height="${destination.imageHeight}"` : ''} alt="${escapeHtml(language === "es" ? destination.imageAltEs : destination.imageAltEn)}" decoding="async" fetchpriority="high"><figcaption class="eta-photo-credit">${destination.imageOwnerSupplied ? escapeHtml(language === "es" ? destination.imageAltEs : destination.imageAltEn) : `${language === "es" ? "Foto" : "Photo"}: <a href="${escapeHtml(destination.imageSource || "https://unsplash.com")}" rel="noopener">${escapeHtml((destination.imageCredit || "").replace(/^Photo: /, ""))}</a>${destination.imageLicense ? ` · <a href="${destination.imageLicense}">${escapeHtml(destination.imageLicenseLabel || "CC BY 2.0")}</a> · ${language === "es" ? "Adaptada" : "Edited"}` : ''}`}</figcaption></figure>`
        : `<div class="eta-country-art" role="img" aria-label="${language === "es" ? "Espacio reservado para una imagen autorizada de" : "Reserved for a rights-cleared image of"} ${escapeHtml(content.name)}"></div>`;
      const html = `<!doctype html>
<html lang="${language}" data-language-pair="${alternateRoute}" data-page-id="ecuador_${destination.slug}_${language}" data-pair-id="${destination.pairId}" data-page-type="destination_page" data-country="ecuador" data-destination="${destination.slug}" data-topic-cluster="ecuador-destinations" data-funnel-stage="consideration">
<head><meta charset="utf-8"><title>${escapeHtml(content.title)}</title><meta name="description" content="${escapeHtml(content.description)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="https://experiencetheamazon.com${route}"><link rel="alternate" hreflang="en" href="https://experiencetheamazon.com/ecuador/${destination.slug}/"><link rel="alternate" hreflang="es" href="https://experiencetheamazon.com/es/ecuador/${destination.slug}/"><link rel="alternate" hreflang="x-default" href="https://experiencetheamazon.com/ecuador/${destination.slug}/">${commonHead}<link rel="stylesheet" href="/assets/css/clusters/country.css"><link rel="stylesheet" href="/assets/css/clusters/destination.css"><script type="application/ld+json">${schema}</script></head>
<body class="eta-destination-page">${shared[language].header}${shared[language].nav}<main id="main-content">
<div class="eta-shell eta-breadcrumbs"><a href="${homeRoute}">${labels.home}</a><span>›</span><a href="${prefix}/ecuador/">${labels.country}</a><span>›</span><span>${escapeHtml(content.name)}</span></div>
<section class="eta-country-hero"><div class="eta-shell eta-country-hero__grid"><div><p class="eta-kicker">${labels.country}</p><h1>${escapeHtml(content.h1)}</h1><p class="eta-lede">${escapeHtml(content.lede)}</p><div class="eta-actions"><a class="eta-button eta-button--gold" href="${language === "es" ? "/es/contacto/" : "/contact/"}" data-cta-id="destination_plan" data-cta-position="hero" data-module-id="destination-hero">${labels.cta}</a><a class="eta-quiet-link" href="#guide">${language === "es" ? "Explora la guía" : "Explore the guide"}</a></div></div>${heroVisual}</div></section>
<section class="eta-section--tight"><div class="eta-shell"><div class="eta-facts"><div class="eta-fact"><strong>${escapeHtml(content.fit)}</strong><span>${language === "es" ? "Perfil ideal" : "Best fit"}</span></div><div class="eta-fact"><strong>${escapeHtml(content.access)}</strong><span>${language === "es" ? "Acceso" : "Access"}</span></div><div class="eta-fact"><strong>${escapeHtml(content.pace)}</strong><span>${language === "es" ? "Ritmo sugerido" : "Suggested pace"}</span></div><div class="eta-fact"><strong>${language === "es" ? "Guía local" : "Local guide"}</strong><span>${language === "es" ? "Parte esencial del viaje" : "Essential to the experience"}</span></div></div></div></section>
<section class="eta-section${content.sections ? ' eta-destination-summary' : ''}" id="guide"><div class="eta-shell"><div class="eta-answer"><span class="eta-answer__label">${labels.answer}</span><h2>${language === "es" ? `¿Para quién funciona ${escapeHtml(content.name)}?` : `Who is ${escapeHtml(content.name)} best for?`}</h2><p>${escapeHtml(content.sections ? content.quick.split(/(?<=[.!?])\s+/).slice(0, 2).join(' ') : content.quick)}</p></div>${content.sections ? '' : `<div class="eta-decision-grid" style="margin-top:40px"><article class="eta-decision-card"><h2>${labels.why}</h2><p>${escapeHtml(content.why)}</p></article><article class="eta-decision-card"><h2>${labels.expect}</h2><p>${escapeHtml(content.expect)}</p></article><article class="eta-decision-card"><h2>${labels.plan}</h2><p>${escapeHtml(content.plan)}</p></article><article class="eta-decision-card"><h2>${labels.related}</h2><div class="eta-link-list">${related}</div></article></div>`}</div></section>
${sections}
<section class="eta-section eta-section--mist"><div class="eta-shell eta-reading"><p class="eta-kicker">${labels.question}</p><h2>${content.name}</h2><div class="eta-stack">${faqs}</div></div></section>
${review}
<section class="eta-section"><div class="eta-shell eta-trust-strip"><p class="eta-kicker">${language === "es" ? "Vive la Amazonía con confianza" : "Experience the Amazon with confidence"}</p><h2>${language === "es" ? `¿Es ${escapeHtml(content.name)} el destino correcto?` : `Is ${escapeHtml(content.name)} right for your trip?`}</h2><p>${language === "es" ? "Comparte tus fechas, el tamaño del grupo y tus prioridades. Compara el destino y después confirma el guía, el lodge y los traslados." : "Share your dates, group size and priorities. Start by comparing the destination, then confirm the guide, lodge and transfers for your trip."}</p><div class="eta-actions"><a class="eta-button eta-button--gold" href="${language === "es" ? "/es/contacto/" : "/contact/"}" data-cta-id="destination_inquiry" data-cta-position="footer" data-module-id="destination-next-step">${labels.cta}</a><a class="eta-quiet-link" href="${lodgeRoute}">${language === "es" ? "Compara lodges" : "Compare lodges"}</a></div><div class="eta-link-list">${related}</div></div></section>
</main>${shared[language].footer}</body></html>`;
      const destinationFile = path.join(outputDir, language === "es" ? "es" : "", "ecuador", destination.slug, "index.html");
      await mkdir(path.dirname(destinationFile), { recursive: true });
      await writeFile(destinationFile, html.replaceAll("{{ETA_ENVIRONMENT}}", environment));
    }
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
await copyIfPresent(path.join(sourceDir, "assets", "images"), path.join(outputDir, "assets", "images"));
await copyIfPresent(path.join(sourceDir, "_redirects"), path.join(outputDir, "_redirects"));
for (const file of ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png", "apple-touch-icon.png", "android-chrome-192x192.png", "android-chrome-512x512.png", "site.webmanifest"]) {
  await copyIfPresent(path.join(rootDir, file), path.join(outputDir, file));
}
await buildCss();
await compilePages();
await compileEcuadorDestinations();
await writeRuntimeConfig();
await writeEnvironmentFiles();
if (ecuadorRelease || peruRelease || boliviaRelease) {
  const files = (await listFiles(outputDir)).filter(file => file.endsWith(".html"));
  const indexable = [];
  for (const file of files) {
    const html = await readFile(file, "utf8");
    if (/<meta name="robots" content="[^"]*noindex/.test(html)) continue;
    const url = html.match(/<link rel="canonical" href="([^"]+)"/)?.[1];
    if (url) indexable.push(url);
  }
  await writeFile(path.join(outputDir,"sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+indexable.map(url => '<url><loc>'+escapeHtml(url)+'</loc></url>').join('\n')+'\n</urlset>\n');
}

// Version local stylesheets and scripts by content so refreshed pages fetch changes.
const cssVersions = new Map();
for (const cssFile of (await listFiles(path.join(outputDir, 'assets'))).filter(file => /\.(css|js)$/.test(file))) {
  const url = '/' + path.relative(outputDir, cssFile).split(path.sep).join('/');
  cssVersions.set(url, createHash('sha256').update(await readFile(cssFile)).digest('hex').slice(0, 12));
}
for (const htmlFile of (await listFiles(outputDir)).filter(file => file.endsWith('.html'))) {
  let html = await readFile(htmlFile, 'utf8');
  html = html.replace(/<main\b([^>]*)>/g, (tag, attrs) => /tabindex=/.test(attrs) ? tag : '<main'+attrs+' tabindex="-1">');
  await writeFile(htmlFile, html.replace(/(href|src)="(\/assets\/(?:css|js)\/[^"?]+\.(?:css|js))"/g, (match, attribute, url) => `${attribute}="${url}?v=${cssVersions.get(url)}"`));
}

if (environment === "staging") {
  for (const file of (await listFiles(outputDir)).filter(file => file.endsWith(".html"))) {
    const html = await readFile(file, "utf8");
    await writeFile(file, html.replace(/<meta name="robots" content="[^"]*">/g, '<meta name="robots" content="noindex,nofollow,noarchive">'));
  }
}

console.log(`Built ${environment} site in ${outputDir}`);
