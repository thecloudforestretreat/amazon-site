# Ecuador contact activation

Implemented: Pages Function `/api/contact`; bilingual general and Ecuador contact forms; managed Turnstile with server validation of success, staging hostname and `contact` action; bounded input, consent and honeypot validation; Brevo transactional email; disabled-on-missing-configuration UI. No form contents or secrets logged; no newsletter subscription or lead-list creation. API acknowledgement means queued, not inbox delivery.

Configure the `amazon-site-staging` project only. Its branch `staging` is served by the primary environment (labelled Production by Pages); Preview also has the dedicated Turnstile bindings. This is the protected staging website, not the public production project. Inspect deployment environment before setting email bindings:

- `TURNSTILE_SITE_KEY`: public key for a managed widget restricted to `staging.experiencetheamazon.com`.
- `TURNSTILE_SECRET_KEY`: secret binding.
- `BREVO_API_KEY`: secret binding for the owner's Brevo account.
- `CONTACT_FROM`: verified Brevo sender email.
- `CONTACT_TO`: owner-selected receiving inbox.
- `CONTACT_ENABLED`: `true` only when the above are valid and protected-staging testing is authorized.

Do not paste secrets into chat or commit them. Use Pages environment secrets and redeploy the staging branch after configuring. The endpoint defaults to the protected staging hostname. Production activation requires an explicit CONTACT_HOSTNAME of experiencetheamazon.com (or www.experiencetheamazon.com), a matching Turnstile widget and separate environment secrets. Direct pages.dev hostnames remain rejected.

Sixteen mocked endpoint tests cover configuration failure, wrong origin/hostname/action, missing consent/token, invalid inputs/honeypot, delivery rejection, body limit, service outage and verified queued flow. Run `node --test scripts/test-contact.mjs`.

Still required: real Turnstile challenge and submission, Brevo acceptance, and owner-confirmed inbox arrival. No live email sent in this implementation turn. Privacy policy is a staging draft; operator details need finalization before public collection. Turnstile tokens expire and are single-use, so the browser resets the widget after every attempted submission.

Ecuador completion: pair_029 is implemented but delivery verification remains pending. Pair_027 is deferred by the owner and does not block launch. Whole-section accessibility, keyboard and performance review remains separate from page-count progress.

October 6 update: dedicated managed staging Turnstile widget created, pre-clearance off; site/secret keys stored in primary and preview bindings; EN desktop and ES mobile automatic verification visually succeeded. First/last names and eight country options are live. Brevo configuration and a real delivery test remain pending.

Travel fields update: first name, last name, email, start date and end date required. Optional phone (32 characters) and guests (1–99). Both dates must be today or future using the Ecuador calendar (America/Guayaquil); end cannot precede start. Browser controls and server validation enforce these rules. Deployment e95137a2; EN desktop and ES mobile verified.
