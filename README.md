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
