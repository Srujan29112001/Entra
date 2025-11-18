-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COMPANIES & PROJECTS
-- ============================================================================

CREATE TYPE company_stage AS ENUM (
    'idea',
    'mvp',
    'seed',
    'series_a',
    'series_b',
    'growth'
);

CREATE TYPE legal_form AS ENUM (
    'sole_proprietorship',
    'llp',
    'pvt_ltd',
    'llc',
    's_corp',
    'c_corp'
);

CREATE TABLE public.companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    country TEXT NOT NULL,
    industry TEXT NOT NULL,
    stage company_stage NOT NULL DEFAULT 'idea',
    legal_form legal_form,
    team_size INTEGER,
    founded_date DATE,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companies_user_id ON public.companies(user_id);

-- ============================================================================
-- FINANCIAL DATA
-- ============================================================================

CREATE TABLE public.financial_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Cash & Runway
    cash_balance DECIMAL(15, 2),
    monthly_revenue DECIMAL(15, 2),
    monthly_expenses DECIMAL(15, 2),
    burn_rate DECIMAL(15, 2),
    runway_months DECIMAL(5, 2),

    -- Unit Economics
    cac DECIMAL(10, 2),
    ltv DECIMAL(10, 2),
    gross_margin DECIMAL(5, 4),

    -- Funding
    total_funding DECIMAL(15, 2),
    valuation DECIMAL(15, 2),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_financial_snapshots_company_id ON public.financial_snapshots(company_id);
CREATE INDEX idx_financial_snapshots_date ON public.financial_snapshots(snapshot_date DESC);

-- ============================================================================
-- SCENARIOS
-- ============================================================================

CREATE TABLE public.scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,

    -- Parameters
    growth_rate DECIMAL(5, 4),
    hiring_plan JSONB,
    price_changes JSONB,
    funding_amount DECIMAL(15, 2),
    months_to_simulate INTEGER DEFAULT 12,

    -- Results
    projections JSONB,
    summary JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scenarios_company_id ON public.scenarios(company_id);
CREATE INDEX idx_scenarios_user_id ON public.scenarios(user_id);

-- ============================================================================
-- TAX & SALARY PLANNING
-- ============================================================================

CREATE TABLE public.salary_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Salary Structure
    founder_salary DECIMAL(12, 2),
    dividend_amount DECIMAL(12, 2),
    total_compensation DECIMAL(12, 2),

    -- Tax Calculations
    corporate_tax DECIMAL(12, 2),
    personal_tax DECIMAL(12, 2),
    total_tax DECIMAL(12, 2),
    effective_rate DECIMAL(5, 4),

    -- Metadata
    tax_year INTEGER,
    country TEXT,
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_salary_plans_company_id ON public.salary_plans(company_id);

-- ============================================================================
-- DOCUMENTS & VECTOR STORE
-- ============================================================================

CREATE TYPE document_type AS ENUM (
    'tax',
    'legal',
    'financial',
    'market_research',
    'contract',
    'pitch_deck',
    'other'
);

CREATE TABLE public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

    -- Document Info
    name TEXT NOT NULL,
    document_type document_type NOT NULL,
    file_url TEXT,
    file_size INTEGER,
    mime_type TEXT,

    -- Content for RAG
    content TEXT,
    embedding vector(1536), -- OpenAI embedding dimension

    -- Metadata
    metadata JSONB,
    processed BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_company_id ON public.documents(company_id);
CREATE INDEX idx_documents_type ON public.documents(document_type);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    filter_company_id uuid DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE
        (filter_company_id IS NULL OR documents.company_id = filter_company_id)
        AND 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- CHAT & CONVERSATIONS
-- ============================================================================

CREATE TABLE public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

CREATE TABLE public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at DESC);

-- ============================================================================
-- AGENT TASK LOGS
-- ============================================================================

CREATE TABLE public.agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,

    -- Task Info
    task_type TEXT NOT NULL,
    question TEXT NOT NULL,
    agents_used TEXT[], -- Array of agent types used

    -- Results
    final_answer TEXT,
    agent_responses JSONB,

    -- Performance
    execution_time_ms INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_tasks_user_id ON public.agent_tasks(user_id);
CREATE INDEX idx_agent_tasks_created_at ON public.agent_tasks(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financial_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.salary_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_tasks ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Companies policies
CREATE POLICY "Users can view own companies"
    ON public.companies FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own companies"
    ON public.companies FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own companies"
    ON public.companies FOR UPDATE
    USING (auth.uid() = user_id);

-- Financial snapshots policies
CREATE POLICY "Users can view own financial data"
    ON public.financial_snapshots FOR SELECT
    USING (
        company_id IN (
            SELECT id FROM public.companies WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own financial data"
    ON public.financial_snapshots FOR INSERT
    WITH CHECK (
        company_id IN (
            SELECT id FROM public.companies WHERE user_id = auth.uid()
        )
    );

-- Similar policies for other tables
CREATE POLICY "Users can view own scenarios"
    ON public.scenarios FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own documents"
    ON public.documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own chat sessions"
    ON public.chat_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view own agent tasks"
    ON public.agent_tasks FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all relevant tables
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON public.companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_snapshots_updated_at
    BEFORE UPDATE ON public.financial_snapshots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenarios_updated_at
    BEFORE UPDATE ON public.scenarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_salary_plans_updated_at
    BEFORE UPDATE ON public.salary_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE VIEWS
-- ============================================================================

-- Company overview view
CREATE OR REPLACE VIEW company_overview AS
SELECT
    c.id,
    c.name,
    c.stage,
    c.country,
    c.industry,
    fs.cash_balance,
    fs.runway_months,
    fs.burn_rate,
    fs.monthly_revenue,
    fs.ltv,
    fs.cac
FROM public.companies c
LEFT JOIN LATERAL (
    SELECT * FROM public.financial_snapshots
    WHERE company_id = c.id
    ORDER BY snapshot_date DESC
    LIMIT 1
) fs ON TRUE;
