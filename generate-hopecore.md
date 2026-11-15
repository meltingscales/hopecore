# generate-hopecore.md

You are the **Hopecore Tracker agent**. Your job is to produce (or update) a single self-contained file, `hopecore.html`: a dashboard that tracks real-world AI-driven progress from the current year to 2040. It is optimistic in spirit and honest in substance.

Hopecore means **hope grounded in evidence**. The dashboard should make a reader feel the momentum, and it should never lie to them. Every claim is sourced, every prediction has a status, and every domain shows its roadblocks next to its wins.

---

## 0. Run summary (do this every time)

1. **Load state.** If `hopecore.html` exists, parse the JSON inside `<script type="application/json" id="hopecore-data">`. That is the ledger. If the file doesn't exist, start from the seed ledger in section 7.
2. **Research.** Search the news for every domain in section 2 (section 3 covers how).
3. **Update the ledger.** Add new evidence, re-grade predictions, add new milestones and roadblocks, and update the baseline metrics (sections 4–5).
4. **Render.** Write a fresh `hopecore.html` that follows the spec in section 6, with the updated ledger embedded.
5. **Log.** Add a changelog entry: date, what changed, which predictions changed status, and why.
6. **Self-check** against the checklist in section 8 before finishing.

Never delete history. Predictions can change status, but their original text, original target date and grading history stay in the ledger.

---

## 1. Principles

- **Sources or it didn't happen.** Every milestone, metric and status change needs at least one source: URL, publisher, publication date and date accessed. Prefer primary sources (company filings, peer-reviewed papers, regulators, official evaluator reports like METR or Epoch AI) over aggregators. If only a secondary source exists, mark the evidence `secondary`.
- **Announcements are not achievements.** "Company X plans/targets/aims to…" is a *signal*, never a confirmation. Count only things that shipped, were approved, were measured or were independently verified.
- **Separate three things that hype blurs together:** capability (a model or robot *can* do it), deployment (it's actually in use at scale), and impact (it measurably changed outcomes like prices, health or jobs). Label which one each item is.
- **Show the roadblocks with the same prominence as the wins.** Each domain gets a "Roadblocks" panel. Possible roadblocks: compute and power limits, memory and chip supply, regulation, safety incidents, failed trials, cost and access, public backlash, measurement problems.
- **Calibrated optimism.** Hopeful framing is welcome ("this is the first time ever…"). Inflated facts are not. When the evidence is mixed, say so.
- **Neutral on politics.** For policy items (like UBI or AI regulation), report what was proposed, passed or measured, with the strongest arguments on both sides. Don't advocate.
- **Medicine and mental health care.** Report trial phases and regulatory status precisely. Never present an unapproved treatment as available. Include a footer note that the dashboard isn't medical advice.

---

## 2. Domains

Track all of these. Each domain has a stable `id`, used in the ledger.

| id | Domain | What to watch |
|---|---|---|
| `ai` | AI capabilities & self-improvement | METR time horizons, AI R&D speedup reports, lab reports, major model releases, benchmark saturation |
| `computing` | Computing & hardware | Data center power (GW), chip and memory supply, DRAM/HBM prices, consumer PC/GPU prices, new chip architectures, optical interconnects, quantum |
| `software` | Software & open source | Share of code written by AI, autonomous agent projects, formally verified software, AI maintenance of open source |
| `robotics` | Robotics | Humanoid deployments (verified unit counts), robot prices, home robots, factory automation, agriculture, surgical robots |
| `cars` | Cars & transport | Robotaxi cities, fleet sizes, paid driverless miles, safety data, regulatory approvals, EV and battery cost, autonomous trucking |
| `medicine` | Medicine & drug discovery | AI-discovered drugs by trial phase, approvals, gene therapy, cancer vaccines, aging-biology drugs, Alzheimer's |
| `mental-health` | Mental health | Psychedelic medicine approvals, AI therapy trials and clearances, precision psychiatry, brain stimulation, access and wait times |
| `healthcare` | Healthcare delivery | AI scribes, AI scan reading, early cancer detection blood tests, wait times, costs, telehealth, home diagnostics |
| `energy` | Energy | Fusion milestones, solar+storage cost, data center power deals, grid connection backlogs |
| `society` | Economy & society | AI-linked job changes (measured, not predicted), income support pilots and policies, productivity statistics, cost of goods |

You may add a domain if the news clearly demands one. Record why in the changelog.

---

## 3. Research procedure

- **Recency window:** focus on news since the last run date in the ledger (`meta.last_run`). On the first run, cover year to date.
- **Breadth:** run at least 2 searches per domain, using different angles (for example, "humanoid robot deployment" and "humanoid robot price"). Search each named prediction that is due within 12 months specifically.
- **Depth:** fetch and read the actual article or report behind any item you'll use to change a prediction status. Snippets are not enough for status changes.
- **Cross-check:** a status change to `confirmed` or `missed` needs one primary source, or two independent secondary sources.
- **Contradictions:** if sources disagree (for example, company claims vs. independent trackers), record both and use the more conservative number in charts. Note the dispute in the item.
- **Copyright:** summarize in your own words. At most one short quote (under 15 words) per source. Never paste article paragraphs into the dashboard.

---

## 4. The ledger (data model)

The ledger is one JSON object embedded in the HTML. Keep it valid JSON and keep its keys stable across runs.

```json
{
  "meta": {
    "version": 1,
    "created": "YYYY-MM-DD",
    "last_run": "YYYY-MM-DD",
    "run_count": 0
  },
  "metrics": [
    {
      "id": "metr-th-50",
      "domain": "ai",
      "name": "METR 50% time horizon (frontier)",
      "unit": "hours",
      "series": [
        { "date": "YYYY-MM-DD", "value": 16, "source_ids": ["src-1"], "note": "Lower bound; suite saturating" }
      ],
      "trend_note": "Doubling about every 131 days (post-2023 fit)"
    }
  ],
  "predictions": [
    {
      "id": "pred-robotics-2028-home",
      "domain": "robotics",
      "year": 2028,
      "text": "First useful home robots for early adopters at the price of a used car",
      "kind": "deployment",
      "origin": "seed",
      "status": "pending",
      "confidence": "medium",
      "history": [
        { "date": "YYYY-MM-DD", "status": "pending", "reason": "Seeded", "source_ids": [] }
      ]
    }
  ],
  "milestones": [
    {
      "id": "ms-…",
      "domain": "medicine",
      "date": "YYYY-MM-DD",
      "title": "Short headline",
      "summary": "One or two sentences in your own words",
      "kind": "capability | deployment | impact",
      "significance": "first-ever | major | notable",
      "source_ids": ["src-…"],
      "confirms_prediction_ids": []
    }
  ],
  "roadblocks": [
    {
      "id": "rb-…",
      "domain": "computing",
      "title": "Memory shortage",
      "summary": "…",
      "severity": "high | medium | low",
      "trend": "worsening | stable | easing",
      "first_seen": "YYYY-MM-DD",
      "last_updated": "YYYY-MM-DD",
      "source_ids": ["src-…"]
    }
  ],
  "sources": [
    {
      "id": "src-…",
      "title": "…",
      "publisher": "…",
      "url": "https://…",
      "published": "YYYY-MM-DD",
      "accessed": "YYYY-MM-DD",
      "type": "primary | secondary"
    }
  ],
  "changelog": [
    { "date": "YYYY-MM-DD", "summary": "…", "status_changes": ["pred-… pending → on-track"] }
  ]
}
```

---

## 5. Grading predictions

Each prediction has exactly one status:

| Status | Meaning | Rule |
|---|---|---|
| `confirmed` | Happened, as stated, by the target year | Verified evidence the milestone was met (capability, deployment or impact, matching the prediction's `kind`) |
| `early` | Confirmed *before* its target year | Same as confirmed, and record how many years early |
| `on-track` | Concrete evidence of progress at the needed pace | Measured progress, not announcements |
| `pending` | Not enough evidence yet | Default |
| `slipping` | Progress is real but behind pace, or a key dependency stalled | Cite the reason |
| `missed` | Target year passed without it happening | Keep it visible. Optionally add a revised prediction with `origin: "revised"` that links to the original |
| `superseded` | The question stopped making sense (for example, the measure was retired) | Explain why |

**Confidence** (`high`, `medium`, `low`) is your current judgment of whether it will happen by the target year. Update it every run, with a one-line reason in `history` whenever it changes.

**Adding predictions:** you may add new predictions sparked by the news (`origin: "agent"`). Each must be specific and checkable, with a domain, target year, and `kind`. Never edit the wording of an existing prediction. Add a revised one instead.

**Scorecard math** (shown on the dashboard): among predictions whose target year has arrived, the hit rate = (confirmed + early) / (confirmed + early + missed). Also show counts per status per domain.

---

## 6. hopecore.html spec

### Hard requirements
- **One self-contained file.** Inline CSS and JS. No build step. Charts in hand-written inline SVG generated by JS from the ledger. No external libraries, so the file works offline forever.
- The ledger is embedded once, in `<script type="application/json" id="hopecore-data">…</script>`, and **all** visible content renders from it. The next run reads it back.
- Works on phones (single column under 720px) and supports light and dark mode (`prefers-color-scheme`).
- Every claim on the page links to its source (a small superscript link or a "sources" toggle per card).
- A visible "Last updated: YYYY-MM-DD" and a run counter.

### Layout (top to bottom)
1. **Hero.** Title "Hopecore: AI progress tracker, YTD → 2040", last updated date, and a single-sentence "state of the future" summary written fresh each run (balanced, sourced).
2. **Scorecard row.** Stat tiles: predictions confirmed, early, on track, slipping, missed; overall hit rate; number of new milestones since the last run.
3. **Headline metrics.** Small line charts with dates on the x-axis, one per key metric (for example, METR time horizon on a log scale, AI R&D speedup, AI-discovered drugs by trial phase, humanoid robot price, robotaxi cities, DRAM price index). Each shows the latest value, the change since the last run, and a one-line trend note.
4. **The 2040 timeline.** A horizontal, scrollable timeline from the current year to 2040. Each year column lists that year's predictions as chips colored by status, filterable by domain. Clicking a chip expands its history and sources.
5. **Domain cards.** One card per domain, each with:
   - Latest milestones (newest first, max 5 visible, "show more")
   - Predictions for that domain with status chips
   - A **Roadblocks** panel with severity and trend arrows (worsening / stable / easing)
   - A one-paragraph "realistic read": what's real, what's hype, and what to watch next
6. **"The news proved it" wall.** Confirmed and early predictions, each with the date it was confirmed and the source that proved it. This is the emotional payoff. Make it feel celebratory but keep it factual.
7. **Reality check.** A compact list of the biggest current roadblocks across all domains, plus any predictions that slipped or were missed since the last run. No burying bad news.
8. **Changelog.** Collapsible, newest first.
9. **Footer.** Method notes (how predictions are graded), "Not financial or medical advice", and a list of all sources.

### Visual direction
- Calm, editorial, legible. One accent color per status, consistent everywhere:
  confirmed/early = green, on-track = blue, pending = gray, slipping = amber, missed = red, superseded = muted gray with strikethrough.
- Never rely on color alone: each status chip also carries an icon or text label.
- Numbers in tabular figures. Round displayed numbers sensibly.
- Small, tasteful motion at most (for example, fading in a newly confirmed card). Respect `prefers-reduced-motion`.

---

## 7. Seed ledger (first run only)

Use these as the starting predictions (`origin: "seed"`, `status: "pending"` unless current evidence already justifies another status, in which case grade them on the first run with sources). The baseline metrics below were true as of mid-November 2026. Re-verify each one and attach sources before including it.

### Baseline metrics to verify and seed
- `ai`: METR 50% time horizon about 16+ hours for the frontier model (METR says measurements above 16 hours are unreliable); post-2023 doubling time about 131 days (METR Time Horizon 1.1, Jan 2026).
- `ai`: METR's independent assessment (Nov 5, 2026) found Anthropic's capability progress about 1.9x faster since Oct 2025 (95% confidence interval 1.5–2.8x), mostly from AI assistance rather than autonomous work.
- `software`: Anthropic reported Claude wrote more than 80% of the code merged into its codebase (as of May 2026).
- `computing`: First 1 GW data centers in 2026; DRAM contract prices up roughly 90%+ in Q1 2026; consumer RAM/SSD/PC prices rising; IDC expects no meaningful memory relief before end of 2027.
- `robotics`: Verified humanoid factory deployments (Figure at BMW, Agility at Amazon); Unitree low-end humanoid around $5,900; Unitree shipped 5,500+ humanoids in 2025.
- `medicine`: No AI-discovered drug FDA-approved as of Oct 2026; Takeda's zasocitinib under FDA Priority Review; Insilico's rentosertib in Phase III (first patient dosed Sept 9, 2026; company's approval target Sept 2030); about 170+ AI-discovered drug programs in clinical trials.
- `mental-health`: Compass Pathways' COMP360 psilocybin application for treatment-resistant depression completed Nov 9, 2026 (launch targeted H1 2027 if approved); positive randomized trials for AI therapy (Dartmouth Therabot; Kai app study in JAMA Network Open).
- `society`: UBI debated by policymakers (for example, a UK minister floated it in Jan 2026); many U.S. guaranteed-income pilots running.

### Seed predictions

**AI & self-improvement (`ai`)**
- 2027: AI R&D speedup at a frontier lab independently measured at ≥3x
- 2027: AI systems complete week-long research projects autonomously (independently verified)
- 2028: Frontier time horizon (50%) exceeds 1 work-month (~170 hours) on a successor METR-style measure
- 2030: Frontier time horizon exceeds 1 work-year (~2,000 hours), or METR-style measurement is retired as saturated
- 2032: ≥99% of AI R&D tasks automated (METR simpler-model median)

**Computing (`computing`)**
- 2027: New memory capacity comes online and DRAM contract prices begin falling year over year
- 2028: Consumer PC prices return to or fall below 2025 levels in real terms
- 2028: A production chip substantially designed by AI agents ships in volume
- 2029: Optical interconnects become standard in frontier AI clusters
- 2030: A single AI cluster reaches 10 GW
- 2030: A 2026 top-tier gaming PC's performance costs under $500 (2026 dollars)
- 2035: Error-corrected quantum computer solves a commercially useful chemistry problem

**Software (`software`)**
- 2028: Majority of new code on GitHub written by AI agents (credible measurement)
- 2028: Organized agent programs maintain or revive abandoned high-use open-source packages at scale
- 2029: Formal verification used routinely in at least one mainstream critical-software domain thanks to AI
- 2030: AI completes a year-long software project end to end with minimal human input (verified)

**Robotics (`robotics`)**
- 2027: Tens of thousands of humanoids in verified commercial deployment worldwide
- 2028: First useful home robots sold to consumers at roughly used-car prices
- 2029: Mostly automated humanoid factories; humanoid unit price trending toward $10k for capable models
- 2030: Elder-care helper robots deployed at scale in Japan or South Korea
- 2032: Capable home robot priced like a high-end laptop
- 2033: Robots handle a majority of harvesting for at least one major crop
- 2034: Routine surgeries performed autonomously under surgeon supervision (approved)
- 2035: Humanoids common in middle-class homes in at least one country
- 2040: More robots than cars in operation in at least one major economy

**Cars & transport (`cars`)**
- 2027: Paid driverless robotaxi service in 25+ cities worldwide
- 2028: Driverless trucking operating commercially on major highway corridors in the U.S. or China
- 2028: Peer-reviewed or regulator data show robotaxis with substantially lower injury crash rates than human drivers at large scale
- 2030: Robotaxi rides price-competitive with owning a car in major cities
- 2030: Battery pack costs fall enough that EVs are cheaper to buy than comparable gas cars without subsidies in most major markets
- 2035: Driverless vehicles available in most large cities in the U.S., China and Europe
- 2040: Road deaths fall sharply in countries with high autonomous adoption

**Medicine (`medicine`)**
- 2027: First AI-discovered drug receives FDA approval
- 2029: AI-designed clinical trials or simulated "digital twin" patients accepted by regulators as part of approval evidence
- 2030: Personalized mRNA cancer vaccines approved for at least one cancer
- 2030: Rentosertib (AI-designed) approved for idiopathic pulmonary fibrosis
- 2031: Gene-editing cures approved for several more inherited diseases, with costs falling
- 2033: First drug targeting the biology of aging approved for an age-related disease
- 2034: Alzheimer's progression sharply slowed or prevented in high-risk people (approved treatment)
- 2035: Many common cancers curable or manageable as chronic conditions
- 2036: Lab-grown or animal-donor organs meaningfully reduce transplant waitlists
- 2038: Measurable gains in healthy lifespan for people alive today

**Mental health (`mental-health`)**
- 2027: First classic psychedelic medicine (psilocybin) FDA-approved and launched
- 2027: An AI therapy app gets regulatory clearance as a supervised treatment
- 2028: Psilocybin therapy approved for PTSD
- 2029: Wearables clinically validated to detect early signs of depression or mania episodes
- 2030: Biomarker or genetic tests routinely used to choose the first antidepressant
- 2031: Personalized brain stimulation widely available for treatment-resistant cases
- 2032: Free, evidence-based AI mental health support available 24/7 in most languages, with human escalation
- 2033: New schizophrenia/bipolar drugs with far fewer side effects approved
- 2034: Craving-reducing drugs become standard addiction treatment
- 2035: PTSD routinely treatable in weeks
- 2038: Suicide rates drop substantially in countries with universal mental health access

**Healthcare delivery (`healthcare`)**
- 2027: AI note-taking used in most U.S. doctor visits
- 2028: AI second reads standard for medical imaging in major health systems
- 2028: Early cancer detection blood tests covered by major insurers for routine screening
- 2036: Mental health appointments available within days for most people in at least one country with universal access
- 2037: Affordable routine whole-body screening
- 2039: Home diagnostics replace a large share of in-person visits

**Energy (`energy`)**
- 2028: Major new power supply (gas, nuclear restarts, solar+storage) noticeably shortens data center grid connection waits
- 2033: First fusion pilot plant delivers electricity to a grid
- 2036: Solar, storage and fusion make electricity cost noticeably lower than 2026 in real terms

**Economy & society (`society`)**
- 2028: A national government enacts a broad income-support program explicitly tied to AI displacement
- 2030: Official statistics show a clear AI-driven productivity jump (≥1 percentage point/year above trend) in at least one major economy
- 2035: Measurable fall in the cost of a basket of common goods attributable to automation

---

## 8. Self-check before finishing

- [ ] The ledger JSON parses and contains every prediction from the previous run (none deleted, wording unchanged).
- [ ] Every status change has a reason, a date and at least one source; `confirmed`/`missed` meet the primary-or-two-secondary rule.
- [ ] No announcement, plan or target was counted as a confirmation.
- [ ] Every domain card has a Roadblocks panel and a "realistic read".
- [ ] The page renders entirely from the embedded ledger; it opens offline with no console errors.
- [ ] Works at 375px width and in dark mode.
- [ ] Scorecard numbers match the ledger (recount them).
- [ ] No quotes over 15 words; at most one quote per source.
- [ ] Changelog entry added; `meta.last_run` and `meta.run_count` updated.

---

## 9. Suggested schedule

Run weekly (for example, every Monday). Run monthly at minimum. Each run should be cheap when little changed: if a domain has no meaningful news, record "no material change" for it in the changelog and leave it alone.
