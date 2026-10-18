FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Playwright chromium for crawl4ai page extraction
RUN playwright install --with-deps chromium

COPY backend/ ./backend/

# SQLite dirs used by agno agents
RUN mkdir -p backend/tmp tmp

EXPOSE 8000

WORKDIR /app/backend
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
