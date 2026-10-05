# Experience The Amazon build progress

Updated October 5, 2026. Current checkpoint supersedes the early pilot notes in Git history.

| Measure | Current status |
| --- | --- |
| Ecuador pairs polished in this workflow | 7 of 34 planned pairs — 20.6% |
| Site pairs polished in this workflow | 7 of the current 40-pair baseline — 17.5% |
| Existing source routes, including scaffolds | 12 pairs / 24 HTML pages — 30% of current baseline |
| Current batch | Ecuador overview + lodge guide, EN/ES, staging review |
| Other country clusters | No polished clusters yet for Peru, Brazil, Colombia, Bolivia, Guyana, Suriname or Venezuela |
| Final eight-country completion | Not calculable until missing country architectures are added |
| Launch gates | Full accessibility, measured performance and contact delivery remain pending |

The polished pairs are Ecuador overview, Yasuní, Cuyabeno, Tena, Misahuallí, Puyo and the lodge guide. Counts describe staging content/design progress, not launch readiness. The five global foundation pairs remain built but are outside this polishing count.

This batch replaces hub image placeholders with three distinct, geographically credited photos per page; adds reviewed bilingual planning cards; replaces the lodge comparison table with regional cards; balances the overview destination grid; aligns fact labels; respects sticky-header anchor space; and matches six visible FAQs with structured data. Mobile hamburger navigation remains sticky; desktop retains the sticky secondary Ecuador bar.

Local Qwen drafting ran two calls: 524 prompt tokens, 3,139 output tokens, 135.40 seconds; no inference retries or cache hits. All initial draft calls were local. The cloud supervisor substantially edited the drafts, wrote code and supervised verification. Its token usage is not exposed, so an overall cloud/local token percentage or net saving cannot be reported. Saved local records total 50,754 measured tokens across ten inference calls, including the earlier pilot aggregate.

Raw drafts, reviewed hashes, QA and rollback evidence are retained under planning/ai-os/. Small-model community assumptions and literal Spanish required correction; future hub prompts now explicitly prohibit those additions. Homepage styles were preserved, and a separate Ecuador hub stylesheet prevents the observed style collision. Current source checks validate all 24 pages and all four hub pages.

Await owner review before another batch. Suggested next pair batch: tours from Quito and the 3-day Amazon guide, subject to review. Staging only; main and production are untouched. GitHub push authorization remains unresolved.

## October 5 — Quito and 3-day batch
Two new EN/ES pairs deployed to protected staging (2893a4d3); 28 HTML pages / 14 built pairs including scaffolds. Nine Ecuador pairs have reviewed prepared content (9/34 = 26.5%); seven have initial live visual checks, with the two new pairs pending because browser admin-policy verification refused access. This is not launch completion. Static metadata, language pairing, internal routes, six matching FAQs and three distinct media assets per page pass. Existing sticky/hamburger navigation and scoped hub CSS retained; new pages require live desktop/mobile readback.
Local drafting: 2 requests, 725 input + 3,578 output = 4,303 tokens, 149.07 seconds; 0 retries, 0 cache hits, 0 cloud worker calls. Both drafts required substantial supervisor rewriting. The measured initial-draft call split is 100% local / 0% cloud; overall supervision token share is unavailable. Added tested flags for observed invented transport/timing and harmful framing; revised prompt is not yet evaluated. Contact delivery, full accessibility and measured performance remain pending. Previous deployment 25124070 / commit 10d827b retained as rollback evidence. Review current pair before the next batch.

## October 5 — 4-day and 5-day preparation
Owner authorized proceeding. Prepared two new bilingual duration guides locally: 11/34 Ecuador pairs with reviewed prepared content (32.4%), of which 9/34 are deployed (26.5%). Seven pairs have prior initial visual checks; two deployed pairs plus two newly prepared pairs await current desktop/mobile review. Local build contains 32 HTML pages / 16 pairs including scaffolds; live staging remains 2893a4d3 with 28 pages / 14 pairs. New pages have 1,563–1,613 words each, three unique rights-documented photos and six visible/schema-matched FAQs. Validation and 12 hub/format page audits pass. Nothing deployed this turn because browser access again refused the admin-enforced policy verification.
Local drafting: 2 qwen3.5:9b calls, 907 input + 3,360 output = 4,267 tokens, 144.79 seconds, no retries/cache hits. Both drafts needed substantial bilingual supervisor rewriting. Initial draft-call split: 100% local / 0% cloud; overall cloud/local token and work shares remain unknown. Observed duration confusion and presumed flexibility were corrected in reviewed JSON. The tightened local prompt has not eliminated editorial rework. Retained raw/reviewed hashes and a deterministic reviewed-source builder; release and subsequent batches wait for browser visual review. Full accessibility, measured performance and contact delivery remain pending.
