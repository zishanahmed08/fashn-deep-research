# Hackathon Demo Kit

Everything needed to record and cut the 2-minute submission video for the **Agentic Deep Research with Token Factory and Tavily** challenge.

| File | What it's for |
|---|---|
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Timed, beat-by-beat script (0:00–2:00) — voiceover + what's on screen |
| [EDITING_GUIDE.md](EDITING_GUIDE.md) | Free tools + concrete effect recipes (R1–R8) referenced from the script |
| `archify-diagram.html` | **Done.** Interactive architecture diagram generated with [Archify](https://github.com/tt-a1i/archify), validated against this repo's actual code at commit `636d205c`. Double-click to open in any browser — pan/zoom, click a node to see its source citation (file + line range), use Live/Still to toggle motion. This is the opening/closing visual in the script. |

Regenerate it after code changes with (from the repo root, Archify skill installed):
```
node <path-to-archify>/bin/archify.mjs finalize architecture .archify/architecture-fashnai-duediligence-20261018-131800/candidate.json hackathon-demo/archify-diagram.html --repo-root . --quality showcase --json
```
The source JSON lives in `.archify/architecture-fashnai-duediligence-20261018-131800/candidate.json` — edit node positions/labels there, not the HTML.

## Why this structure

The challenge is judged on: originality/creativity/tool use, **a judge clicking three citations at random and them holding up**, one complete demo run with no cuts around the hard part, and the trace showing the agent *deciding*, not following a script. The script is built around the `/due-diligence` page already in `frontend/app/due-diligence/`, which was built for exactly this: it shows verified/contested/unsupported claim cards with expandable sources + quotes, and a live agent trace panel (`DiligenceOrchestrator.py` → `FactCheckerAgent.py`, running on Nebius Token Factory with Tavily search).

## Before recording

Run the due-diligence flow end-to-end once off-camera to pick a product URL that actually produces a contested or unsupported claim — see the checklist at the bottom of DEMO_SCRIPT.md.
