import logging
import uuid
import os
from textwrap import dedent
from typing import List, Optional, Dict
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


class ProductSpecification(BaseModel):
    product_name: str = Field(..., description="Full product name/title")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category (e.g., Sneakers, Dress, Jacket)")
    color: str = Field(..., description="Color or colorway")
    material: str = Field(..., description="Primary material or fabric composition")
    sizes_available: List[str] = Field(..., description="List of available sizes")
    care_instructions: Optional[str] = Field(None, description="Care and washing instructions")
    features: List[str] = Field(..., description="Key product features (3-7 items)")
    dimensions: Optional[Dict[str, str]] = Field(None, description="Product dimensions if applicable")
    weight: Optional[str] = Field(None, description="Product weight if applicable")
    style_number: Optional[str] = Field(None, description="Style number, SKU, or product code")
    country_of_origin: Optional[str] = Field(None, description="Manufacturing country")
    sustainability: Optional[str] = Field(None, description="Sustainability or eco-friendly information")
    fit_type: Optional[str] = Field(None, description="Fit type (e.g., Regular Fit, Slim Fit, Oversized)")
    additional_specs: Dict[str, str] = Field(default_factory=dict, description="Any additional specifications")
    sources: List[str] = Field(..., description="URLs where specifications were found")
    claims: List[CitedClaim] = Field(
        default_factory=list,
        description="Per-claim citations: each material, feature, or spec fact with source URL, verbatim quote, and confidence")


# Two-stage pipeline: Nemotron on Nebius refuses to call tools when a
# response_format is set, so research runs schema-free and a second,
# tool-free call produces the schema-enforced JSON.
def specs_research_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=8192,
    )
    return Agent(
        name="Fashion Product Specs Research Agent",
        model=llm,
        tools=[TavilyTools(enable_search=True, enable_extract=True)],
        tool_call_limit=15,
        description=dedent("""\
        You are a fashion product specifications research agent. You crawl product pages
        and write structured research notes on materials, sizes, care, and features.
        A separate agent formats your notes into the final JSON report.
        """),
        instructions=dedent("""\
        You will receive a product URL. Research it:

        1. Basic information (crawl the product URL with extract_url_content)
            - Product name/title, brand, category, color/colorway, style number/SKU.

        2. Material and construction
            - Primary materials (e.g., "100% Cotton", "100% recycled polyester"),
              fabric type, treatments/finishes, stitching, closure type, lining.

        3. Sizing
            - Available sizes, fit type (Regular/Slim/Oversized), size chart notes.

        4. Care instructions
            - Washing, drying, ironing, special care notes.

        5. Features (3-7)
            - Functional (pockets, straps), design, performance (waterproof,
              breathable), comfort.

        6. Additional specs
            - Dimensions, weight, country of origin, sustainability info,
              certifications (OEKO-TEX, Fair Trade, etc.).

        7. Gap filling (only if the product page is missing specs)
            - Search "[Brand] [Product] specifications", "[Product] material composition",
              "[Product] care instructions" and crawl official/retailer pages.

        8. Final answer — plain structured notes (NOT JSON). Format:

            PRODUCT: <name> | <brand> | <category> | <color> | <style number> | <original URL>
            FACT: <category: material|spec|sustainability> | <the fact, specific not generic> | <verbatim quote ≤80 words> | <source URL>
            (one FACT line per extracted specification)
            SOURCES: <url1>, <url2>, ...

        Rules:
            - Be specific: "100% Organic Cotton" not just "Cotton".
            - Only include facts you actually saw on a page you visited.
            - Every FACT line MUST contain a verbatim quote and its source URL.
            - If a spec was not found anywhere, omit it — do not guess.
        """),
        add_datetime_to_context=True,
    )


def specs_synthesis_agent() -> Agent:
    llm = Nebius(
        id='nvidia/Nemotron-3-Ultra-550b-a55b',
        api_key=os.getenv("NEBIUS_API_KEY"),
        max_tokens=16384,
    )
    return Agent(
        name="Fashion Product Specs Synthesis Agent",
        model=llm,
        tools=[],
        description="Formats product spec research notes into the final JSON report.",
        instructions=dedent("""\
        Convert the researcher's notes into a ProductSpecification JSON.

        - Do NOT invent data. Use only what appears in the notes.
        - Map PRODUCT line to product_name, brand, category, color, style_number.
        - Map FACT lines to material, features, sizes_available, care_instructions,
          sustainability, fit_type, etc.
        - For every FACT line, add a CitedClaim:
          claim: one falsifiable sentence restating the fact
          source_url: the FACT's source URL
          quote: the verbatim quote from the notes (≤80 words)
          confidence: 0.9 for direct product page crawls
          category: the FACT's category ("material", "spec", or "sustainability")
          kind: "fact" for directly observed page attributes (product name, brand,
            category, color, style number, listed sizes, care instructions) — these
            are self-verified by the source quote. "claim" for assertions about the
            world that deserve independent corroboration (material composition,
            sustainability certifications, performance numbers like waterproof
            ratings or insulation weight).
        - sources: the SOURCES URLs from the notes.
        - If a spec is absent from the notes, use null (optional fields) or an empty
          list — never fabricate.
        - Be compact: quotes ≤40 words, omit null optional fields, keep
          additional_specs to the 5 most useful entries. Output budget matters —
          a truncated JSON is a failed response.

        CRITICAL OUTPUT FORMAT:
        Your final output MUST be a raw JSON object matching the ProductSpecification
        schema exactly, with "product_name", "brand", "category" etc. as top-level keys.
        Do NOT wrap it in {"response": ...} or any container.
        """),
        output_schema=ProductSpecification,
        add_datetime_to_context=False,
        use_json_mode=True,
    )


def extract_specifications(product_url: str, max_retries: int = 3) -> RunOutput:
    research_payload = dedent(f"""
        product_url: {product_url}

        Research comprehensive product specifications for this fashion product.
    """)

    research = specs_research_agent().run(
        input=research_payload, session_id=str(uuid.uuid4()))
    notes = research.content if isinstance(research.content, str) else str(research.content)

    synth_payload = dedent(f"""
        product_url: {product_url}

        RESEARCHER NOTES:
        {notes}
    """)

    agent = specs_synthesis_agent()
    response = None
    for attempt in range(1, max_retries + 1):
        response = agent.run(input=synth_payload, session_id=str(uuid.uuid4()))
        try:
            _ = ProductSpecification.model_validate(response.content)
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
    result = extract_specifications(test_url)
    print("\n" + "="*80)
    print("PRODUCT SPECIFICATIONS")
    print("="*80)
    print(result.content)