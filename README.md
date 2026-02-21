# BlackRock Retirement Savings API

Production-grade API for automated retirement savings through expense-based micro-investments. Built for the BlackRock Hackathon Challenge.

## Production Deployment (Docker)

```bash
# Pull and run from Docker Hub (3 uvicorn workers)
docker run -d -p 5477:5477 tjnakka/blk-hacking-ind-tejas-nakka
```

Or with Docker Compose:

```bash
docker compose up -d
```

The API is now available at **http://localhost:5477**

- API Docs (Swagger): http://localhost:5477/docs
- Frontend Playground: http://localhost:5477/
- Performance: http://localhost:5477/blackrock/challenge/v1/performance

## Local Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 20+ (for frontend build)

```bash
# 1. Install dependencies
uv sync

# 2. Build frontend (optional — API works without it)
cd frontend && npm install && npm run build && cd ..

# 3. Start the server (with hot-reload)
uv run uvicorn backend.main:app --host 0.0.0.0 --port 5477 --reload
```

### Testing

```bash
# Run all tests (58 tests)
uv run pytest test/ -v
```

- **Unit tests**: parser, validator, periods, tax, returns
- **Integration tests**: full endpoint round-trips with spec examples

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

Returns current datetime, memory usage, and thread count.

## Architecture

```
backend/
├── main.py                          # FastAPI app + middleware + SPA serving
├── config.py                        # All constants & env settings
├── core/
│   ├── logging.py                   # Structured JSON logging
│   └── datetime_utils.py            # Date parsing utility
└── api/v1/
    ├── router.py                    # V1 router aggregator
    ├── routers/                     # Thin HTTP layer (stateless)
    │   ├── transactions.py          # :parse, :validator, :filter
    │   ├── returns.py               # :nps, :index
    │   └── performance.py           # /performance
    ├── models/                      # Pydantic schemas (data governance)
    │   ├── transaction.py           # Expense, Transaction, InvalidTransaction
    │   ├── period.py                # BasePeriod → QPeriod, PPeriod, KPeriod
    │   ├── requests.py              # Request bodies
    │   └── responses.py             # Response bodies
    └── services/                    # Business logic (class-based)
        ├── transaction_pipeline.py  # TransactionPipeline (parse/validate/periods)
        ├── returns_service.py       # ReturnsCalculator (compound interest)
        ├── tax_service.py           # TaxCalculator (progressive slabs)
        ├── investment_strategy.py   # Strategy + StrategyRegistry + StrategyName enum
        └── performance_service.py   # PerformanceMonitor (system metrics)
frontend/                            # React playground (served from same origin)
test/                                # Unit + integration tests (58 tests)
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

## Design Patterns

| Pattern             | Where                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------- |
| **Facade**          | `TransactionPipeline.run()` — single call for the full parse → validate → period pipeline |
| **Strategy**        | `InvestmentStrategy` ABC with `NPSStrategy` / `IndexStrategy`                             |
| **Registry**        | `StrategyRegistry` — O(1) lookup, zero-change extensibility                               |
| **Template Method** | `_apply_q` / `_apply_p` share the same iterate-and-transform skeleton                     |
| **Enum (StrEnum)**  | `StrategyName` — type-safe strategy selection                                             |
| **Inheritance**     | `BasePeriod` → `QPeriod`, `PPeriod`, `KPeriod`                                            |

## Design Principles

| Principle           | Implementation                                         |
| ------------------- | ------------------------------------------------------ |
| **Clarity**         | Descriptive naming, type hints, Pydantic docs          |
| **Modular**         | Router → Service → Utils layers, single responsibility |
| **Stateless**       | No DB, no sessions — all data in request/response      |
| **Extensible**      | StrategyRegistry + versioned API (v1/v2)               |
| **Data Governance** | Pydantic enforces schemas, invalid input rejected      |
| **Observable**      | Structured JSON logging, performance endpoint          |
| **Secure**          | Pydantic input validation, type-safe schemas           |

## Versioning

The API supports URL-path versioning. Currently v1 is implemented at `/blackrock/challenge/v1/`. Future versions mount at `/blackrock/challenge/v2/` and can selectively override routers while reusing unchanged ones from v1.
