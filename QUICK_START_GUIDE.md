# Entra Platform - Quick Start & Deployment Guide

This comprehensive guide covers everything you need to run, build, and deploy the Entra AI-Powered Entrepreneur Support Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Development Environment](#development-environment)
4. [Building for Production](#building-for-production)
5. [Deployment Options](#deployment-options)
6. [Environment Variables](#environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **pnpm** 8.x or higher (`npm install -g pnpm`)
- **Python** 3.11 or higher ([Download](https://www.python.org/))
- **Docker** & **Docker Compose** ([Download](https://www.docker.com/))
- **Git** ([Download](https://git-scm.com/))

### Required API Keys

1. **Supabase** (Database & Auth)
   - Create project at [supabase.com](https://supabase.com)
   - Get: URL, Anon Key, Service Role Key

2. **OpenAI** (AI Models)
   - Get API key at [platform.openai.com](https://platform.openai.com/api-keys)

3. **Anthropic Claude** (AI Models)
   - Get API key at [console.anthropic.com](https://console.anthropic.com/settings/keys)

4. **FRED API** (Economic Data)
   - Get free key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)

### Optional API Keys

- **Helicone** (LLM Observability): [helicone.ai](https://www.helicone.ai/)
- **Sentry** (Error Tracking): [sentry.io](https://sentry.io/)
- **Alpha Vantage** (Stock Data): [alphavantage.co](https://www.alphavantage.co/)
- **NewsAPI** (Business News): [newsapi.org](https://newsapi.org/)

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Srujan29112001/Entra.git
cd Entra
```

### 2. Install Dependencies

```bash
# Install frontend dependencies
pnpm install

# Install backend dependencies
cd apps/agents
pip install -r requirements.txt
cd ../..
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor
```

**Required variables to update in `.env`:**

```bash
# Supabase (REQUIRED)
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_actual_service_role_key

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-proj-your_actual_openai_key

# Anthropic (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your_actual_anthropic_key

# FRED API (REQUIRED for economic data)
FRED_API_KEY=your_actual_fred_api_key
```

### 4. Setup Supabase Database

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Run migrations
supabase db push
```

**Or manually via Supabase Dashboard:**
1. Go to your Supabase project → SQL Editor
2. Execute the SQL files in order:
   - `packages/database/supabase/migrations/001_initial_schema.sql`
   - `packages/database/supabase/migrations/002_time_series_and_metrics.sql`

---

## Development Environment

### Option 1: Quick Start (Makefile)

```bash
# Install all dependencies
make install

# Start development servers (frontend + backend)
make dev

# Start all services including monitoring
make dev-full
```

### Option 2: Individual Services

#### Frontend Only

```bash
cd apps/web
pnpm dev
```
- Access at: http://localhost:3000

#### Backend Only

```bash
cd apps/agents
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Access at: http://localhost:8000
- API docs: http://localhost:8000/docs

#### Full Stack with Docker

```bash
docker-compose up
```

**Services available:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

---

## Building for Production

### Frontend (Next.js)

```bash
cd apps/web

# Type check
pnpm type-check

# Build production bundle
pnpm build

# Start production server
pnpm start
```

### Backend (FastAPI)

#### Option 1: Docker (Recommended)

```bash
# Build Docker image
docker build -t entra-agents:latest -f docker/Dockerfile.agents .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  entra-agents:latest
```

#### Option 2: Direct Python

```bash
cd apps/agents

# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (production server)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Build Everything

```bash
# Using Makefile
make build

# Or with TurboRepo
pnpm turbo build
```

---

## Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd apps/web
vercel --prod
```

3. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `BACKEND_API_URL` (your Railway backend URL)

#### Deploy Backend to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Deploy:
```bash
railway up
```

4. Set environment variables in Railway dashboard (all from `.env`)

### Option 2: Docker Compose (VPS/Cloud)

1. **Setup VPS** (DigitalOcean, AWS EC2, etc.)

2. **Install Docker & Docker Compose**

3. **Clone repository and configure**:
```bash
git clone https://github.com/Srujan29112001/Entra.git
cd Entra
cp .env.example .env
# Edit .env with production values
```

4. **Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: AWS ECS/Fargate

1. **Build and push Docker images**:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ECR_URL

# Build and tag
docker build -t entra-agents:latest -f docker/Dockerfile.agents .
docker tag entra-agents:latest YOUR_ECR_URL/entra-agents:latest

# Push
docker push YOUR_ECR_URL/entra-agents:latest
```

2. **Create ECS Task Definition** with environment variables

3. **Create ECS Service** with load balancer

4. **Deploy frontend to Vercel** pointing to ECS backend

### Option 4: Kubernetes (Enterprise)

```bash
# Create namespace
kubectl create namespace entra

# Create secrets from .env
kubectl create secret generic entra-secrets --from-env-file=.env -n entra

# Apply Kubernetes manifests (create these based on docker-compose.yml)
kubectl apply -f k8s/ -n entra
```

---

## Environment Variables

### Critical Production Settings

```bash
# SECURITY: Change these in production!
NODE_ENV=production
ENVIRONMENT=production
DEBUG=false
USE_MOCK_DATA=false
ALLOW_PLACEHOLDER_KEYS=false

# CORS: Add your production domains
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Database: Use Supabase Connection Pooler for production
DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# Redis: Use managed Redis (Railway, Upstash, etc.)
REDIS_URL=redis://your-redis-url:6379
```

### All Environment Variables

See `.env.example` for complete list with descriptions.

---

## Testing

### Frontend Tests

```bash
cd apps/web
pnpm test
pnpm test:watch
```

### Backend Tests

```bash
cd apps/agents
pytest
pytest --cov=app tests/  # with coverage
```

### E2E Tests

```bash
pnpm test:e2e
```

### Run All Tests

```bash
make test
```

---

## Monitoring & Observability

### Local Monitoring Stack

```bash
# Start monitoring services
docker-compose up prometheus grafana
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin`
  - Dashboards: Pre-configured in `docker/grafana/dashboards/`

### Production Monitoring

1. **Sentry** (Error Tracking)
   - Add `SENTRY_DSN` to environment variables
   - Automatic error reporting enabled

2. **Helicone** (LLM Observability)
   - Add `HELICONE_API_KEY` to environment variables
   - Track LLM usage, costs, and latency

3. **Custom Metrics**
   - FastAPI exposes `/metrics` endpoint for Prometheus
   - Configure Prometheus to scrape your backend

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

```bash
# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### 2. Database connection errors

- Verify Supabase URL and keys in `.env`
- Check if database migrations are applied
- Ensure IP is whitelisted in Supabase (or disable RLS for testing)

#### 3. Python dependency conflicts

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r apps/agents/requirements.txt
```

#### 4. Docker build fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 5. TypeScript errors

```bash
cd apps/web
pnpm type-check
```

#### 6. Port already in use

```bash
# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9
```

### Health Checks

```bash
# Check frontend
curl http://localhost:3000

# Check backend API
curl http://localhost:8000/health

# Check backend docs
curl http://localhost:8000/docs
```

### Logs

```bash
# Docker logs
docker-compose logs -f agents
docker-compose logs -f postgres

# Backend logs (if running directly)
tail -f apps/agents/logs/app.log
```

---

## Performance Optimization

### Frontend

1. **Enable caching**:
   - Configure CDN (Vercel automatically does this)
   - Use `stale-while-revalidate` for data fetching

2. **Optimize images**:
   - Already configured in `next.config.js`
   - Use Next.js `<Image>` component

3. **Code splitting**:
   - Automatically handled by Next.js App Router
   - Use dynamic imports for heavy components

### Backend

1. **Enable Redis caching**:
   - Already configured in `docker-compose.yml`
   - Set `REDIS_URL` in production

2. **Database optimization**:
   - Use connection pooling (Supabase Pooler)
   - Add indexes for frequently queried fields

3. **Celery for background tasks**:
   - Already configured for document processing
   - Offloads heavy computations from API

---

## Security Checklist

- [ ] Change all default passwords and secret keys
- [ ] Set `DEBUG=false` in production
- [ ] Set `ALLOW_PLACEHOLDER_KEYS=false` in production
- [ ] Enable HTTPS/SSL for all services
- [ ] Configure CORS properly (`ALLOWED_ORIGINS`)
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting on API endpoints
- [ ] Set up backups for database
- [ ] Configure Sentry for error tracking
- [ ] Review and limit service role key usage

---

## Useful Commands Reference

```bash
# Development
make install          # Install all dependencies
make dev             # Start dev servers
make dev-full        # Start all services with monitoring

# Building
make build           # Build frontend and backend
pnpm build           # Build frontend only

# Testing
make test            # Run all tests
make test-frontend   # Frontend tests only
make test-backend    # Backend tests only

# Docker
docker-compose up    # Start all services
docker-compose down  # Stop all services
docker-compose logs -f  # View logs

# Database
supabase db push     # Apply migrations
supabase db reset    # Reset database (dev only)

# Type checking
pnpm type-check      # Check TypeScript errors
```

---

## Next Steps

1. ✅ Complete initial setup
2. ✅ Test locally with `make dev`
3. ✅ Deploy frontend to Vercel
4. ✅ Deploy backend to Railway/AWS
5. ✅ Configure custom domain
6. ✅ Set up monitoring
7. ✅ Configure backups
8. ✅ Launch! 🚀

---

## Support & Resources

- **Documentation**: See `README.md`, `DEPLOYMENT_GUIDE.md`
- **Architecture**: See `PROJECT_SUMMARY.md`
- **Contributing**: See `CONTRIBUTING.md`
- **Issues**: [GitHub Issues](https://github.com/Srujan29112001/Entra/issues)

---

**Built with ❤️ by the Entra Team**
