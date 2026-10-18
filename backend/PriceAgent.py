import logging
import uuid
import os
from textwrap import dedent
from typing import List
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


class ProductListing(BaseModel):
    website_name: str = Field(
        ..., description="Name of the fashion e-commerce website (e.g., ASOS, Zara, H&M, Nordstrom, etc.)")
    product_url: str = Field(
        ..., description="Direct URL to the product page on this website")
    price: str = Field(
        ..., description="Current price of the product including currency symbol (e.g., $49.99, €45.00)")
    availability: str = Field(
        ..., description="Product availability status (e.g., In Stock, Out of Stock, Limited Stock)")
    seller_info: str = Field(
        default="Not specified", description="Seller or vendor information if available")


class PriceComparisonResult(BaseModel):
    original_product_name: str = Field(
        ..., description="Name/title of the fashion product (apparel or shoes) being searched")
    original_product_url: str = Field(
        ..., description="The original product URL provided as input")
    product_listings: List[ProductListing] = Field(
        ..., description="List of product listings found across different e-commerce websites with their prices")
    search_summary: str = Field(
        ..., description="Brief summary of the search results and price range found")
    sources_checked: List[str] = Field(
        ..., description="List of all URLs checked during the research process")
    claims: List[CitedClaim] = Field(
        default_factory=list,
        description="Per-claim citations: each price or availability fact with source URL, verbatim quote, and confidence score")


# Two-stage pipeline: Nemotron on Nebius refuses to call tools when a
# response_format is set, so research runs schema-free and a second,
# tool-free call produces the schema-enforced JSON.
def price_research_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=8192,
    )
    return Agent(
        name="Fashion Price Research Agent",
        model=llm,
        tools=[TavilyTools(enable_search=True, enable_extract=True)],
        tool_call_limit=15,
        description=dedent("""\
        You are a fashion price research agent. You crawl a product page, search other
        retailers for the same item, verify matches, and write structured research notes.
        A separate agent formats your notes into the final JSON report.
        """),
        instructions=dedent("""\
        You will receive a product URL from a fashion e-commerce website. Research it:

        1. Identification
            - Crawl the provided product URL with extract_url_content and extract:
              product name, brand, style number/SKU, category, color, material,
              current price (with currency), available sizes.

        2. Search other retailers
            - Use web_search_using_tavily with queries like:
              * "[Brand] [Style Number] buy"
              * "[Brand] [Product Name] [Color] price"
              * "[Product Name] [Brand] fashion"

        3. Verify matches
            - Crawl 2-5 promising results with extract_url_content.
            - Confirm each is the EXACT same item (same brand, style, color, design).
            - Extract final customer price (incl. currency), availability, sizes, seller.
            - Exclude different colors/styles, other seasons, used/vintage items,
              unreliable websites, counterfeits.

        4. Final answer — plain structured notes (NOT JSON). Format:

            PRODUCT: <name> | <brand> | <style number> | <original price> | <original URL>
            LISTING: <website_name> | <product_url> | <price> | <availability> | <seller> | <verbatim quote ≤80 words from that page>
            (one LISTING line per verified listing)
            SOURCES_CHECKED: <url1>, <url2>, ...
            SUMMARY: <how many sites checked, price range found, notable differences; state explicitly if nothing was found>

        Rules:
            - Only include listings you actually crawled and verified.
            - Every LISTING line MUST contain a verbatim quote from that page.
            - Do not invent listings, prices, or quotes.
        """),
        add_datetime_to_context=True,
    )


def price_synthesis_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=16384,
    )
    return Agent(
        name="Fashion Price Synthesis Agent",
        model=llm,
        tools=[],
        description="Formats price research notes into the final JSON report.",
        instructions=dedent("""\
        Convert the researcher's notes into a PriceComparisonResult JSON.

        - Do NOT invent data. Use only what appears in the notes.
        - Map every LISTING line to one ProductListing entry.
        - For every listing, also add one CitedClaim per price/availability fact:
          claim: one falsifiable sentence, e.g. "Listed at €179.95 on thenorthface.com"
          source_url: the listing's URL
          quote: the verbatim quote from the notes (≤80 words)
          confidence: 0.9 for direct crawls
          category: "price" or "availability"
        - sources_checked: copy the SOURCES_CHECKED URLs from the notes.
        - search_summary: rewrite the SUMMARY from the notes.
        - If the notes say nothing was found, return an empty product_listings list
          and explain in search_summary. Never fabricate listings.

        CRITICAL OUTPUT FORMAT:
        Your final output MUST be a raw JSON object matching the PriceComparisonResult
        schema exactly, with "original_product_name", "original_product_url", etc. as
        top-level keys. Do NOT wrap it in {"response": ...} or any container.
        """),
        output_schema=PriceComparisonResult,
        add_datetime_to_context=False,
        use_json_mode=True,
    )


def compare_prices(product_url: str, max_retries: int = 3) -> RunOutput:
    research_payload = dedent(f"""
        product_url: {product_url}

        Research this fashion product across other e-commerce websites for price comparison.
    """)

    research = price_research_agent().run(
        input=research_payload, session_id=str(uuid.uuid4()))
    notes = research.content if isinstance(research.content, str) else str(research.content)

    synth_payload = dedent(f"""
        product_url: {product_url}

        RESEARCHER NOTES:
        {notes}
    """)

    agent = price_synthesis_agent()
    response = None
    for attempt in range(1, max_retries + 1):
        response = agent.run(input=synth_payload, session_id=str(uuid.uuid4()))
        try:
            _ = PriceComparisonResult.model_validate(response.content)
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
    result = compare_prices(test_url)
    print("\n" + "="*80)
    print("PRICE COMPARISON RESULTS")
    print("="*80)
    print(result.content)