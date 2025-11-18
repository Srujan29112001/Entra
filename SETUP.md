# Entra AI Advisor Platform - Setup Guide

Complete setup guide for the Entra AI-powered advisory platform.

## Prerequisites

### Required
- **Node.js** >= 20.0.0
- **pnpm** >= 8.0.0
- **Python** >= 3.11
- **Docker** and **Docker Compose**
- **Git**

### API Keys Required
- **OpenAI API Key** - For GPT-4 and embeddings
- **Anthropic API Key** - For Claude 3.5 Sonnet
- **Supabase Project** - For database and auth

### Optional (for production)
- **Helicone API Key** - LLM observability
- **Sentry DSN** - Error tracking
- **Vercel Account** - Frontend deployment

## Quick Start (5 Minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd entra

# Install dependencies
make install
# or manually:
pnpm install
cd apps/agents && pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file in the root:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Supabase (create a project at supabase.com)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Monitoring
HELICONE_API_KEY=your-helicone-key
SENTRY_DSN=your-sentry-dsn
```

### 3. Start Development Environment

```bash
# Start all services (database, redis, backend, monitoring)
make dev-full

# Or individually:
make docker-up  # Start PostgreSQL + Redis
make dev        # Start Next.js frontend + agents backend
```

Your services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

### 4. Initialize Database

```bash
make db-migrate
```

## Development

### Project Structure

```
entra/
├── apps/
│   ├── web/              # Next.js frontend
│   └── agents/           # FastAPI agent backend
├── packages/
│   ├── database/         # Database schemas & migrations
│   ├── ui/              # Shared UI components
│   └── types/           # Shared TypeScript types
├── docker/              # Docker configurations
└── .github/workflows/   # CI/CD pipelines
```

### Running Tests

```bash
# All tests
make test

# Frontend only
make test-frontend

# Backend only
make test-backend
```

### Code Quality

```bash
# Linting
make lint

# Formatting
make format

# Type checking
make type-check
```

### Working with Agents

Each specialist agent is in `apps/agents/app/agents/`:
- `finance_agent.py` - Finance & Fund Management
- `tax_agent.py` - Tax & Policy
- `market_agent.py` - Market & Strategy
- `legal_agent.py` - Legal & Compliance
- `wealth_agent.py` - Personal Wealth

To test an agent directly:

```python
from app.agents.finance_agent import FinanceAgent
from app.models.schemas import AgentTask

agent = FinanceAgent()
task = AgentTask(
    task_id="test",
    agent_type="finance",
    question="Calculate my runway",
    context={"company_data": {"cash_balance": 100000, "monthly_expenses": 10000}},
    user_id="user123",
    company_id="comp123"
)

result = await agent.process(task)
print(result.answer)
```

### Working with RAG

Ingest documents:

```python
from app.rag.ingestion import pipeline

# Ingest a PDF
result = await pipeline.ingest_file(
    file_path="path/to/tax_document.pdf",
    company_id="comp123",
    document_type="tax",
    metadata={"year": 2024, "country": "US"}
)

# Query documents
from app.rag.retriever import retriever

results = await retriever.retrieve(
    query="What are the corporate tax rates?",
    company_id="comp123",
    document_type="tax",
    top_k=5
)
```

## Database Management

### Local PostgreSQL with pgvector

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Connect to database
make shell-db

# Run migrations
make db-migrate

# Reset database (WARNING: destroys data)
make db-reset
```

### Supabase (Production)

1. Create a Supabase project at https://supabase.com
2. Enable pgvector extension:
   - Go to Database → Extensions
   - Enable "vector"
3. Run migrations:
   - Copy content of `packages/database/supabase/migrations/001_initial_schema.sql`
   - Paste into Supabase SQL Editor
   - Execute

4. Set up Row Level Security:
   - Already included in migration script
   - Policies ensure users only access their own data

## Deployment

### Frontend (Vercel)

1. **Connect Repository**
   ```bash
   cd apps/web
   vercel link
   ```

2. **Set Environment Variables**
   - Go to Vercel Dashboard → Project Settings → Environment Variables
   - Add all `NEXT_PUBLIC_*` variables

3. **Deploy**
   ```bash
   make deploy-frontend
   # or
   vercel --prod
   ```

### Backend (Docker)

1. **Build Docker Image**
   ```bash
   docker build -t entra-agents:latest -f docker/Dockerfile.agents .
   ```

2. **Push to Registry**
   ```bash
   docker tag entra-agents:latest your-registry/entra-agents:latest
   docker push your-registry/entra-agents:latest
   ```

3. **Deploy to Cloud**

   **Option A: Railway**
   - Connect GitHub repo
   - Set environment variables
   - Deploy

   **Option B: Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

   **Option C: AWS ECS/Fargate**
   - Create task definition
   - Create service
   - Configure load balancer

## Monitoring & Observability

### Prometheus & Grafana

```bash
# Start monitoring stack
docker-compose up -d prometheus grafana

# Access dashboards
make monitoring
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### Helicone (LLM Monitoring)

Add to your `.env`:
```env
HELICONE_API_KEY=your-key
```

View LLM usage, costs, and latency at https://helicone.ai

### Sentry (Error Tracking)

Add to your `.env`:
```env
SENTRY_DSN=your-dsn
```

Errors automatically sent to Sentry dashboard.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
PORT=3001 pnpm dev
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Agent Not Responding

```bash
# Check backend logs
make logs-agents

# Restart agents service
docker-compose restart agents
```

### Out of Memory (Embeddings)

Reduce batch size in `app/rag/retriever.py`:

```python
# Change chunk_size
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Reduced from 1000
    chunk_overlap=100,
)
```

## Performance Optimization

### Frontend
- Enable SWC minification (already configured)
- Use `next/image` for optimized images
- Implement code splitting with dynamic imports
- Enable caching in Vercel

### Backend
- Use Redis for caching agent responses
- Batch database queries
- Implement request rate limiting
- Use async/await properly

### Database
- Create indexes for frequently queried fields (already done)
- Use connection pooling
- Implement query result caching
- Regular VACUUM and ANALYZE

## Security Best Practices

1. **Never commit `.env` files**
2. **Use Row Level Security** (RLS) in Supabase
3. **Validate all inputs** with Pydantic/Zod
4. **Rate limit API endpoints**
5. **Use HTTPS in production**
6. **Rotate API keys regularly**
7. **Monitor for suspicious activity**

## Getting Help

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Next Steps

1. **Customize Agents**: Modify prompts in `app/agents/*.py`
2. **Add Tools**: Create new tools in `app/tools/`
3. **Extend RAG**: Add more document types
4. **Build UI**: Create dashboard components
5. **Add Features**: Implement scenario planning UI
6. **Scale**: Set up autoscaling and load balancing

## License

Proprietary - All Rights Reserved
