"""
Orchestrates product due-diligence:
  1. Runs PriceAgent, ReviewAnalyzerAgent, ProductSpecsAgent in parallel
  2. Collects all CitedClaims from all three
  3. Runs FactCheckerAgent on the full claim list
  4. Returns a DueDiligenceReport with per-claim verdicts and a trace
"""
import asyncio
import logging
from urllib.parse import urlparse

from PriceAgent import compare_prices, PriceComparisonResult
from ReviewAnalyzerAgent import analyze_reviews, ReviewAnalysis
from ProductSpecsAgent import extract_specifications, ProductSpecification
from FactCheckerAgent import _check_one, extract_domain
from schemas import CitedClaim, CheckedClaim, TraceStep, DueDiligenceReport

logger = logging.getLogger(__name__)


def _derive_verdict(checked: list[CheckedClaim]) -> str:
    # Verdict derives from independently-checked claims only; facts (directly
    # observed, source-quoted) always verify and would otherwise inflate it.
    claims = [c for c in checked if c.kind == "claim"]
    if not claims:
        return "Conditional — details extracted and source-quoted; no independent claims to verify"
    contested = sum(1 for c in claims if c.verdict == "contested")
    unsupported = sum(1 for c in claims if c.verdict == "unsupported")
    verified = sum(1 for c in claims if c.verdict == "verified")
    total = len(claims)
    if contested >= 2 or unsupported / total > 0.5:
        return "Skip — multiple claims contested or unsupported"
    if contested == 1:
        return "Conditional — one contested claim, review before buying"
    if verified / total >= 0.6:
        return "Worth buying — majority of claims independently verified"
    return "Conditional — limited independent verification available"


async def run_due_diligence(product_url: str) -> DueDiligenceReport:
    trace: list[TraceStep] = []

    trace.append(TraceStep(
        agent="Planner",
        action="decompose",
        detail=f"Research questions: price comparison, material/spec verification, review authenticity for {product_url}",
    ))

    # Run three researchers in parallel
    trace.append(TraceStep(agent="Planner", action="dispatch", detail="Running PriceAgent, ReviewAgent, SpecsAgent in parallel"))

    price_task = asyncio.to_thread(compare_prices, product_url)
    review_task = asyncio.to_thread(analyze_reviews, product_url)
    specs_task = asyncio.to_thread(extract_specifications, product_url)

    results = await asyncio.gather(price_task, review_task, specs_task, return_exceptions=True)

    all_claims: list[CitedClaim] = []
    product_name = "Unknown product"
    brand_domain = extract_domain(product_url)

    # Price
    if isinstance(results[0], Exception):
        trace.append(TraceStep(agent="PriceAgent", action="error", detail=str(results[0])[:200]))
    elif isinstance(results[0].content, str):
        trace.append(TraceStep(agent="PriceAgent", action="agent_error", detail=f"returned error string: {results[0].content[:150]}"))
    else:
        try:
            price_data: PriceComparisonResult = results[0].content
            product_name = price_data.original_product_name
            all_claims.extend(price_data.claims)
            trace.append(TraceStep(
                agent="PriceAgent",
                action="complete",
                detail=f"Found {len(price_data.product_listings)} listings, {len(price_data.claims)} cited claims",
            ))
        except Exception as e:
            trace.append(TraceStep(agent="PriceAgent", action="parse_error", detail=str(e)[:200]))

    # Reviews
    if isinstance(results[1], Exception):
        trace.append(TraceStep(agent="ReviewAgent", action="error", detail=str(results[1])[:200]))
    elif isinstance(results[1].content, str):
        trace.append(TraceStep(agent="ReviewAgent", action="agent_error", detail=f"returned error string: {results[1].content[:150]}"))
    else:
        try:
            review_data: ReviewAnalysis = results[1].content
            all_claims.extend(review_data.claims)
            trace.append(TraceStep(
                agent="ReviewAgent",
                action="complete",
                detail=f"Rating {review_data.overall_rating}/5 from {review_data.total_reviews} reviews, {len(review_data.claims)} cited claims",
            ))
        except Exception as e:
            trace.append(TraceStep(agent="ReviewAgent", action="parse_error", detail=str(e)[:200]))

    # Specs
    if isinstance(results[2], Exception):
        trace.append(TraceStep(agent="SpecsAgent", action="error", detail=str(results[2])[:200]))
    elif isinstance(results[2].content, str):
        trace.append(TraceStep(agent="SpecsAgent", action="agent_error", detail=f"returned error string: {results[2].content[:150]}"))
    else:
        try:
            specs_data: ProductSpecification = results[2].content
            if product_name == "Unknown product":
                product_name = specs_data.product_name
            all_claims.extend(specs_data.claims)
            trace.append(TraceStep(
                agent="SpecsAgent",
                action="complete",
                detail=f"Extracted {len(specs_data.claims)} cited claims (material, spec, sustainability)",
            ))
        except Exception as e:
            trace.append(TraceStep(agent="SpecsAgent", action="parse_error", detail=str(e)[:200]))

    # Cap at 8 items. Claims first (they need independent verification); reserve the
# last 2 slots for facts so the report shows source-quoted facts too (they cost
# no search — self-verified from the quote).
    priority_order = ["material", "sustainability", "review", "price", "spec"]
    claims_sorted = sorted(
        (c for c in all_claims if c.kind == "claim"),
        key=lambda c: priority_order.index(c.category) if c.category in priority_order else 99,
    )
    facts_sorted = sorted(
        (c for c in all_claims if c.kind == "fact"),
        key=lambda c: priority_order.index(c.category) if c.category in priority_order else 99,
    )
    batch = claims_sorted[:6] + facts_sorted[:2]
    batch = batch[:8]

    n_facts = sum(1 for c in all_claims if c.kind == "fact")
    n_claims = len(all_claims) - n_facts

    trace.append(TraceStep(
        agent="FactChecker",
        action="start",
        detail=f"{n_claims} claims to verify independently ({n_facts} facts self-verified from source quotes), excluding brand domain: {brand_domain}",
    ))

    # Run each claim check in its own thread — parallel fact-checking
    check_tasks = [asyncio.to_thread(_check_one, claim, brand_domain) for claim in batch]
    checked = list(await asyncio.gather(*check_tasks, return_exceptions=False))

    contested = [c for c in checked if c.verdict == "contested"]
    verified_count = sum(1 for c in checked if c.verdict == "verified")
    unsupported = [c for c in checked if c.verdict == "unsupported" and c.kind == "claim"]

    trace.append(TraceStep(
        agent="FactChecker",
        action="complete",
        detail=f"verified={verified_count}, contested={len(contested)}, unsupported={len(unsupported)} (claims only; facts self-verified)",
    ))
    for c in contested:
        trace.append(TraceStep(
            agent="FactChecker",
            action="challenge",
            detail=f'CONTESTED: "{c.claim[:80]}" — {c.checker_note}',
        ))

    verdict = _derive_verdict(checked)

    return DueDiligenceReport(
        product_name=product_name,
        product_url=product_url,
        verdict=verdict,
        checked_claims=checked,
        trace=trace,
    )
