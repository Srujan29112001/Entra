# Entra - AI-Powered Advisory Platform for Entrepreneurs

A comprehensive, enterprise-grade multi-agent AI platform that provides entrepreneurs with expert advice on finance, tax, strategy, legal, and personal wealth management.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User & UI Layer                      │
│              (Next.js + React + Tailwind)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              API Gateway / Backend App                  │
│         (Next.js API Routes + FastAPI)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│           Multi-Agent Orchestrator                      │
│              (LangGraph + LangChain)                    │
└─────┬──────┬──────┬──────┬──────┬───────────────────────┘
      │      │      │      │      │
      ▼      ▼      ▼      ▼      ▼
  ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
  │Finance││Tax ││Market││Legal││Wealth│  Specialist Agents
  │Agent││Agent││Agent││Agent││Agent│
  └──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘
     │      │      │      │      │
     └──────┴──────┴──────┴──────┘
              │
┌─────────────▼───────────────────────────────────────────┐
│         Tools & RAG Layer                               │
│  (Vector DB, APIs, Calculators, Doc Parsers)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│      Database & Auth (Supabase Postgres + Auth)        │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI**: React 18, TypeScript
- **Styling**: Tailwind CSS, shadcn/ui
- **Charts**: Recharts
- **State**: Zustand
- **Forms**: React Hook Form + Zod

### Backend
- **Agent Orchestration**: FastAPI + LangGraph
- **API Gateway**: Next.js API Routes
- **LLM Framework**: LangChain
- **Models**: Claude 3.5 Sonnet, GPT-4

### Data & Storage
- **Database**: Supabase (Postgres)
- **Vector DB**: pgvector (Supabase extension)
- **Auth**: Supabase Auth (JWT)
- **File Storage**: Supabase Storage

### AI & RAG
- **Embeddings**: OpenAI / Hugging Face
- **Vector Search**: pgvector
- **Document Processing**: LangChain Document Loaders
- **OCR**: Tesseract / Cloud Vision API

### Infrastructure
- **Deployment**: Vercel (Frontend), Docker (Backend)
- **Orchestration**: Kubernetes (optional)
- **Monitoring**: Helicone, Sentry, Prometheus
- **CI/CD**: GitHub Actions

## Project Structure

```
entra/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── agents/              # FastAPI agent backend
├── packages/
│   ├── database/            # Supabase schemas & migrations
│   ├── ui/                  # Shared UI components
│   ├── types/               # Shared TypeScript types
│   └── utils/               # Shared utilities
├── docker/                  # Docker configurations
├── docs/                    # Documentation
└── scripts/                 # Build & deployment scripts
```

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 8+
- Python 3.11+
- Docker & Docker Compose
- Supabase CLI

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd entra
```

2. Install dependencies:
```bash
pnpm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your API keys
```

4. Start Supabase locally:
```bash
supabase start
```

5. Run database migrations:
```bash
pnpm db:migrate
```

6. Start development servers:
```bash
pnpm dev
```

This will start:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Supabase Studio: http://localhost:54323

## Specialist Agents

### 1. Finance & Fund Management Agent
- Revenue & expense modeling
- Runway calculations
- Funding strategy (debt vs equity)
- Unit economics (CAC, LTV)
- Scenario planning

### 2. Tax & Policy Agent
- Multi-jurisdiction tax calculations
- Corporate vs personal tax optimization
- Policy incentive identification
- Compliance checking
- Salary vs dividend structuring

### 3. Market & Strategy Agent
- Go-to-market planning
- Distribution channel selection
- SWOT analysis
- Competitive positioning
- Pricing strategy

### 4. Legal & Compliance Agent
- Contract analysis & summarization
- Risk identification
- Clause extraction from PDFs
- Jurisdiction-specific compliance
- Template generation

### 5. Personal Wealth Agent
- Founder salary optimization
- Personal tax planning
- Wealth accumulation strategy
- ESOP/equity structuring
- Exit planning

## Features

- **Multi-Agent Intelligence**: Coordinated specialist agents working together
- **RAG-Powered Insights**: Grounded in real tax laws, market data, and policies
- **Real-Time Calculations**: Financial models, tax projections, scenario analysis
- **Document Intelligence**: Extract insights from contracts, pitch decks, tax notices
- **Interactive Dashboard**: Visualize runway, burn rate, projections
- **Scenario Planning**: Model different growth, hiring, pricing scenarios
- **Multi-Jurisdiction**: Support for different countries and tax systems
- **Secure & Private**: Row-level security, encrypted data, SOC 2 ready

## Development

### Running Tests
```bash
pnpm test
```

### Type Checking
```bash
pnpm type-check
```

### Linting
```bash
pnpm lint
```

### Building for Production
```bash
pnpm build
```

## Deployment

### Frontend (Vercel)
```bash
vercel deploy
```

### Backend (Docker)
```bash
docker build -t entra-agents:latest -f docker/Dockerfile.agents .
docker push entra-agents:latest
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## Monitoring

- **LLM Observability**: Helicone dashboard
- **Error Tracking**: Sentry
- **Metrics**: Prometheus + Grafana
- **Logs**: CloudWatch / GCP Logging

## Security

- JWT-based authentication
- Row-level security (RLS) in Supabase
- API rate limiting
- Input validation with Zod/Pydantic
- Secrets management with environment variables
- HTTPS everywhere
- Regular security audits

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

Proprietary - All Rights Reserved

## Support

For issues and questions: [GitHub Issues](https://github.com/your-org/entra/issues)
