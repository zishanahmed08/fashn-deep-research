import logging
import os
import uuid
from textwrap import dedent
from urllib.parse import urlparse

from agno.agent import Agent
from agno.models.nebius import Nebius
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, Optional

from schemas import CitedClaim, CheckedClaim

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
logger.addHandler(handler)

load_dotenv()


class SingleCheckResult(BaseModel):
    verdict: Literal["verified", "contested", "unsupported"]
    checker_note: str = Field(..., description="What the fact-checker found or failed to find")
    checker_source_url: Optional[str] = None
    checker_quote: Optional[str] = None


VERDICT_PROMPT = dedent("""\
    You are a sceptical product fact-checker. You receive ONE claim and web search results.
    Based on the search results, decide:
      - verified: an independent source (NOT the brand's own site) confirms the claim
      - contested: evidence contradicts or significantly differs from the claim
      - unsupported: only the brand's own pages appear, results are empty, or no independent corroboration

    CRITICAL OUTPUT FORMAT:
    Return a raw JSON object with exactly these top-level keys:
      "verdict": "verified", "contested", or "unsupported"
      "checker_note": 1-2 sentences on what you found
      "checker_source_url": URL of the independent source that confirmed/contested (null if unsupported)
      "checker_quote": verbatim excerpt ≤80 words (null if unsupported)

    Do NOT output search queries. Do NOT wrap in {"response": ...}.
    Start directly with { "verdict": ...
""")


def _verdict_agent() -> Agent:
    llm = Nebius(
        id="nvidia/Nemotron-3-Ultra-550b-a55b",
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=2048,
    )
    return Agent(
        name="FactChecker",
        model=llm,
        tools=[],  # No tools — search results are pre-fetched and passed in prompt
        description="Decides verdict for a product claim given pre-fetched search results.",
        instructions=[VERDICT_PROMPT],
        output_schema=SingleCheckResult,
        add_datetime_to_context=False,
        use_json_mode=True,
    )


def _tavily_search(query: str, brand_domain: str, max_results: int = 5) -> list[dict]:
    """Direct Tavily search without agno wrapper."""
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        resp = client.search(
            query=query,
            max_results=max_results,
            exclude_domains=[brand_domain] if brand_domain else [],
        )
        return resp.get("results", [])
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
        return []


def _check_one(claim: CitedClaim, brand_domain: str) -> CheckedClaim:
    # Build search query from the claim
    query = f"{claim.claim} independent review verification"

    results = _tavily_search(query, brand_domain)

    if not results:
        return CheckedClaim(
            claim=claim.claim,
            source_url=claim.source_url,
            quote=claim.quote,
            confidence=claim.confidence,
            category=claim.category,
            verdict="unsupported",
            checker_note="No independent search results found.",
        )

    # Format results for the verdict agent
    results_text = "\n".join(
        f"Source {i+1}: {r.get('url','')}\nTitle: {r.get('title','')}\nSnippet: {r.get('content','')[:300]}"
        for i, r in enumerate(results[:4])
    )

    payload = (
        f'Claim to verify: "{claim.claim}" (category: {claim.category})\n'
        f'Brand domain to exclude: {brand_domain}\n\n'
        f'Search results:\n{results_text}'
    )

    try:
        agent = _verdict_agent()
        response = agent.run(input=payload, session_id=str(uuid.uuid4()))
        result = SingleCheckResult.model_validate(response.content)
        return CheckedClaim(
            claim=claim.claim,
            source_url=claim.source_url,
            quote=claim.quote,
            confidence=claim.confidence,
            category=claim.category,
            verdict=result.verdict,
            checker_note=result.checker_note,
            checker_source_url=result.checker_source_url,
            checker_quote=result.checker_quote,
        )
    except Exception as e:
        logger.warning(f"Verdict agent failed for '{claim.claim[:60]}': {e}")
        return CheckedClaim(
            claim=claim.claim,
            source_url=claim.source_url,
            quote=claim.quote,
            confidence=claim.confidence,
            category=claim.category,
            verdict="unsupported",
            checker_note=f"Check failed: {str(e)[:120]}",
        )


def check_claims(claims: list[CitedClaim], brand_domain: str = "") -> list[CheckedClaim]:
    if not claims:
        return []

    # Cap at 8 claims, prioritise material/price over spec-only
    priority_order = ["price", "material", "sustainability", "review", "spec"]
    sorted_claims = sorted(claims, key=lambda c: priority_order.index(c.category) if c.category in priority_order else 99)
    batch = sorted_claims[:8]

    results = []
    for claim in batch:
        results.append(_check_one(claim, brand_domain))
    return results


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
