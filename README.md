# BlackRock Retirement Savings API

Production-grade API for automated retirement savings through expense-based micro-investments. Built for the BlackRock Hackathon Challenge.

## Architecture

```
backend/
├── main.py                         # FastAPI app + middleware + SPA serving
├── config.py                       # All constants & env settings
├── core/
│   ├── logging.py                  # Structured JSON logging
│   ├── security.py                 # API key authentication
│   └── datetime_utils.py           # Date parsing & period checks
└── api/v1/
    ├── router.py                   # V1 router aggregator
    ├── routers/                    # Thin HTTP layer (stateless)
    │   ├── transactions.py         # :parse, :validator, :filter
    │   ├── returns.py              # :nps, :index
    │   └── performance.py          # /performance
    ├── models/                     # Pydantic schemas (data governance)
    │   ├── transaction.py
    │   ├── period.py
    │   ├── requests.py
    │   └── responses.py
    └── services/                   # Pure business logic
        ├── parser_service.py       # Ceiling/remanent calculation
        ├── validator_service.py    # Negative amount & duplicate checks
        ├── period_service.py       # q/p/k period application
        ├── returns_service.py      # Compound interest & inflation
        ├── tax_service.py          # Tax slabs & NPS deduction
        └── performance_service.py  # System metrics
frontend/                           # React playground (served from same origin)
test/                               # Unit + integration tests
```

## Tech Stack

| Component  | Choice       | Why                                             |
| ---------- | ------------ | ----------------------------------------------- |
| Language   | Python 3.12  | Simple, clear, fast enough                      |
| Framework  | FastAPI      | Async, auto-OpenAPI docs, Pydantic integration  |
| Server     | uvicorn      | Fastest Python ASGI server (uvloop + httptools) |
| Validation | Pydantic v2  | Rust-backed, type-safe schemas                  |
| Frontend   | React + Vite | Fast builds, same-origin serving (no CORS)      |
| Container  | Alpine Linux | ~50MB base, security-hardened                   |
| Testing    | pytest       | Industry standard, clean fixtures               |

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 20+ (for frontend build)
- Docker (for containerized deployment)

### Local Development

```bash
# 1. Install dependencies
uv sync

# 2. Build frontend (optional — API works without it)
cd frontend && npm install && npm run build && cd ..

# 3. Start the server
uv run uvicorn backend.main:app --host 0.0.0.0 --port 5477 --reload
```

The API is now available at **http://localhost:5477**

- API Docs (Swagger): http://localhost:5477/docs
- Frontend Playground: http://localhost:5477/
- Performance: http://localhost:5477/blackrock/challenge/v1/performance

### Docker

```bash
# Build the image
docker build -t blk-hacking-ind-tejas-nakka .

# Run the container
docker run -d -p 5477:5477 blk-hacking-ind-tejas-nakka
```

Or with Docker Compose:

```bash
docker compose up -d
```

## API Endpoints

All endpoints are prefixed with `/blackrock/challenge/v1`.

### 1. Transaction Parser

`POST /blackrock/challenge/v1/transactions:parse`

Parses expenses into transactions with ceiling (next multiple of 100) and remanent.

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/transactions:parse \
  -H "Content-Type: application/json" \
  -d '[{"date":"2023-10-12 20:15:30","amount":250}]'
```

### 2. Transaction Validator

`POST /blackrock/challenge/v1/transactions:validator`

Validates transactions — rejects negative amounts and duplicates.

### 3. Transaction Filter

`POST /blackrock/challenge/v1/transactions:filter`

Full pipeline: parse → validate → apply q/p period rules → check k membership.

### 4. Returns Calculator

- `POST /blackrock/challenge/v1/returns:nps` — NPS (7.11% annual, with tax benefit)
- `POST /blackrock/challenge/v1/returns:index` — Index Fund / NIFTY 50 (14.49% annual)

### 5. Performance Report

`GET /blackrock/challenge/v1/performance`

Returns server uptime, memory usage, and thread count.

## Testing

```bash
# Run all tests (58 tests)
uv run pytest test/ -v
```

Tests are in the `test/` directory and include:

- **Unit tests**: parser, validator, periods, tax, returns
- **Integration tests**: full endpoint round-trips with spec examples

## Design Principles

| Principle           | Implementation                                            |
| ------------------- | --------------------------------------------------------- |
| **Clarity**         | Descriptive naming, type hints, Pydantic docs             |
| **Modular**         | Router → Service → Utils layers, single responsibility    |
| **Stateless**       | No DB, no sessions — all data in request/response         |
| **Extensible**      | Versioned API (v1/v2), new investment vehicles = new rate |
| **Data Governance** | Pydantic enforces schemas, invalid input rejected         |
| **Observable**      | Structured JSON logging, performance endpoint             |
| **Secure**          | Optional API key auth, input validation                   |

## Security

Set the `API_KEY` environment variable to enable authentication:

```bash
docker run -d -p 5477:5477 -e API_KEY=your-key blk-hacking-ind-tejas-nakka
```

Then include `X-API-Key: your-key` header in requests. In dev mode (default), auth is disabled.

## Versioning

The API supports URL-path versioning. Currently v1 is implemented at `/blackrock/challenge/v1/`. Future versions mount at `/blackrock/challenge/v2/` and can selectively override routers while reusing unchanged ones from v1.
