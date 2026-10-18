import logging
import os
import uuid
from textwrap import dedent
from urllib.parse import urlparse

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.nebius import Nebius
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from schemas import CitedClaim, CheckedClaim

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
logger.addHandler(handler)

load_dotenv()

llm = Nebius(
    id="nvidia/nemotron-3-super-120b-a12b",  # confirmed: tool calling + JSON output
    api_key=os.getenv("NEBIUS_API_KEY"),
    max_tokens=8192,
)


class FactCheckBatch(BaseModel):
    results: list[CheckedClaim] = Field(..., description="One CheckedClaim per input claim, same order")


SYSTEM_PROMPT = dedent("""\
    You are a sceptical fact-checker for a product due-diligence report.
    You receive a list of claims, each with a source URL.

    For each claim:
    1. Formulate a skeptical search query designed to surface contradicting or independent evidence.
       NEVER include the brand's own domain in your search.
    2. Call web_search_using_tavily with that query.
    3. Apply these verdict rules:
       - verified: an independent source (not the brand's site) confirms the claim with a quotable excerpt
       - contested: you found evidence that contradicts or significantly differs from the claim
       - unsupported: only the brand's own pages appear, results are empty, or no independent corroboration exists
    4. For price claims: also check whether the item is currently in stock at the stated price.
       If out of stock or price differs, mark contested.
    5. For material claims (e.g. "100% organic cotton"): if only brand marketing copy exists, mark unsupported.
       Look for lab tests, third-party reviews, or retailer spec sheets.
    6. For rating claims: cross-check on a second platform (Trustpilot, Google, Reddit).
       If the rating on another platform differs by more than 0.5 stars, mark contested.

    Return a JSON object with a single key "results" containing an array of CheckedClaim objects,
    one per input claim, in the same order. Do not add or remove claims.
    For checker_source_url and checker_quote: populate only when verdict is verified or contested.
""")


def fact_checker_agent() -> Agent:
    return Agent(
        name="FactChecker",
        model=llm,
        tools=[TavilyTools(enable_search=True, enable_extract=True)],
        tool_call_limit=30,
        description="Verifies product claims against independent sources using Tavily search.",
        instructions=[SYSTEM_PROMPT],
        output_schema=FactCheckBatch,
        db=SqliteDb(session_table="fact_checker_agent", db_file="tmp/agents.db"),
        add_datetime_to_context=True,
        use_json_mode=True,
    )


def check_claims(claims: list[CitedClaim], brand_domain: str = "") -> list[CheckedClaim]:
    if not claims:
        return []

    claims_json = "\n".join(
        f'{i+1}. claim="{c.claim}" source_url="{c.source_url}" category="{c.category}" quote="{c.quote[:120]}"'
        for i, c in enumerate(claims)
    )

    domain_note = f"\nExclude domain: {brand_domain}" if brand_domain else ""
    payload = f"Verify these claims. Return one CheckedClaim per claim.{domain_note}\n\n{claims_json}"

    agent = fact_checker_agent()
    response = agent.run(input=payload, session_id=str(uuid.uuid4()))

    try:
        batch = FactCheckBatch.model_validate(response.content)
        return batch.results
    except Exception as e:
        logger.error(f"FactChecker validation failed: {e}")
        # Fallback: mark all as unsupported
        return [
            CheckedClaim(
                claim=c.claim,
                source_url=c.source_url,
                quote=c.quote,
                confidence=c.confidence,
                category=c.category,
                verdict="unsupported",
                checker_note=f"Fact-check failed: {str(e)[:120]}",
            )
            for c in claims
        ]


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
