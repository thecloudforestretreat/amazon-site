# Ecuador contact activation

Implemented: Pages Function `/api/contact`; bilingual general and Ecuador contact forms; managed Turnstile with server validation of success, staging hostname and `contact` action; bounded input, consent and honeypot validation; Brevo transactional email; disabled-on-missing-configuration UI. No form contents or secrets logged; no newsletter subscription or lead-list creation. API acknowledgement means queued, not inbox delivery.

Configure only `amazon-site-staging` preview environment (branch `staging`) in Cloudflare Pages:

- `TURNSTILE_SITE_KEY`: public key for a managed widget restricted to `staging.experiencetheamazon.com`.
- `TURNSTILE_SECRET_KEY`: secret binding.
- `BREVO_API_KEY`: secret binding for the owner's Brevo account.
- `CONTACT_FROM`: verified Brevo sender email.
- `CONTACT_TO`: owner-selected receiving inbox.
- `CONTACT_ENABLED`: `true` only when the above are valid and protected-staging testing is authorized.

Do not paste secrets into chat or commit them. Use Pages environment secrets and redeploy the staging branch after configuring. The endpoint rejects production and direct pages.dev hostnames. Production activation needs a separate reviewed configuration.

Eight mocked endpoint tests cover configuration failure, wrong origin/hostname/action, missing consent/token, invalid inputs/honeypot, delivery rejection, body limit, service outage and verified queued flow. Run `node --test scripts/test-contact.mjs`.

Still required: real Turnstile challenge and submission, Brevo acceptance, and owner-confirmed inbox arrival. No live email sent in this implementation turn. Privacy policy is a staging draft; operator details need finalization before public collection. Turnstile tokens expire and are single-use, so the browser resets the widget after every attempted submission.

Ecuador completion: pair_029 is implemented but delivery verification remains pending. Pair_027 needs permissioned genuine reviews; do not invent reviews or ratings. Whole-section accessibility, keyboard and performance review remains separate from page-count progress.
