# FashnAI

AI-powered fashion product due-diligence system using a multi-agent architecture built on Nebius Token Factory. Specialized in apparel and footwear analysis with per-claim citations and independent fact-checking.

## Live Demo

- **Frontend**: https://fashn-deep-research.vercel.app/
- **Backend API**: https://port8000-zq4qjnhgksz8t94.tunnel.applications.eu-west2.nebius.cloud

## Features

- **Fashion Price Comparison Agent**: Finds the same fashion product across multiple e-commerce websites and compares prices with per-claim citations
- **Review Analysis Agent**: Analyzes customer reviews, sentiment, pros/cons with source quotes and confidence scores
- **Product Specifications Agent**: Extracts detailed specifications including materials, sizes, care instructions, and sustainability claims
- **FactChecker Agent**: Independently verifies every claim against non-brand sources using Tavily; returns verified/contested/unsupported verdicts
- **Due Diligence Endpoint**: Runs all three research agents in parallel, then routes all claims through the fact-checker for a full `DueDiligenceReport`
- **Virtual Try-On AI**: AI-powered virtual try-on providing personalized fit analysis and size recommendations

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm (for frontend)
- Nebius API key (Token Factory)
- Tavily API key (web search + extraction)

## Installation

### 1. Install uv

If you don't have `uv` installed, install it using:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd fashnai
```

### 3. Set Up Environment

Create a `.env` file in the project root with the following variables:

```env
NEBIUS_API_KEY=your-nebius-api-key
TAVILY_API_KEY=your-tavily-api-key
```

**Required API Keys:**
- **Nebius API**: Get your API key from [Nebius AI Studio](https://studio.nebius.ai/)
- **Tavily API**: Get your API key from [tavily.com](https://tavily.com)

### 4. Install Dependencies

**Backend Dependencies:**
Use `uv sync` to create a virtual environment and install all dependencies:

```bash
uv sync
```

This command will:
- Create a virtual environment in `.venv/`
- Install all dependencies specified in `pyproject.toml`
- Lock dependencies for reproducibility

**Frontend Dependencies:**
```bash
cd frontend
npm install
cd ..
```

### 5. Activate Virtual Environment

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### 6. Setup crawl4ai to install browser tools
```bash
source .venv/bin/activate
crawl4ai-setup
```

### 7. To Enable debugging
```bash
export AGNO_DEBUG=true
```

## Usage

### Quick Start - Run Everything

To start the full application (backend + frontend):

```bash
./start.sh
```

This will start:
- **Backend (Agents)**: http://localhost:8000
- **Frontend**: http://localhost:3000

To stop all services, press `Ctrl+C`.

View logs:
```bash
# Backend logs
tail -f backend_log.txt

# Frontend logs
tail -f frontend_log.txt
```

### Manual Start

**Start Backend API Server:**
```bash
uv run backend/api.py
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Alternative - AgentOS Playground (for testing agents directly):**
```bash
uv run backend/playground.py
```
Note: The playground is for agent testing with AgentOS UI, not for the web frontend.

### Using the Web Application

1. **Search for a Product**: Paste any fashion product URL on the home page
2. **View Analysis**: See price comparisons, reviews, and specifications
3. **Try Virtual Try-On**: Click the "Try Virtual Try-On" button on any product page
4. **Get Personalized Insights**: Enter your size, height, and body type for AI-powered fit analysis and styling recommendations

### Fashion Price Comparison Agent

Compare prices for fashion products (apparel, shoes, accessories) across multiple fashion e-commerce websites:

```python
from backend.PriceAgent import compare_prices

# Example with a fashion product URL
result = compare_prices("https://www.asos.com/product/example-dress")
print(result.content)
```

### Virtual Try-On Agent

Get AI-powered fit analysis and styling recommendations:

```python
from backend.VirtualTryOnAgent import virtual_tryon

# Example with user characteristics
result = virtual_tryon(
    product_url="https://en.zalando.de/bershka-baby-gifts-black-bej22s0jx-q11.html",
    user_size="M",
    user_height="5'9\"",
    user_body_type="athletic"
)
print(result.content)
```

### AgentOS Integration
- Rename .env-template to .env and set the API Keys
- Is necessary to create an account with agno to use the playground, even locally
- Connect to AgentOS UI for a readymade interface to interact with the agent as mentioned here https://docs.agno.com/introduction

## Project Structure

```
fashnai/
├── backend/
│   ├── PriceAgent.py            # Price comparison agent (Nemotron)
│   ├── ReviewAnalyzerAgent.py   # Review analysis agent (Nemotron)
│   ├── ProductSpecsAgent.py     # Specs extraction agent (Nemotron)
│   ├── FactCheckerAgent.py      # Independent fact-checker (Nemotron)
│   ├── DiligenceOrchestrator.py # Parallel orchestration + due-diligence report
│   ├── VirtualTryOnAgent.py     # Virtual try-on (MiniCPM-V vision model)
│   ├── schemas.py               # Shared Pydantic types (CitedClaim, CheckedClaim, etc.)
│   ├── cache/                   # Pre-cached demo responses (baked into Docker image)
│   └── api.py                   # FastAPI server
├── frontend/                    # Next.js app (deployed on Vercel)
│   ├── app/
│   │   ├── page.tsx            # Home page
│   │   ├── product/            # Product analysis page (3 parallel agents)
│   │   ├── due-diligence/      # Due diligence page with per-claim verdicts
│   │   └── layout.tsx          # App layout
│   └── package.json
├── Dockerfile                   # Backend image (deployed on Nebius Serverless AI)
├── .env                         # Environment variables (committed with placeholder values)
└── pyproject.toml               # Backend dependencies
```

## Dependencies

**Backend:**
- **agno**: Multi-agent framework
- **nebius**: Nebius Token Factory model integration (Nemotron, MiniCPM-V)
- **crawl4ai**: Web scraping and crawling
- **tavily-python**: Web search and extraction
- **fastapi**: REST API framework
- **pydantic**: Data validation and schema definition

**Frontend:**
- **Next.js 14**: React framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

See `pyproject.toml` for the complete list.

## Development

### Adding New Dependencies

```bash
# Add a new package
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update a specific package
uv add package-name --upgrade
```

### Running Tests

```bash
# Activate environment first
source .venv/bin/activate

# Run your tests
python -m pytest
```

## API Configuration

**API Key Usage:**
- `NEBIUS_API_KEY`: All agents run on Nebius Token Factory (`nvidia/nemotron-3-super-120b-a12b` for research agents and fact-checker, `openbmb/MiniCPM-V-4_5` for virtual try-on)
- `TAVILY_API_KEY`: Web search and page extraction used by all research agents

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```bash
# Remove existing environment
rm -rf .venv

# Recreate with uv sync
uv sync
```

