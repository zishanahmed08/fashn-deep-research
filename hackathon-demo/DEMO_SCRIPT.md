# FashnAI — 2-Minute Demo Script

**Challenge:** Agentic Deep Research with Token Factory and Tavily (Nebius × Tavily × Reflection AI)
**Direction used:** Vendor/product due-diligence with a confidence rating per claim
**Hard rule from the brief:** one complete run, no cuts around the hard part. Blocks 0:00→1:40 are recorded as **ONE continuous screen-capture take** — the presenter switches tabs live on camera, nothing is edited around the run.

Total runtime: **2:00**. Every beat below has a timestamp, a voiceover (VO) line, what's on screen, and a pointer to the matching effect recipe in [EDITING_GUIDE.md](EDITING_GUIDE.md).

**Core trick of this edit:** the due-diligence run takes ~60–90s. Instead of staring at a loading spinner, we hit submit at 0:12 and spend that compute window explaining the architecture on the Archify diagram — then return to a finished report. The wait becomes the explanation.

---

## 0:00–0:12 — HOOK + FIRE THE RUN

**Screen:** `https://fashn-deep-research.vercel.app/` — homepage, due-diligence front and center. Type the North Face Limbara URL (or click **Try a sample product**), then click **Start due diligence**. Let the "researching" state appear on camera before we leave this tab.

**VO:**
> "You find a product you want to buy. The brand's page says it's recycled, in stock, well reviewed. How much of that can you actually trust? FashnAI finds out. I paste one URL — and while it works, I'll show you what's happening under the hood."

**On-screen text (lower third, appears at 0:08):** `FashnAI — agentic due diligence`

→ Effect recipe **R2** (lower third). Do NOT cut away until the loading state is visibly running.

---

## 0:12–1:20 — THE ARCHITECTURE, WHILE IT RUNS (live tab switch, no cut)

**Screen:** Switch browser tabs (on camera) to `hackathon-demo/archify-diagram.html`. Slow pan/zoom into the due-diligence path. Walk it in three moves:

1. **Planner + parallel research** — zoom on the branch: one request → planner decomposes → **PriceAgent, ReviewAgent, SpecsAgent** fan out **in parallel**, each crawling the live web through Tavily, each running on **Nemotron-3-Ultra-550B** via **Nebius Token Factory**.
2. **The fact-checker** — trace the claim flow: every claim the three agents produce gets handed to a fourth agent, a skeptic that re-searches Tavily **with the brand's own domain explicitly excluded**, hunting for independent confirmation or contradiction.
3. **Verdicts with receipts** — land on the output node: per-claim verdicts (verified / contested / unsupported), source URLs, verbatim quotes, and the full research trace.

**VO:**
> "Here's what's running right now. A planner decomposes my one URL into three research jobs — price, reviews, specs — and fires them in parallel. Each agent searches and reads the live web through Tavily, powered by Nemotron on Nebius Token Factory. Every claim they produce goes to a fourth agent — a skeptical fact-checker that re-searches Tavily, forbidden from trusting the brand's own site. It looks for outside evidence that confirms or contradicts each claim. That's why the answer takes a minute: it's doing real research, not recalling a cached answer."

**On-screen text, timed to move 2:** `4 agents · Nemotron-550B on Nebius · Tavily live search`
**On-screen text, timed to move 3:** `every claim → verified / contested / unsupported`

→ Effect **R1** (diagram zoom) + **R3** (caption fades synced to moves)

**Pacing rule:** rehearse the chosen URL's end-to-end time first. If the run finishes before 1:20, switch back early and let the close beat absorb the extra seconds. If it's still running at 1:20, a brief "still finishing up…" glance at the tab is fine — never fake the result.

---

## 1:20–1:40 — THE RESULTS (switch back, single take continues)

**Screen:** Switch back to the app tab (on camera). The report has landed. Scroll the **Research Trace** panel in real time: `Planner → decompose`, `dispatch`, agent completions, then — the moment that matters — the red `CONTESTED` line from the fact-checker.

**VO:**
> "And here it is — every step it actually took. Watch the fact-checker: it just caught claims the brand can't independently back up."

**On-screen text, timed to the CONTESTED trace line:** `CONTESTED` stamp, red, punches in.

→ Effect **R5** (trace auto-scroll highlight) + **R6** (contested stamp punch-in with sound hit)

---

## 1:40–1:55 — CITATIONS HOLD UP

**Screen:** Scroll to the claim cards. Click **sources** on a claim — expand to show the agent's source URL + quoted excerpt, and where present, the fact-checker's independent source + quote. Click the **Contested** card and show the challenge note.

**VO:**
> "Click any claim. Here's the source and the exact quote behind it — and the independent evidence the fact-checker found to confirm or challenge it. Nothing is asserted without a receipt."

→ Effect **R7** (cursor spotlight on click) + **R2** (verdict badge glow)

---

## 1:55–2:00 — CLOSE

**Screen:** Pull back to the top-level verdict badge. Optional 1s flash of the Archify diagram with the due-diligence path highlighted. End card.

**VO:**
> "One verdict, fully sourced, built on Nebius Token Factory and Tavily. That's FashnAI."

**End card text:**
```
FashnAI
Nebius Token Factory · Tavily · Agno
github.com/zishanahmed08/fashn-deep-research
```

→ Effect **R8** (end-card fade + tagline typewriter)

---

## Recording checklist before you hit record

- [ ] Live backend healthy: `curl https://port8000-zq4qjnhgksz8t94.tunnel.applications.eu-west2.nebius.cloud/health` returns `"status": "healthy"`
- [ ] Rehearse the exact product URL once and note its runtime — the 0:12–1:20 diagram segment must cover it
- [ ] Confirm the chosen URL produces **at least one CONTESTED or UNSUPPORTED claim** — all-verified is a weaker demo (the North Face Limbara URL currently yields 2 contested)
- [ ] Confirm the URL is **not** in `backend/cache/demo_responses.json` — a cache hit returns instantly and breaks the architecture segment
- [ ] Vercel deploy is on `main` with `NEXT_PUBLIC_API_URL` pointing at the live tunnel URL
- [ ] Browser: two tabs pre-arranged (app left, diagram right in tab order), zoom ~125%, clear history/autocomplete dropdowns
- [ ] Close notifications/Slack before recording — no pop-ups mid-take
- [ ] Record 0:00→1:40 as ONE take with live tab switches; everything after 1:40 can be cut freely