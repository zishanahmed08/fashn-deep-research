from pydantic import BaseModel, Field
from typing import Literal, Optional


class CitedClaim(BaseModel):
    claim: str = Field(..., description="One falsifiable factual assertion, e.g. 'jacket costs €179 at thenorthface.com'")
    source_url: str = Field(..., description="URL of the page this claim comes from")
    quote: str = Field(..., description="Verbatim excerpt (≤80 words) from the source that supports the claim")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Tavily result score or LLM-estimated confidence")
    category: str = Field(..., description="One of: price, material, review, availability, spec, sustainability")


class CheckedClaim(BaseModel):
    claim: str
    source_url: str
    quote: str
    confidence: float
    category: str
    verdict: Literal["verified", "contested", "unsupported"]
    checker_note: str = Field(..., description="What the fact-checker found or failed to find")
    checker_source_url: Optional[str] = None
    checker_quote: Optional[str] = None


class TraceStep(BaseModel):
    agent: str
    action: str
    detail: str


class DueDiligenceReport(BaseModel):
    product_name: str
    product_url: str
    verdict: str = Field(..., description="Top-level verdict: 'Worth buying', 'Skip', or 'Conditional — see contested claims'")
    checked_claims: list[CheckedClaim]
    trace: list[TraceStep]
