# 🚀 Entra AI Advisor Platform - Complete Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup (Supabase)](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Monitoring & Observability](#monitoring--observability)
7. [Post-Deployment Testing](#post-deployment-testing)
8. [Scaling & Performance](#scaling--performance)

---

## Prerequisites

### Required Software

- **Node.js**: 20.x or higher
- **pnpm**: 8.x or higher
- **Python**: 3.11 or higher
- **Docker**: Latest version
- **Docker Compose**: 2.x or higher

### Required API Keys

1. **Supabase** (Database & Auth)
   - Sign up at https://supabase.com
   - Create a new project
   - Get your `SUPABASE_URL` and `SUPABASE_ANON_KEY`

2. **OpenAI** (LLM & Embeddings)
   - Get API key from https://platform.openai.com

3. **Anthropic (Claude)** (Primary LLM)
   - Get API key from https://console.anthropic.com

4. **Alpha Vantage** (Financial Data) - OPTIONAL
   - Free key: https://www.alphavantage.co/support/#api-key

5. **NewsAPI** (Market News) - OPTIONAL
   - Free key: https://newsapi.org/register

6. **Helicone** (LLM Observability) - OPTIONAL
   - Sign up at https://helicone.ai

7. **Sentry** (Error Tracking) - OPTIONAL
   - Sign up at https://sentry.io

---

## Environment Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <your-repo-url>
cd entra

# Install dependencies
make install

# Or manually:
pnpm install
cd apps/agents && pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables:**

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Backend API URL
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000

# Optional: External Data APIs
ALPHA_VANTAGE_API_KEY=your-key  # For financial data
NEWS_API_KEY=your-key            # For market news

# Optional: Monitoring
HELICONE_API_KEY=your-key
SENTRY_DSN=your-dsn

# Environment
NODE_ENV=development
```

---

## Database Setup (Supabase)

### Option 1: Use Supabase Cloud (Recommended for Production)

1. **Create Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Note your project URL and keys

2. **Run Migrations**

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

**OR** manually run the SQL:

```bash
# Copy the migration file content
cat packages/database/supabase/migrations/001_initial_schema.sql

# Paste into Supabase SQL Editor and run
```

3. **Enable pgvector Extension**

In Supabase Dashboard → Database → Extensions:
- Enable `vector` extension

### Option 2: Local Development with Docker

```bash
# Start local Supabase
make docker-up

# Run migrations
make db-migrate

# Access local Supabase Studio
# http://localhost:54323
```

---

## Backend Deployment

### Option 1: Docker (Recommended)

```bash
# Build Docker image
docker build -t entra-agents:latest -f docker/Dockerfile.agents .

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
  -e SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY \
  entra-agents:latest

# Test
curl http://localhost:8000/health
```

### Option 2: Cloud Platforms

#### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy
cd apps/agents
railway up

# Add environment variables in Railway dashboard
```

#### Deploy to Render

1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `cd apps/agents && pip install -r requirements.txt`
4. Set start command: `cd apps/agents && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

#### Deploy to AWS ECS/Fargate

```bash
# Build and push to ECR
aws ecr create-repository --repository-name entra-agents
docker tag entra-agents:latest <your-ecr-url>/entra-agents:latest
docker push <your-ecr-url>/entra-agents:latest

# Deploy using ECS task definition
# See aws-ecs-task-definition.json example
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd apps/web
vercel

# For production
vercel --prod
```

**Environment Variables in Vercel:**

Add all `NEXT_PUBLIC_*` variables in Vercel Dashboard → Settings → Environment Variables

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd apps/web
netlify deploy --prod
```

### Option 3: Docker + Nginx

```bash
# Build frontend
cd apps/web
pnpm build

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "start"]
EOF

# Build and run
docker build -t entra-web:latest .
docker run -p 3000:3000 entra-web:latest
```

---

## Monitoring & Observability

### 1. LLM Observability with Helicone

```bash
# In backend, wrap LLM calls with Helicone
# Already integrated in codebase

# View logs at https://helicone.ai/dashboard
```

### 2. Error Tracking with Sentry

```bash
# Frontend and backend are already instrumented

# View errors at https://sentry.io
```

### 3. Metrics with Prometheus + Grafana

```bash
# Start monitoring stack
docker-compose up -d prometheus grafana

# Access:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)

# Import Grafana dashboard
# Use pre-configured dashboard in docker/grafana/
```

### 4. Health Checks

```bash
# Backend health check
curl https://your-backend-url/health

# Returns:
# {
#   "status": "healthy",
#   "app": "Entra AI Advisor Platform",
#   "version": "1.0.0"
# }
```

---

## Post-Deployment Testing

### 1. End-to-End Test Flow

```bash
# 1. Sign up new user
# Visit: https://your-app.com/auth/signup

# 2. Complete onboarding
# Visit: https://your-app.com/onboarding

# 3. View dashboard
# Should show metrics and charts

# 4. Test chat
# Ask: "What's my runway?"

# 5. Create scenario
# Visit: https://your-app.com/dashboard/scenarios

# 6. Upload document
# Visit: https://your-app.com/dashboard/upload
```

### 2. API Tests

```bash
# Test backend endpoints
cd apps/agents

# Run pytest
pytest tests/ -v

# Expected: All tests passing
```

### 3. Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from k6.io

# Create load test script
cat > load-test.js << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  let res = http.get('https://your-backend-url/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
EOF

# Run load test
k6 run load-test.js
```

---

## Scaling & Performance

### Backend Scaling

#### Horizontal Scaling

```bash
# Kubernetes deployment
kubectl apply -f k8s/deployment.yaml

# Or with Docker Swarm
docker service scale entra-agents=5
```

#### Autoscaling on AWS ECS

```json
{
  "scalingTargetId": "service/entra-cluster/entra-agents-service",
  "minCapacity": 2,
  "maxCapacity": 10,
  "targetTrackingScalingPolicyConfiguration": {
    "targetValue": 70.0,
    "predefinedMetricSpecification": {
      "predefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }
}
```

### Database Scaling

1. **Enable Connection Pooling**
   - Use PgBouncer (built into Supabase)

2. **Read Replicas**
   - Configure in Supabase Dashboard → Database → Read Replicas

3. **Index Optimization**
   - Already configured in migration file

### Caching Strategy

```bash
# Add Redis for caching
docker run -d -p 6379:6379 redis:alpine

# Configure in backend
# Already set up in docker-compose.yml
```

### CDN for Frontend

- Vercel/Netlify have built-in CDN
- For custom: Use CloudFlare, AWS CloudFront, or Fastly

---

## Cost Estimation

### Monthly Costs (Production - 10,000 users, 50,000 chats)

| Service | Plan | Cost |
|---------|------|------|
| Supabase | Pro | $25 |
| Vercel | Pro | $20 |
| Backend (Railway/Render) | - | $50 |
| OpenAI API | Pay-as-you-go | $100-200 |
| Anthropic (Claude) | Pay-as-you-go | $500-1000 |
| Helicone | Free | $0 |
| Sentry | Free | $0 |
| **Total** | | **~$700-1300/month** |

### Optimization Tips

1. **Use caching** to reduce LLM calls
2. **Implement rate limiting** per user
3. **Use smaller models** for simple queries (e.g., GPT-3.5 instead of GPT-4)
4. **Batch requests** where possible
5. **Monitor usage** with Helicone

---

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Clear cache and reinstall
rm -rf node_modules
pnpm install
```

**2. Database connection failed**
```bash
# Check Supabase URL and keys
# Verify RLS policies are enabled
```

**3. LLM API rate limits**
```bash
# Add retry logic with exponential backoff
# Implement request queuing
# Use caching
```

**4. Slow response times**
```bash
# Check agent execution time
# Enable streaming for chat
# Optimize database queries
```

---

## Security Checklist

- [ ] All API keys stored in environment variables
- [ ] Row-Level Security enabled in Supabase
- [ ] HTTPS enforced (automatic with Vercel/Railway)
- [ ] Rate limiting configured
- [ ] Input validation with Zod/Pydantic
- [ ] CORS properly configured
- [ ] Secrets never committed to Git
- [ ] Regular dependency updates
- [ ] Security headers configured

---

## Next Steps

1. **Monitor for 1 week** - Check errors, performance, costs
2. **Gather user feedback** - Iterate on prompts and features
3. **Optimize costs** - Review LLM usage, add caching
4. **Add more agents** - Expand to new domains
5. **Build mobile app** - React Native version
6. **Enterprise features** - SSO, RBAC, audit logs

---

## Support & Resources

- **Documentation**: See README.md, SETUP.md, CONTRIBUTING.md
- **Issues**: GitHub Issues
- **Community**: Discord/Slack (if applicable)

---

**🎉 Congratulations! Your Entra AI Advisor Platform is now deployed and ready for users!**
