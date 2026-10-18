# FashnAI — Demo Script (single file: beats + read-aloud lines + checklist)

**Challenge:** Agentic Deep Research with Token Factory and Tavily (Nebius × Tavily × Reflection AI)
**Direction:** Vendor/product due-diligence with a confidence rating per claim
**Hard rule from the brief:** one complete run, no cuts around the hard part. Blocks 0:00→1:40 are recorded as **ONE continuous screen-capture take** — you switch tabs live on camera, nothing is edited around the run.

Total runtime: **2:00**. Effect recipes referenced as R1–R8 live in [EDITING_GUIDE.md](EDITING_GUIDE.md).

**Core trick:** the due-diligence run takes ~60–90s. Hit submit at 0:12 and spend that compute window explaining the architecture on the Archify diagram — then return to a finished report. The wait becomes the explanation.

**Key product story to land:** the report separates **facts** from **claims**. Facts (product name, brand, listed prices, sizes, care) come straight off the source page and are self-verified by a verbatim quote. Claims (material composition, sustainability, performance numbers, ratings) are handed to a skeptical fact-checker that re-searches Tavily with the brand's own domain excluded. Facts show a gray chip, claims show an indigo chip.

---

## Before presenting (tab setup)

1. **FashnAI:** https://fashn-deep-research.vercel.app/ (homepage — due-diligence front and center)
2. **Architecture:** `hackathon-demo/archify-diagram.html` (presentation mode, full diagram fit on screen)
3. Backend check: `curl https://port8000-zq4qjnhgksz8t94.tunnel.applications.eu-west2.nebius.cloud/health` returns `"status": "healthy"`

On the homepage, click **Try a sample product** so the URL is pre-filled. Close notifications/Slack. Browser zoom ~125%.

---

## 0:00–0:12 — HOOK + FIRE THE RUN

**[Show: homepage. Type/paste the North Face Limbara URL, click **Start due diligence**. Let the researching state appear on camera before leaving the tab.]**

**VO:**
> "Online shopping gives us plenty of product claims — price, materials, ratings, sustainability — but very little proof. FashnAI turns those claims into an evidence-based buying decision. I paste one URL — and while it works, I'll show you what's happening under the hood."

**On-screen text (lower third, appears at 0:08):** `FashnAI — agentic due diligence`

→ Effect **R2** (lower third). Do NOT cut away until the loading state is visibly running.

## 0:12–1:20 — THE ARCHITECTURE, WHILE IT RUNS (live tab switch, no cut)

**[Switch tabs on camera to archify-diagram.html. Slow pan/zoom into the due-diligence path. Three moves:]**

**Move 1 — Planner + parallel research. [Zoom on the branch: one request → planner → three agents.]**

**VO:**
> "Here's what's running right now. The Next.js interface sends the URL to our FastAPI backend, where a planner decomposes my one URL into three research jobs — price, reviews, specs — and fires them in parallel. Each agent searches and reads the live web through Tavily, powered by Nemotron on Nebius Token Factory."

**Move 2 — The fact-checker. [Trace the claim flow into FactCheckerAgent.]**

**VO:**
> "Every claim they produce goes to a fourth agent — a skeptical fact-checker that re-searches Tavily, forbidden from trusting the brand's own site. It looks for outside evidence that confirms or contradicts each claim. And we keep facts and claims separate: a listed price or size is a fact, self-verified by its source quote. A '100% recycled' or waterproof-rating assertion is a claim, and it has to survive independent verification."

**Move 3 — Verdicts with receipts. [Land on the output node.]**

**VO:**
> "The result: per-claim verdicts — verified, contested, unsupported — with source URLs and verbatim quotes, plus a full research trace. That's why the answer takes a minute: it's doing real research, not recalling a cached answer."

**On-screen text, timed to move 2:** `4 agents · Nemotron-550B on Nebius · Tavily live search`
**On-screen text, timed to move 3:** `facts: source-quoted · claims: independently checked`

→ Effect **R1** (diagram zoom) + **R3** (caption fades synced to moves)

**Pacing rule:** rehearse the chosen URL's runtime first. If the run finishes before 1:20, switch back early. If it's still running, a brief "still finishing up…" glance is fine — never fake the result.

## 1:20–1:40 — THE RESULTS (switch back, single take continues)

**[Switch back to the app tab. The report has landed. Scroll the Research Trace panel in real time: Planner → decompose, dispatch, agent completions, then the red CONTESTED line.]**

**VO:**
> "And here it is — every step it actually took. Watch the fact-checker: it just flagged claims the brand can't independently back up."

**On-screen text, timed to the CONTESTED trace line:** `CONTESTED` stamp, red, punches in.

→ Effect **R5** (trace auto-scroll highlight) + **R6** (contested stamp punch-in with sound hit)

## 1:40–1:55 — CITATIONS HOLD UP

**[Scroll to claim cards. Click "sources" on one green claim — expand to show the agent's source URL + quote and, where present, the fact-checker's independent source + quote. Click a Contested card and read the challenge note. Point out the Fact/Claim chips.]**

**VO:**
> "Click any claim. Here's the source and the exact quote behind it — and the independent evidence the fact-checker found to confirm or challenge it. Gray chips are facts, straight off the page. Indigo chips are claims that had to earn their verdict. Nothing is asserted without a receipt."

→ Effect **R7** (cursor spotlight on click) + **R2** (verdict badge glow)

## 1:55–2:00 — CLOSE

**[Pull back to the top-level verdict badge. Optional 1s flash of the Archify diagram with the due-diligence path highlighted. End card.]**

**VO:**
> "One verdict, fully sourced, built on Nebius Token Factory and Tavily. FashnAI doesn't ask shoppers to trust another AI opinion — it gives them the sources to verify it."

**End card text:**
```
FashnAI
Nebius Token Factory · Tavily · Agno
github.com/zishanahmed08/fashn-deep-research
```

→ Effect **R8** (end-card fade + tagline typewriter)

---

## Timing checkpoints (self-correct mid-presentation)

- **0:12** submit clicked, switching to diagram
- **0:45** mid-move-2 (fact-checker)
- **1:20** back on the app, results on screen
- **1:35** expanding citations
- **2:00** verdict + close

**If ahead of pace:** linger on one expanded citation and read the quote aloud — judges value that more than rushing.

**If behind pace:** drop citation-clicking to one claim; skip straight from trace to verdict.

**If the live result is still loading at 1:20:** say "This is a live multi-agent investigation, so it's still gathering and checking evidence" and show a completed backup report (cached tab — see checklist).

---

## Recording checklist before you hit record

- [ ] Live backend healthy: `curl https://port8000-zq4qjnhgksz8t94.tunnel.applications.eu-west2.nebius.cloud/health` returns `"status": "healthy"`
- [ ] Rehearse the exact product URL once and note its runtime — the 0:12–1:20 diagram segment must cover it
- [ ] Confirm the chosen URL produces **at least one CONTESTED or UNSUPPORTED claim** — all-verified is a weaker demo
- [ ] Primary take uses a URL **not** in `backend/cache/demo_responses.json` (a cache hit returns instantly and breaks the architecture segment). Backup tab: the cached North Face report loads instantly
- [ ] Vercel deploy is on `main` with `NEXT_PUBLIC_API_URL` pointing at the live tunnel URL
- [ ] Browser: two tabs pre-arranged (app, diagram), zoom ~125%, clear autocomplete dropdowns
- [ ] Close notifications/Slack before recording — no pop-ups mid-take
- [ ] Record 0:00→1:40 as ONE take with live tab switches; everything after 1:40 can be cut freely