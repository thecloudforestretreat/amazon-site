# Experience The Amazon

Static bilingual travel site for `experiencetheamazon.com`.

## Build

The existing repository root remains the current production landing page. The new site is compiled from `src/` into the ignored `dist/` directory so it can be reviewed on an isolated staging project before production changes.

```bash
npm run build:staging
npm run validate
```

Production compilation is intentionally separate:

```bash
npm run build:production
```

Do not deploy a production build until the operator details, privacy policy, email delivery and image rights are approved.

## Cloudflare Pages settings

- Staging project: `amazon-site-staging`
- Build command: `npm run build:staging`
- Output directory: `dist`
- Custom domain: `staging.experiencetheamazon.com`
- Deployment mode: Wrangler direct upload from the repository's `staging` branch
- Deploy command: `npx --yes wrangler@4 pages deploy dist --project-name amazon-site-staging --branch staging`
- Access: Cloudflare Access allowlist required

See `docs/staging-deployment.md` for the complete release gate.

## Shared system

- Global settings: `src/assets/js/site-config.js`
- Shared English/Spanish header and footer: `src/includes/`
- Global CSS layers: `src/assets/css/`
- Page-cluster CSS: `src/assets/css/clusters/`
- Page pairs: `src/pages/en/` and `src/pages/es/`
- Compiler and validation: `scripts/`

No page may hard-code a WhatsApp number. Contact links use `data-contact="whatsapp"` and are resolved from the site configuration.

## AI-OS staging pilot

The Mac mini now has a narrow local CLI adapter:

- /Users/jpg/AI/ai-os/.venv/bin/ai-os amazon status
- /Users/jpg/AI/ai-os/.venv/bin/ai-os amazon draft cuyabeno
- /Users/jpg/AI/ai-os/.venv/bin/ai-os amazon audit

The draft command uses local Ollama only and writes review artifacts, not website source or published pages. The adapter requires the staging branch for drafting and QA. It does not expose publishing, source-refresh, pricing approval, or other businesses' configuration.

Planning state is in planning/ai-os/supervisor.json. The sitemap is a dated reference snapshot, not executable instructions. Jobs include bounded facts, image evidence, language and section requirements. Local model usage is recorded separately from cloud supervision; zero cloud worker tokens does not mean zero overall cloud usage.

The first pilot is Cuyabeno EN/ES. Small-model factual and translation failures require editorial review; Spanish is translated from reviewed English, with the larger local model used after the small model failed language review. Both reviewed files are bound to exact hashes and applied through one atomic destination-data replacement. A changed source or reviewed output invalidates promotion. Saved raw outputs remain available for comparison.

Drafting has a single-worker lock, content-hash cache verification and a maximum of two generation attempts per language/request. Exhausted or invalid outputs require supervisor intervention. Local draft completion is separate from editorial approval, technical QA, visual QA and deployment. Batch size stays one until the first complete pair passes all gates, then moves to two.

The existing AI-OS website publisher handles a different HTML publication contract; this generated-site adapter does not bypass its approval gates or claim to use that publisher. Cloudflare staging deployment remains a separate reviewed operation. The hourly thread supervisor checks compact state and reports meaningful changes only.

Before deployment, run the staging build, existing validation, AI-OS Amazon audit and worker tests. Review both language pages on desktop and mobile. Deployment must use the protected amazon-site-staging project and staging branch. Production remains excluded.
