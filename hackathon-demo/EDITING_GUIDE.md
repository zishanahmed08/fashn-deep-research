# Editing & Effects Guide

Everything here is doable for free in under an hour. No Adobe After Effects license needed — [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (free) covers all of it, [CapCut](https://www.capcut.com/) is faster if you're short on time. Recipe numbers match the cues in [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Recording setup

- **Screen capture:** OBS Studio (free). 1920×1080, 60fps if your machine handles it, 30fps is fine otherwise.
- **Cursor:** turn on "highlight clicks" (OBS has a filter, or use a tool like Cursor Highlighter) — judges need to see exactly where you clicked.
- **Audio:** record voiceover separately after capturing screens, not live — much easier to get clean narration and re-takes without re-recording the agent run.
- **Browser zoom:** 125–150% before recording so text reads on a 2-minute compressed export.

## Effect recipes

**R1 — Diagram zoom/pan.** In Resolve/CapCut, apply a slow Ken Burns zoom (scale 100%→115% over the clip) on the Archify diagram screenshot/recording. Add a soft drop-shadow or subtle glow behind diagram nodes if Archify's theme doesn't already have one — Settings → Effects → Glow, low intensity (10–15%), color-matched to your accent (your frontend already uses a Flash.co-style gradient — sample that hex).

**R2 — Lower third / badge glow.** Simple animated lower third: dark translucent bar (70% opacity black) sliding in from the left over 0.3s, text fades in 0.1s after. For verdict badges (green/yellow/red), add a 1–2px outer glow pulsing once (scale 100%→102%→100%, 0.4s) when the badge first appears on screen — draws the eye without being gimmicky.

**R3 — Quick-cut montage.** 1–2s clips, cut on a whip-pan or fast cross-dissolve (4–6 frames), not hard cuts — hard cuts feel choppy at this pace. Keep a consistent transition style across the whole montage so it doesn't look random.

**R4 — Network-call glow ping.** The moment the request fires, add a small animated dot/ping effect near the submit button or in a corner HUD — expanding translucent circle, 0.6s, fading out. Pairs well with a soft "whoosh" or UI-blip sound effect (free ones: Pixabay Sound Effects, zapsplat.com).

**R5 — Trace auto-scroll highlight.** If the trace panel scrolls slowly, you can speed-ramp it 1.5–2x in the edit except for the 2–3 seconds around the CONTESTED line — slow back to 1x right before it appears so it doesn't get lost. Add a thin highlight bar that tracks the newest trace line (a rectangle mask with slight motion blur).

**R6 — Contested stamp punch-in.** Red "CONTESTED" text, scale in from 130%→100% over 0.15s with a slight overshoot/bounce (ease: back-out), paired with a sharp, low "thud" sound hit. This is your one "special effect" moment — don't repeat the same punch for Verified claims, or it loses impact. Save the punch for the beat that matters.

**R7 — Cursor spotlight on click.** Darken everything outside a soft circular spotlight (radius ~150px) centered on the cursor for 0.5s after each click, then release. Most editors have a built-in "spotlight" or "vignette mask" tool; alternatively a radial gradient mask layer works in any NLE.

**R8 — End-card typewriter + fade.** Tagline text types on at ~40ms/character, logo fades in underneath (0.4s delay, 0.5s fade), background holds the Archify diagram slightly blurred (Gaussian blur, 8–10px) so the text pops. Fade whole card to black over the last 0.3s.

## Color grade

Your product's visual identity is a "Flash.co-inspired gradient" (per the README) — keep that language in the video. A quick grade: lift shadows very slightly blue/purple, keep whites clean (don't crush them — your UI's claim-card colors are the information, don't let a heavy grade muddy green/yellow/red). If using Resolve, the "Rec709 → Soft" LUT at 20–30% opacity is a safe, fast look.

## Music

Keep it instrumental, ducked to -15dB or lower whenever VO plays. Something with a subtle build around 1:00–1:35 (the trace/decision beat) works well structurally. Free sources: YouTube Audio Library, Pixabay Music — search "tech minimal build."

## Export

1080p, H.264, target under 150MB for easy upload to the hackathon platform. Double-check the platform's exact runtime/format limit before final export — the brief says "2-minute demo video," confirm whether that's a hard cutoff.

## What NOT to over-effect

The brief is explicit: *"the trace shows the agent making decisions, not following a script."* Don't effect-layer the 0:30–1:35 live-run segment so heavily that it starts looking staged or edited — judges are specifically watching for an unscripted, real trace. Save the heavier effects (R1, R3, R6, R8) for the bookend sections where you're not claiming "this is live."
