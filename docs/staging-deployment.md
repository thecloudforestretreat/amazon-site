# Staging deployment and release gate

## Cloudflare Pages

The separate Pages project is named `amazon-site-staging`. It is deployed by Wrangler direct upload from the repository's `staging` branch; it is not currently connected to Git for automatic builds.

- Build command: `npm run build:staging`
- Build output: `dist`
- Node version: 20 or later
- Custom domain: `staging.experiencetheamazon.com`
- Deploy command: `npx --yes wrangler@4 pages deploy dist --project-name amazon-site-staging --branch staging`

The staging build produces a blocking `robots.txt`, an `X-Robots-Tag: noindex, nofollow, noarchive` header and a visible staging badge. The production analytics configuration does not load Google Tag Manager on staging.

## Cloudflare Access

Protect the complete staging hostname with an Access application before sharing it. Use an email allowlist for the owner and explicitly approved reviewers. The DNS record and certificate should be managed through the Pages custom-domain workflow.

## Email and leads

Before form submission is enabled:

1. Create `info@experiencetheamazon.com` in Cloudflare Email Routing.
2. Select and verify the destination inbox.
3. Verify the sending domain and sender in Brevo.
4. Publish and verify SPF, DKIM and DMARC.
5. Create the Experience The Amazon lead list and fields.
6. Deploy a same-origin lead endpoint with Turnstile and server-side validation.
7. Put the endpoint in `src/assets/js/site-config.js`.
8. Test English and Spanish confirmations without sending personal data to analytics.

## Production release gate

- Legal operator identity and jurisdiction confirmed
- Privacy policy and terms approved
- Email delivery and reply path verified
- Lead retention and deletion process documented
- Every production image marked approved in the rights register
- English/Spanish page pairs validated
- Canonical and hreflang tests pass
- Staging crawl has no broken internal routes
- Mobile, keyboard and form testing completed
- GTM Preview and consent tests completed
- Production build reviewed before deployment
