# FashnAI — 2-Minute Demo Script

**Challenge:** Agentic Deep Research with Token Factory and Tavily (Nebius × Tavily × Reflection AI)
**Direction used:** Vendor/product due-diligence with a confidence rating per claim
**Hard rule from the brief:** one complete run, no cuts around the hard part. Record the due-diligence run **live and unedited** as a single screen-capture take; everything else can be cut around it.

Total runtime: **2:00**. Every beat below has a timestamp, a voiceover (VO) line, what's on screen, and a pointer to the matching effect recipe in [EDITING_GUIDE.md](EDITING_GUIDE.md).

---

## 0:00–0:12 — HOOK

**Screen:** `hackathon-demo/archify-diagram.html` open full-screen — the whole FashnAI system in one interactive view (frontend → FastAPI → 4 agents → Nebius/Tavily/Gemini → external sites). Slow pan/zoom into the due-diligence branch.

**VO:**
> "You find a product you want to buy. The brand's page says it's organic cotton, 4.8 stars, in stock. How much of that can you actually trust?"

**On-screen text (lower third, appears at 0:08):** `FashnAI — agentic due diligence`

→ Effect recipe **R1** (diagram zoom) + **R2** (lower third)

---

## 0:12–0:30 — THE WHOLE PRODUCT, FAST

**Screen:** Quick cuts (1–2s each) across the live app: home search → price comparison tab → review sentiment tab → virtual try-on image. Then land on the **Due Diligence** page.

**VO:**
> "FashnAI already runs four agents to compare prices, read reviews, pull specs, and even try the product on for you. For this challenge, we gave it a fifth job: don't just report what the brand says — verify it."

**On-screen text:** `4 research agents → 1 fact-checker`

→ Effect **R3** (quick-cut montage with whip-pan transitions)

---

## 0:30–1:00 — THE REAL RUN (live, unedited, no cuts)

**Screen:** Paste a real product URL into the Due Diligence page, hit submit. Let the loading state run on camera.

**VO:**
> "I paste one URL. Behind it, a planner decomposes the question into three jobs — price, specs, reviews — and runs them in parallel against the live web."

**On-screen caption (small, corner):** `Nebius Token Factory · Nemotron-3-Super-120B` appears as soon as the request fires.

→ Effect **R4** (terminal/network-call glow ping, no cut)

---

## 1:00–1:35 — THE DECISION TRACE

**Screen:** The Trace Panel scrolling in real time: `Planner → decompose`, `Planner → dispatch`, `PriceAgent → complete (N claims)`, `ReviewAgent → complete`, `SpecsAgent → complete`, `FactChecker → start`, then — the moment that matters — `FactChecker → challenge: CONTESTED "..."`.

**VO:**
> "Every claim those three agents make gets handed to a fourth agent — a skeptical fact-checker running on Nebius, searching Tavily, explicitly forbidden from trusting the brand's own domain. Watch: it just caught a claim the brand can't actually back up."

**On-screen text, timed to the CONTESTED trace line:** `CONTESTED` stamp, red, punches in.

→ Effect **R5** (trace auto-scroll highlight) + **R6** (contested stamp punch-in with sound hit)

---

## 1:35–1:50 — CITATIONS HOLD UP

**Screen:** Scroll to the claim cards. Click "sources" on a **Verified** (green) claim — expand to show the agent's source URL + quoted excerpt, and the fact-checker's independent source + quote. Click a second one. Click the **Contested** (yellow) one and show why.

**VO:**
> "Click any claim. Here's the agent's source and quote — and here's the independent source the fact-checker found that confirms, or contradicts, it. Every number is clickable. Nothing is asserted without a receipt."

→ Effect **R7** (cursor spotlight on click) + **R2** (verdict badge glow)

---

## 1:50–2:00 — CLOSE

**Screen:** Pull back to the top-level verdict badge (e.g. "Conditional — one contested claim, review before buying"). Cut to Archify diagram one more time, now with the due-diligence path highlighted end-to-end. End card.

**VO:**
> "One verdict, fully sourced, built on Nebius Token Factory and Tavily. That's FashnAI."

**End card text:**
```
FashnAI
Nebius Token Factory · Tavily · Agno
github.com/<your-org>/fashn-deep-research
```

→ Effect **R8** (end-card fade + tagline typewriter)

---

## Recording checklist before you hit record

- [ ] `.env` has live `NEBIUS_API_KEY` and `TAVILY_API_KEY` — confirm with one throwaway run first (the brief: "if the report has no sources, your Tavily key isn't set")
- [ ] Pick a product URL in advance where you've already seen it produce **at least one contested or unsupported claim** — a run with all-verified claims is a weaker demo
- [ ] Backend + frontend both running (`./start.sh`), browser zoomed to ~125% so on-screen text reads clearly when re-encoded
- [ ] Close notifications/Slack before recording — no pop-ups mid-take
- [ ] Do the 0:30–1:35 block as ONE continuous take. Everything outside it can be cut freely.
