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
