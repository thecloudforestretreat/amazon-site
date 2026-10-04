# Experience The Amazon analytics implementation

## Production configuration

- GA4 property: `Experience The Amazon` (`557349745`)
- Web stream: `ExperienceTheAmazon.com Production` (`16042105636`)
- Measurement ID: `G-TTSHGZCZZW`
- Search Console property: `sc-domain:experiencetheamazon.com`
- BigQuery project: `mindo-bird-watching` (`1038556015352`)
- BigQuery export: daily events, US data location
- GA4 event retention: 14 months

The implementation lives in `/assets/js/head.js`. It runs only on
`experiencetheamazon.com` and `www.experiencetheamazon.com`; preview and local
hosts are excluded. `/testing`, `/testing2`, and `/testing3` are also excluded
from collection.

## Consent and privacy

Analytics storage defaults to denied. The Google tag is not downloaded until a
visitor chooses **Allow analytics**. Advertising storage, ad user data, ad
personalization, Google Signals, and personalized-ad signals remain disabled.

Never send names, email addresses, phone numbers, message text, booking notes,
or other user-entered content to GA4. The shared script strips common PII query
parameters from recorded URLs and removes common PII keys from event payloads.

Every public page must offer a persistent footer link that calls:

```html
<button type="button" onclick="etaAnalytics.openPrivacyChoices()">
  Privacy choices
</button>
```

Add bilingual privacy-policy pages before accepting inquiries. The final policy
must identify the operating legal entity and contact address; those details must
not be invented in code.

## Required page metadata

Every English/Spanish page pair must have a stable, shared `data-pair-id` and a
unique `data-page-id`. Add these attributes to the root `html` element:

```html
<html lang="en"
  data-page-id="ecuador-amazon-lodges-en"
  data-pair-id="ecuador-amazon-lodges"
  data-page-type="destination"
  data-country="ecuador"
  data-destination="ecuadorian-amazon"
  data-topic-cluster="amazon-lodges"
  data-funnel-stage="consideration">
```

The Spanish partner uses the same `data-pair-id`, changes `lang` to `es`, and
uses a language-specific `data-page-id`. These fields accompany page views and
all custom events so performance can be compared by page pair, language,
country, destination, topic cluster, page type, and funnel stage.

## Event taxonomy

The shared script records these interactions automatically after consent:

| Event | Trigger | Important parameters |
| --- | --- | --- |
| `page_view` | Page load | page and content metadata |
| `internal_link_click` | Link to this site | `link_text`, `link_url`, CTA fields |
| `outbound_click` | External link | `link_text`, `link_domain`, `link_url` |
| `language_switch` | English/Spanish switch | `target_language` |
| `click_whatsapp` | WhatsApp link | CTA fields |
| `click_phone` | Telephone link | CTA fields |
| `click_email` | Email link | CTA fields |
| `download_itinerary` | PDF/download/itinerary link | CTA fields |
| `form_start` | First focus inside a form | `form_id` |
| `form_submit` | Form submit attempt | `form_id` |

Use `data-cta-id`, `data-cta-position`, and `data-module-id` on meaningful links
and buttons. `data-analytics-label` can provide a stable label when visible text
is not suitable.

`form_submit` is diagnostic and is not a lead. Fire `generate_lead` only after
the backend or form provider confirms successful delivery:

```js
window.etaAnalytics.track("generate_lead", {
  form_id: "trip-inquiry",
  lead_channel: "website_form"
});
```

Likewise, fire `purchase` only after a booking is confirmed, with a non-PII
transaction ID, currency, and value. Never infer a conversion from a button
click.

## Reporting model

GA4 provides acquisition, engagement, landing-page, language, and conversion
reporting. Search Console provides queries, pages, countries, devices, clicks,
impressions, CTR, and average position. The Search Console link supports organic
landing-page analysis in GA4. Daily BigQuery export preserves event-level data
for page-pair comparisons, assisted journeys, content cohorts, QA, and future
Looker Studio reporting.

The following event-scoped GA4 custom dimensions were created on October 4,
2026: `page_id`, `pair_id`, `language`, `page_type`, `country`, `destination`,
`topic_cluster`, `funnel_stage`, `cta_id`, `cta_position`, `module_id`,
`form_id`, `partner_id`, and `target_language`.

Mark `generate_lead` as a key event after the first verified form-success event
is received. It must not be created from the current `form_submit` diagnostic
event because that event represents an attempt, not confirmed delivery. Mark
`purchase` when booking checkout is implemented and a confirmed-transaction
event is available.

## Release QA

1. Confirm the English and Spanish page metadata and canonical/hreflang pair.
2. Confirm no Google request occurs before analytics consent.
3. Accept analytics and verify one `page_view` in GA4 DebugView/Realtime.
4. Test each CTA and form event without submitting personal data.
5. Confirm a successful inquiry emits one `generate_lead`, while validation and
   delivery failures do not.
6. Check GA4 and BigQuery on the following day; daily export is not immediate.
7. Re-crawl the deployed site and reconcile indexable URLs with the sitemap.
