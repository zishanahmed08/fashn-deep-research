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
    if not checked:
        return "Insufficient data"
    contested = sum(1 for c in checked if c.verdict == "contested")
    unsupported = sum(1 for c in checked if c.verdict == "unsupported")
    verified = sum(1 for c in checked if c.verdict == "verified")
    total = len(checked)
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

    # Prioritise claims: material/price first, cap at 8
    priority_order = ["price", "material", "sustainability", "review", "spec"]
    sorted_claims = sorted(all_claims, key=lambda c: priority_order.index(c.category) if c.category in priority_order else 99)
    batch = sorted_claims[:8]

    trace.append(TraceStep(
        agent="FactChecker",
        action="start",
        detail=f"Verifying {len(batch)} claims in parallel, excluding brand domain: {brand_domain}",
    ))

    # Run each claim check in its own thread — parallel fact-checking
    check_tasks = [asyncio.to_thread(_check_one, claim, brand_domain) for claim in batch]
    checked = list(await asyncio.gather(*check_tasks, return_exceptions=False))

    contested = [c for c in checked if c.verdict == "contested"]
    unsupported = [c for c in checked if c.verdict == "unsupported"]
    verified_count = sum(1 for c in checked if c.verdict == "verified")

    trace.append(TraceStep(
        agent="FactChecker",
        action="complete",
        detail=f"verified={verified_count}, contested={len(contested)}, unsupported={len(unsupported)}",
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
