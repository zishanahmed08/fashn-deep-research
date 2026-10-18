# FashnAI — 105–110 Second Demo Script

## Before presenting

Open these tabs in this order:

1. **FashnAI Due Diligence:** <https://fashn-deep-research.vercel.app/due-diligence>
2. **Architecture:** `file:///C:/Users/safic/Documents/Fashnai/fashn-deep-research/hackathon-demo/archify-diagram.html`
3. **Backend check:** <https://port8000-pt7m5w845bntrd3.tunnel.applications.eu-west2.nebius.cloud>

Make sure the backend is live. On the website, click **“Try example: North Face Limbara jacket”** so the URL is ready. On the architecture tab, use presentation mode and fit the full diagram on screen.

## 0:00–0:25 — Website

**[Show the Due Diligence page.]**

“Online shopping gives us plenty of product claims—price, materials, ratings and sustainability—but very little proof. FashnAI turns those claims into an evidence-based buying decision.

I’ll use this North Face jacket as a live example. One product URL is all we need.”

**[Click “Analyse”, then immediately switch to the architecture tab.]**

“While the research runs, let’s look at what happens behind this button.”

## 0:25–1:20 — Architecture

**[Trace Shopper → Next.js UI → FastAPI → DiligenceOrchestrator.]**

“The Next.js interface sends the URL to our FastAPI backend. The Diligence Orchestrator plans the investigation and launches three specialist agents in parallel.”

**[Point to PriceAgent, ReviewAnalyzerAgent and ProductSpecsAgent.]**

“The Price Agent compares listings, the Review Agent examines ratings and sentiment, and the Specs Agent extracts materials, product details and sustainability claims. Each result must include a source and supporting quote.”

**[Point to Nebius Token Factory, then FactCheckerAgent and Tavily.]**

“These agents reason with a Nebius-hosted Nemotron model. Their evidence then goes to a fourth, skeptical agent. Using Tavily, the Fact Checker searches for independent confirmation and deliberately excludes the brand’s own domain.”

**[Point to the return path: FactCheckerAgent → FastAPI → UI.]**

“Every claim becomes verified, contested or unsupported. Those claim-level checks produce one practical verdict: worth buying, conditional, or skip.”

## 1:20–1:48 — Back to the website

**[Return to the website. Show the verdict and the three claim counts.]**

“And here is the result from the request we started: a clear recommendation, with the evidence grouped by status.”

**[Open “sources” on one claim, then briefly open the Research trace.]**

“Open any claim and you can inspect both the original evidence and the independent fact-check. The research trace also shows what each agent did, so the answer is transparent—not just generated.

FashnAI doesn’t ask shoppers to trust another AI opinion. It gives them the sources to verify it.”

## Timing checkpoints

- **0:00** Start on the website
- **0:20** Click **Analyse**
- **0:25** Switch to the architecture
- **1:20** Return to the website
- **1:35** Expand one claim and the research trace
- **1:48** Finish, leaving roughly 12 seconds of buffer

## If the live result is still loading

Say: “This is a live multi-agent investigation, so it is still gathering and checking evidence. Here is a completed report showing the same output.” Then switch to a prepared screenshot or a completed result in a backup tab.
