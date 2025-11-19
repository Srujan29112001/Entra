-- Migration: Time-Series and Historical Metrics Tracking
-- Description: Add tables for tracking company metrics over time (no more synthetic data!)
-- Date: 2025-11-19

-- ============================================================================
-- COMPANY METRICS TIME SERIES
-- ============================================================================

-- Financial metrics snapshots (daily/weekly/monthly)
CREATE TABLE IF NOT EXISTS public.financial_metrics_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Timestamp
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    period_type VARCHAR(20) NOT NULL DEFAULT 'daily', -- daily, weekly, monthly, quarterly

    -- Revenue metrics
    revenue DECIMAL(15, 2),
    recurring_revenue DECIMAL(15, 2),
    one_time_revenue DECIMAL(15, 2),

    -- Expense metrics
    total_expenses DECIMAL(15, 2),
    operating_expenses DECIMAL(15, 2),
    marketing_expenses DECIMAL(15, 2),
    rd_expenses DECIMAL(15, 2),
    admin_expenses DECIMAL(15, 2),

    -- Cash metrics
    cash_balance DECIMAL(15, 2),
    accounts_receivable DECIMAL(15, 2),
    accounts_payable DECIMAL(15, 2),

    -- Derived metrics
    burn_rate DECIMAL(15, 2),
    runway_months DECIMAL(5, 2),
    gross_margin DECIMAL(5, 4),
    net_margin DECIMAL(5, 4),

    -- Customer metrics
    total_customers INTEGER,
    new_customers INTEGER,
    churned_customers INTEGER,
    active_customers INTEGER,

    -- Employee metrics
    total_employees INTEGER,

    -- Metadata
    source VARCHAR(50) DEFAULT 'manual', -- manual, api, integration
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_period_type CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly'))
);

-- Indexes for efficient time-series queries
CREATE INDEX idx_financial_metrics_company_time ON public.financial_metrics_history(company_id, recorded_at DESC);
CREATE INDEX idx_financial_metrics_period ON public.financial_metrics_history(company_id, period_type, recorded_at DESC);

-- Row-Level Security
ALTER TABLE public.financial_metrics_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company metrics history"
    ON public.financial_metrics_history FOR SELECT
    USING (
        user_id = auth.uid() OR
        company_id IN (SELECT id FROM public.companies WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert their company metrics"
    ON public.financial_metrics_history FOR INSERT
    WITH CHECK (
        user_id = auth.uid() AND
        company_id IN (SELECT id FROM public.companies WHERE user_id = auth.uid())
    );

-- ============================================================================
-- CUSTOMER COHORTS & LTV TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.customer_cohorts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,

    -- Cohort definition
    cohort_month DATE NOT NULL, -- First day of month customer signed up

    -- Cohort metrics by age
    month_0_customers INTEGER DEFAULT 0,
    month_0_revenue DECIMAL(15, 2) DEFAULT 0,
    month_1_customers INTEGER,
    month_1_revenue DECIMAL(15, 2),
    month_2_customers INTEGER,
    month_2_revenue DECIMAL(15, 2),
    month_3_customers INTEGER,
    month_3_revenue DECIMAL(15, 2),
    month_6_customers INTEGER,
    month_6_revenue DECIMAL(15, 2),
    month_12_customers INTEGER,
    month_12_revenue DECIMAL(15, 2),

    -- Calculated metrics
    retention_rate_1mo DECIMAL(5, 4),
    retention_rate_3mo DECIMAL(5, 4),
    retention_rate_6mo DECIMAL(5, 4),
    retention_rate_12mo DECIMAL(5, 4),
    ltv_estimate DECIMAL(15, 2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(company_id, cohort_month)
);

CREATE INDEX idx_customer_cohorts_company ON public.customer_cohorts(company_id, cohort_month DESC);

ALTER TABLE public.customer_cohorts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their company cohorts"
    ON public.customer_cohorts FOR ALL
    USING (company_id IN (SELECT id FROM public.companies WHERE user_id = auth.uid()));

-- ============================================================================
-- KPI TARGETS & GOALS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.kpi_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Target definition
    kpi_name VARCHAR(100) NOT NULL,
    target_value DECIMAL(15, 2) NOT NULL,
    target_date DATE NOT NULL,

    -- Progress tracking
    current_value DECIMAL(15, 2),
    last_updated TIMESTAMP WITH TIME ZONE,

    -- Metadata
    category VARCHAR(50), -- revenue, customers, efficiency, etc.
    unit VARCHAR(20), -- dollars, count, percentage, etc.
    status VARCHAR(20) DEFAULT 'active', -- active, achieved, abandoned

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_kpi_targets_company ON public.kpi_targets(company_id, target_date);

ALTER TABLE public.kpi_targets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their KPI targets"
    ON public.kpi_targets FOR ALL
    USING (
        user_id = auth.uid() AND
        company_id IN (SELECT id FROM public.companies WHERE user_id = auth.uid())
    );

-- ============================================================================
-- MARKET & COMPETITIVE METRICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.market_metrics_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,

    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Market data
    market_size_tam DECIMAL(15, 2),
    market_size_sam DECIMAL(15, 2),
    market_size_som DECIMAL(15, 2),
    market_growth_rate DECIMAL(5, 4),

    -- Competitive position
    market_share DECIMAL(5, 4),
    competitors_count INTEGER,
    pricing_position VARCHAR(20), -- premium, mid_market, budget

    -- External indicators (from FRED/World Bank)
    gdp_value DECIMAL(15, 2),
    inflation_rate DECIMAL(5, 4),
    unemployment_rate DECIMAL(5, 4),
    interest_rate DECIMAL(5, 4),

    -- Industry-specific
    industry_growth_rate DECIMAL(5, 4),
    industry_trends JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_market_metrics_company_time ON public.market_metrics_history(company_id, recorded_at DESC);

ALTER TABLE public.market_metrics_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their market metrics"
    ON public.market_metrics_history FOR ALL
    USING (company_id IN (SELECT id FROM public.companies WHERE user_id = auth.uid()));

-- ============================================================================
-- AGENT PERFORMANCE METRICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.agent_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Agent identification
    agent_type VARCHAR(50) NOT NULL,
    agent_version VARCHAR(20),

    -- Performance metrics
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10, 2),
    avg_token_usage INTEGER,

    -- Quality metrics (from user feedback)
    avg_user_rating DECIMAL(3, 2),
    total_ratings INTEGER DEFAULT 0,

    -- Tool usage stats
    tool_calls_count INTEGER DEFAULT 0,
    mcp_calls_count INTEGER DEFAULT 0,
    rag_retrievals_count INTEGER DEFAULT 0,

    -- Cost tracking
    total_cost_usd DECIMAL(10, 4),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_performance_type_time ON public.agent_performance_metrics(agent_type, recorded_at DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate burn rate from recent expenses
CREATE OR REPLACE FUNCTION calculate_current_burn_rate(p_company_id UUID, p_months INTEGER DEFAULT 3)
RETURNS DECIMAL AS $$
DECLARE
    avg_burn DECIMAL;
BEGIN
    SELECT AVG(total_expenses - revenue)
    INTO avg_burn
    FROM public.financial_metrics_history
    WHERE company_id = p_company_id
      AND recorded_at >= NOW() - (p_months || ' months')::INTERVAL
      AND period_type = 'monthly';

    RETURN COALESCE(avg_burn, 0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get revenue growth rate
CREATE OR REPLACE FUNCTION calculate_revenue_growth_rate(p_company_id UUID, p_months INTEGER DEFAULT 6)
RETURNS DECIMAL AS $$
DECLARE
    growth_rate DECIMAL;
    first_revenue DECIMAL;
    last_revenue DECIMAL;
BEGIN
    -- Get first and last revenue in period
    SELECT revenue INTO first_revenue
    FROM public.financial_metrics_history
    WHERE company_id = p_company_id
      AND period_type = 'monthly'
      AND recorded_at >= NOW() - (p_months || ' months')::INTERVAL
    ORDER BY recorded_at ASC
    LIMIT 1;

    SELECT revenue INTO last_revenue
    FROM public.financial_metrics_history
    WHERE company_id = p_company_id
      AND period_type = 'monthly'
      AND recorded_at >= NOW() - (p_months || ' months')::INTERVAL
    ORDER BY recorded_at DESC
    LIMIT 1;

    IF first_revenue > 0 AND first_revenue IS NOT NULL AND last_revenue IS NOT NULL THEN
        growth_rate := ((last_revenue - first_revenue) / first_revenue) * 100;
        RETURN growth_rate;
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Latest metrics for each company
CREATE OR REPLACE VIEW public.latest_company_metrics AS
SELECT DISTINCT ON (company_id)
    *
FROM public.financial_metrics_history
ORDER BY company_id, recorded_at DESC;

-- Monthly revenue trends
CREATE OR REPLACE VIEW public.monthly_revenue_trends AS
SELECT
    company_id,
    DATE_TRUNC('month', recorded_at) AS month,
    SUM(revenue) AS total_revenue,
    SUM(total_expenses) AS total_expenses,
    SUM(revenue) - SUM(total_expenses) AS net_income,
    AVG(gross_margin) AS avg_gross_margin
FROM public.financial_metrics_history
WHERE period_type IN ('daily', 'monthly')
GROUP BY company_id, DATE_TRUNC('month', recorded_at)
ORDER BY company_id, month DESC;

-- Grant permissions on views
GRANT SELECT ON public.latest_company_metrics TO authenticated;
GRANT SELECT ON public.monthly_revenue_trends TO authenticated;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE public.financial_metrics_history IS 'Historical financial metrics for trend analysis and charts';
COMMENT ON TABLE public.customer_cohorts IS 'Customer cohort analysis for LTV and retention tracking';
COMMENT ON TABLE public.kpi_targets IS 'Company KPI targets and goals tracking';
COMMENT ON TABLE public.market_metrics_history IS 'Market and macroeconomic metrics over time';
COMMENT ON TABLE public.agent_performance_metrics IS 'AI agent performance and quality metrics';
COMMENT ON FUNCTION calculate_current_burn_rate IS 'Calculate average burn rate over recent months';
COMMENT ON FUNCTION calculate_revenue_growth_rate IS 'Calculate revenue growth rate over period';
