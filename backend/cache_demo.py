"""
Run this once before building the Docker image to warm the demo cache.
Saves the due-diligence result for a URL to backend/cache/demo_responses.json.

Usage:
    uv run backend/cache_demo.py "https://www.thenorthface.com/de-de/p/..."
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from DiligenceOrchestrator import run_due_diligence

CACHE_FILE = Path(__file__).parent / "cache" / "demo_responses.json"

async def main(url: str) -> None:
    print(f"Running due-diligence for: {url}")
    report = await run_due_diligence(url)
    key = hashlib.md5(url.strip().encode()).hexdigest()
    cache: dict = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    cache[key] = report.model_dump()
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    print(f"Saved to {CACHE_FILE} under key {key}")
    print(f"Verdict: {report.verdict}")
    print(f"Claims: {len(report.checked_claims)} ({sum(1 for c in report.checked_claims if c.verdict == 'verified')} verified)")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://www.thenorthface.com/de-de/p/herren-211701/"
        "limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M"
    )
    asyncio.run(main(url))
