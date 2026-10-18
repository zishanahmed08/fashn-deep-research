# FashnAI — 2-Minute Concept Pitch (Archify-driven)

For presenting the **concept** against the challenge brief, not a feature walkthrough. The only visual you need is `archify-diagram.html` — point at the named node as you say its line. No live app, no API keys, nothing that can fail on stage.

Open the diagram full-screen before you start talking.

---

**[Diagram: full view]**

"The challenge was: build a research agent that turns a question into a sourced, verifiable answer. It has to plan its searches, decide when it has enough evidence, and cite where every claim came from. We built that inside a product that already existed — FashnAI."

**[Point: Shopper → Next.js UI]**

"Someone pastes a product URL. One question: can I trust what this listing is telling me?"

**[Point: FastAPI → DiligenceOrchestrator]**

"That's the planner. It decomposes one vague question — 'can I trust this?' — into three concrete research jobs: price, specs, and reviews."

**[Point: the three agents — PriceAgent, ReviewAnalyzerAgent, ProductSpecsAgent]**

"Three agents run those jobs in parallel against the live web. These aren't new — they're the same agents already powering FashnAI's everyday price-comparison product. Every fact they produce comes out as a claim with a source URL and a quote attached."

**[Point: Nebius Token Factory]**

"All of them reason on Nebius Token Factory — that's the primary inference layer the challenge required."

**[Point: FactCheckerAgent]**

"Here's the part that answers the brief directly: a fourth agent takes every one of those claims and tries to break them."

**[Point: Tavily]**

"It searches Tavily for independent confirmation — and it's explicitly instructed to exclude the brand's own domain. If only the brand's marketing page supports a claim, that claim gets marked unsupported, not verified."

**[Point: the verdict / claim cards in the diagram's notes]**

"Verified, contested, or unsupported — per claim, with the receipt attached. One contested claim is enough to downgrade the whole recommendation. That's the 'decide when you have enough evidence' part of the brief, made concrete."

**[Pull back to full diagram]**

"Planner, parallel researchers, a skeptical fact-checker that tries to break the draft — on Nebius Token Factory, verified through Tavily. That's FashnAI's answer to this challenge."

---

### Timing checkpoints
0:15 → finished the hook, pointing at the UI · 0:35 → pointing at the orchestrator · 1:00 → pointing at the three agents · 1:20 → pointing at Nebius · 1:35 → pointing at Tavily · 1:50 → verdict line · 2:00 → closing line.

### Why this version, not the live-demo one
[PRESENTER_SCRIPT.md](PRESENTER_SCRIPT.md) walks the actual running app and needs real API keys plus a working live run — better once you've rehearsed a run that produces a contested claim. This version only needs the diagram, so it's the safer fallback if the live app isn't ready, and it's the stronger opener if your 2 minutes are really about judging criteria (originality, tool use, decisions-not-script) rather than proving the UI works.
