import logging
import uuid
import os
from textwrap import dedent
from typing import List, Dict
from agno.agent import Agent, RunOutput
from agno.models.nebius import Nebius
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from schemas import CitedClaim

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(handler)

load_dotenv()


class SentimentScore(BaseModel):
    positive: int = Field(..., description="Positive sentiment percentage (0-100)")
    negative: int = Field(..., description="Negative sentiment percentage (0-100)")
    neutral: int = Field(..., description="Neutral sentiment percentage (0-100)")


class ReviewAnalysis(BaseModel):
    overall_rating: float = Field(..., description="Overall product rating (0-5 stars)")
    total_reviews: int = Field(..., description="Total number of reviews analyzed")
    sentiment: SentimentScore = Field(..., description="Sentiment distribution across reviews")
    pros: List[str] = Field(..., description="List of 3-5 main pros mentioned in reviews")
    cons: List[str] = Field(..., description="List of 3-5 main cons mentioned in reviews")
    common_themes: List[str] = Field(..., description="Common themes or topics mentioned in reviews")
    summary: str = Field(..., description="2-3 sentence summary of overall customer feedback")
    verified_purchase_percentage: int = Field(default=0, description="Percentage of verified purchase reviews")
    sources_analyzed: List[str] = Field(..., description="URLs of review sources analyzed")
    claims: List[CitedClaim] = Field(
        default_factory=list,
        description="Per-claim citations: each rating, sentiment fact, or key review finding with source URL, verbatim quote, and confidence")


# Two-stage pipeline: Nemotron on Nebius refuses to call tools when a
# response_format is set, so research runs schema-free and a second,
# tool-free call produces the schema-enforced JSON.
def review_research_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=8192,
    )
    return Agent(
        name="Fashion Review Research Agent",
        model=llm,
        tools=[TavilyTools(enable_search=True, enable_extract=True)],
        tool_call_limit=15,
        description=dedent("""\
        You are a fashion review research agent. You find customer reviews for a product
        across multiple sources and write structured research notes.
        A separate agent formats your notes into the final JSON report.
        """),
        instructions=dedent("""\
        You will receive a product URL or product name. Research it:

        1. Review discovery
            - Crawl the provided product URL with extract_url_content to find on-page reviews.
            - Search for additional review sources with web_search_using_tavily:
              review sites, fashion forums, retailer listings of the same product.
            - Collect as many substantive reviews as available.

        2. Analysis
            - For each source, note the rating shown and roughly how many reviews.
            - Identify recurring pros: quality, fit/sizing, comfort, style, value.
            - Identify recurring cons: quality issues, sizing problems, durability, value.
            - Note common themes that appear across multiple reviews.
            - Note verified-purchase indicators if visible.

        3. Final answer — plain structured notes (NOT JSON). Format:

            PRODUCT: <name> | <product URL>
            SOURCE: <url> | rating shown: <x.x/5 or n/a> | approx reviews: <n or unknown> | verified purchase info | <verbatim quote ≤80 words>
            (one SOURCE line per review source you actually visited)
            PROS: <pro 1>; <pro 2>; ... (each backed by quotes above)
            CONS: <con 1>; <con 2>; ...
            THEMES: <theme 1>; <theme 2>; ...
            SUMMARY: <2-3 sentences; state explicitly if insufficient reviews were found>

        Rules:
            - Only report ratings and reviews you actually saw on a page you visited.
            - Every SOURCE line MUST contain a verbatim quote from that page.
            - Do not invent ratings, counts, or quotes. If a source has no reviews, say so.
            - If you find no review data at all, write exactly that in SUMMARY.
        """),
        add_datetime_to_context=True,
    )


def review_synthesis_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=16384,
    )
    return Agent(
        name="Fashion Review Synthesis Agent",
        model=llm,
        tools=[],
        description="Formats review research notes into the final JSON report.",
        instructions=dedent("""\
        Convert the researcher's notes into a ReviewAnalysis JSON.

        - Do NOT invent data. Use only what appears in the notes.
        - overall_rating / total_reviews: only from ratings actually shown in SOURCE lines.
          If the notes contain no ratings, use 0.0 and 0.
        - pros / cons / common_themes: from the PROS, CONS, THEMES note lines.
        - sources_analyzed: the URLs from every SOURCE line.
        - For every rating or key finding, add a CitedClaim:
          claim: one falsifiable sentence, e.g. "4.3/5 stars on Trustpilot (127 reviews)"
          source_url: that source's URL
          quote: the verbatim quote from the notes (≤80 words)
          confidence: 0.9 for direct crawls
          category: "review"
        - summary: rewrite the SUMMARY from the notes, including any explicit
          "insufficient reviews" statement.

        CRITICAL OUTPUT FORMAT:
        Your final output MUST be a raw JSON object matching the ReviewAnalysis schema
        exactly, with "overall_rating", "total_reviews", etc. as top-level keys.
        Do NOT wrap it in {"response": ...} or any container.
        """),
        output_schema=ReviewAnalysis,
        add_datetime_to_context=False,
        use_json_mode=True,
    )


def analyze_reviews(product_url: str, max_retries: int = 3) -> RunOutput:
    research_payload = dedent(f"""
        product_url: {product_url}

        Research customer reviews for this fashion product from multiple sources.
    """)

    research = review_research_agent().run(
        input=research_payload, session_id=str(uuid.uuid4()))
    notes = research.content if isinstance(research.content, str) else str(research.content)

    synth_payload = dedent(f"""
        product_url: {product_url}

        RESEARCHER NOTES:
        {notes}
    """)

    agent = review_synthesis_agent()
    response = None
    for attempt in range(1, max_retries + 1):
        response = agent.run(input=synth_payload, session_id=str(uuid.uuid4()))
        try:
            _ = ReviewAnalysis.model_validate(response.content)
            return response
        except Exception as e:
            if attempt < max_retries:
                logger.error(f"Synthesis attempt {attempt} failed: {e}. Retrying...")
                continue
            logger.error(f"All {max_retries} synthesis attempts failed.")
            return response
    return response


if __name__ == "__main__":
    test_url = "https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html"
    result = analyze_reviews(test_url)
    print("\n" + "="*80)
    print("REVIEW ANALYSIS RESULTS")
    print("="*80)
    print(result.content)