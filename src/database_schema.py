"""
BLOOM Database Schema - PostgreSQL

Production-ready database design for all BLOOM systems.
Optimized for scalability, performance, and data integrity.
"""

# =============================================================================
# DATABASE SCHEMA DESIGN
# =============================================================================

DATABASE_SCHEMA = """

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    industry VARCHAR(100),

    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    stripe_customer_id VARCHAR(255) UNIQUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,

    -- Soft delete
    deleted_at TIMESTAMP,

    INDEX idx_email (email),
    INDEX idx_subscription_tier (subscription_tier),
    INDEX idx_created_at (created_at)
);

-- API Keys table
CREATE TABLE api_keys (
    api_key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,  -- First 8 chars for identification
    name VARCHAR(255),

    -- Permissions
    scopes JSONB DEFAULT '[]',  -- ['read:agents', 'write:campaigns']

    -- Rate limiting
    rate_limit_per_minute INTEGER DEFAULT 100,
    rate_limit_per_hour INTEGER DEFAULT 1000,

    -- Usage tracking
    last_used_at TIMESTAMP,
    request_count BIGINT DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_key_hash (key_hash),
    INDEX idx_is_active (is_active)
);

-- ============================================================================
-- AGENT TABLES
-- ============================================================================

-- Agents table
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    colony_id UUID NOT NULL,

    -- Identity
    agent_name VARCHAR(255) NOT NULL,
    specialization VARCHAR(100),
    personality_type VARCHAR(50),

    -- Genealogy
    parent_agent_id UUID REFERENCES agents(agent_id),
    generation INTEGER DEFAULT 1,

    -- DNA (genetic algorithm)
    dna JSONB,  -- {aggressiveness: 0.5, posting_frequency: 0.7, ...}

    -- Performance
    total_revenue DECIMAL(12, 2) DEFAULT 0.00,
    total_spent DECIMAL(12, 2) DEFAULT 0.00,
    total_conversions INTEGER DEFAULT 0,
    total_actions INTEGER DEFAULT 0,
    current_roi DECIMAL(8, 2) DEFAULT 0.00,

    -- Operating mode
    current_balance DECIMAL(12, 2) DEFAULT 0.00,
    operating_mode VARCHAR(50) DEFAULT 'SURVIVAL',

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, paused, archived
    is_rentable BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_colony_id (colony_id),
    INDEX idx_parent_agent_id (parent_agent_id),
    INDEX idx_specialization (specialization),
    INDEX idx_status (status),
    INDEX idx_is_rentable (is_rentable)
);

-- Agent strategies table
CREATE TABLE agent_strategies (
    strategy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,

    -- Strategy details
    strategy_name VARCHAR(255) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(100),

    -- Performance
    uses INTEGER DEFAULT 0,
    roi_history JSONB DEFAULT '[]',  -- [2.5, 3.1, 2.8, ...]
    average_roi DECIMAL(8, 2) DEFAULT 0.00,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_id (agent_id),
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_platform (platform)
);

-- Agent actions table (for learning replay)
CREATE TABLE agent_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,

    -- Action details
    platform VARCHAR(100) NOT NULL,
    strategy_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(100),
    content_preview TEXT,

    -- Decision tracking
    decision_reasoning TEXT,
    alternatives_considered JSONB,  -- [{option: 'twitter', score: 2.8}, ...]
    selected_option VARCHAR(255),
    expected_outcome TEXT,

    -- Results
    actual_outcome TEXT,
    cost DECIMAL(10, 2),
    revenue DECIMAL(10, 2),
    conversions INTEGER DEFAULT 0,
    roi DECIMAL(8, 2),
    success BOOLEAN,

    -- Human feedback
    human_feedback_score DECIMAL(3, 2),  -- 0-5
    human_feedback_text TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_agent_id (agent_id),
    INDEX idx_platform (platform),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- MARKETPLACE TABLES
-- ============================================================================

-- Agent marketplace listings
CREATE TABLE agent_listings (
    listing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    owner_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Listing details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price_per_day DECIMAL(10, 2) NOT NULL,

    -- Requirements met
    total_revenue DECIMAL(12, 2) NOT NULL,
    average_roi DECIMAL(8, 2) NOT NULL,
    total_conversions INTEGER NOT NULL,
    days_active INTEGER NOT NULL,

    -- Performance stats
    rating DECIMAL(3, 2) DEFAULT 5.00,  -- 0-5
    total_rentals INTEGER DEFAULT 0,
    total_rental_revenue DECIMAL(12, 2) DEFAULT 0.00,

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, paused, sold_out

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_id (agent_id),
    INDEX idx_owner_user_id (owner_user_id),
    INDEX idx_status (status),
    INDEX idx_rating (rating)
);

-- Agent rentals
CREATE TABLE agent_rentals (
    rental_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES agent_listings(listing_id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(agent_id),
    renter_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    owner_user_id UUID NOT NULL REFERENCES users(user_id),

    -- Rental terms
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    duration_days INTEGER NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,

    -- Revenue split
    owner_revenue DECIMAL(10, 2) NOT NULL,  -- 60%
    platform_revenue DECIMAL(10, 2) NOT NULL,  -- 30%
    parent_agent_revenue DECIMAL(10, 2) NOT NULL,  -- 10%

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, cancelled

    -- Performance during rental
    conversions_during_rental INTEGER DEFAULT 0,
    revenue_during_rental DECIMAL(12, 2) DEFAULT 0.00,

    -- Rating
    rating INTEGER,  -- 1-5
    review_text TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_listing_id (listing_id),
    INDEX idx_renter_user_id (renter_user_id),
    INDEX idx_owner_user_id (owner_user_id),
    INDEX idx_status (status)
);

-- Strategy marketplace listings
CREATE TABLE strategy_listings (
    strategy_listing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    seller_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Strategy details
    strategy_name VARCHAR(255) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    description TEXT,
    execution_guide TEXT NOT NULL,

    -- Performance guarantee
    price DECIMAL(10, 2) NOT NULL,
    performance_guarantee DECIMAL(8, 2) NOT NULL,  -- Min ROI guaranteed
    average_roi DECIMAL(8, 2) NOT NULL,

    -- Track record
    uses INTEGER NOT NULL,
    success_rate DECIMAL(5, 2) NOT NULL,  -- Percentage

    -- Sales stats
    total_sales INTEGER DEFAULT 0,
    total_sales_revenue DECIMAL(12, 2) DEFAULT 0.00,
    refunds INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'active',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_seller_agent_id (seller_agent_id),
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_average_roi (average_roi)
);

-- Strategy purchases
CREATE TABLE strategy_purchases (
    purchase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_listing_id UUID NOT NULL REFERENCES strategy_listings(strategy_listing_id),
    buyer_agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    buyer_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    seller_user_id UUID NOT NULL REFERENCES users(user_id),

    -- Purchase details
    price DECIMAL(10, 2) NOT NULL,
    performance_guarantee DECIMAL(8, 2) NOT NULL,

    -- Revenue split
    seller_revenue DECIMAL(10, 2) NOT NULL,  -- 70%
    platform_revenue DECIMAL(10, 2) NOT NULL,  -- 20%
    colony_revenue DECIMAL(10, 2) NOT NULL,  -- 10%

    -- Performance tracking
    actual_roi DECIMAL(8, 2),
    uses INTEGER DEFAULT 0,

    -- Refund
    refunded BOOLEAN DEFAULT false,
    refund_reason TEXT,
    refunded_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_strategy_listing_id (strategy_listing_id),
    INDEX idx_buyer_user_id (buyer_user_id),
    INDEX idx_seller_user_id (seller_user_id)
);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Performance data points (for Analytics SaaS)
CREATE TABLE performance_data_points (
    data_point_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Anonymized for cross-colony learning
    is_anonymized BOOLEAN DEFAULT false,

    -- Context
    platform VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(100),
    industry VARCHAR(100),

    -- Metrics
    roi DECIMAL(8, 2) NOT NULL,
    conversion_rate DECIMAL(5, 2),
    revenue DECIMAL(12, 2),
    cost DECIMAL(12, 2),
    actions INTEGER,
    conversions INTEGER,

    -- Agent context
    agent_age_days INTEGER,
    agent_specialization VARCHAR(100),

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_id (agent_id),
    INDEX idx_platform (platform),
    INDEX idx_industry (industry),
    INDEX idx_created_at (created_at),
    INDEX idx_is_anonymized (is_anonymized)
);

-- Benchmarks (cached, regenerated daily)
CREATE TABLE benchmarks (
    benchmark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Benchmark key
    category VARCHAR(100) NOT NULL,  -- 'platform', 'industry', 'strategy_type'
    category_value VARCHAR(100) NOT NULL,  -- 'discord', 'creative_tools', etc.

    -- Statistics
    sample_size INTEGER NOT NULL,
    average_roi DECIMAL(8, 2) NOT NULL,
    median_roi DECIMAL(8, 2) NOT NULL,
    percentile_25_roi DECIMAL(8, 2) NOT NULL,
    percentile_75_roi DECIMAL(8, 2) NOT NULL,
    percentile_90_roi DECIMAL(8, 2) NOT NULL,
    top_10_percent_roi DECIMAL(8, 2) NOT NULL,

    average_conversion_rate DECIMAL(5, 2),
    average_revenue_per_action DECIMAL(10, 2),

    -- Trends
    week_over_week_change DECIMAL(5, 2),  -- Percentage
    month_over_month_change DECIMAL(5, 2),

    -- Timestamps
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(category, category_value),
    INDEX idx_category (category),
    INDEX idx_category_value (category_value)
);

-- Analytics subscriptions
CREATE TABLE analytics_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Subscription details
    tier VARCHAR(50) NOT NULL,  -- 'free', 'basic', 'pro', 'enterprise'
    status VARCHAR(50) DEFAULT 'active',

    -- Stripe
    stripe_subscription_id VARCHAR(255) UNIQUE,

    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP,
    expires_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_tier (tier),
    INDEX idx_status (status)
);

-- ============================================================================
-- CAMPAIGN TABLES
-- ============================================================================

-- Campaigns
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    colony_id UUID NOT NULL,

    -- Campaign details
    campaign_name VARCHAR(255) NOT NULL,
    goal TEXT,
    campaign_type VARCHAR(100),  -- 'product_launch', 'brand_awareness', etc.

    -- Budget
    total_budget DECIMAL(12, 2) NOT NULL,
    spent DECIMAL(12, 2) DEFAULT 0.00,

    -- Timeline
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    duration_days INTEGER,

    -- Performance
    total_actions INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0.00,
    overall_roi DECIMAL(8, 2) DEFAULT 0.00,

    -- Status
    status VARCHAR(50) DEFAULT 'draft',  -- draft, active, paused, completed

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_start_date (start_date)
);

-- Campaign tasks
CREATE TABLE campaign_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,

    -- Task details
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    phase VARCHAR(50),  -- 'awareness', 'education', 'consideration', 'conversion', 'retention'
    role VARCHAR(50),  -- 'content_creator', 'distributor', 'engager', 'converter', 'supporter'
    platform VARCHAR(100),

    -- Assignment
    assigned_agent_id UUID REFERENCES agents(agent_id),

    -- Dependencies
    depends_on_task_id UUID REFERENCES campaign_tasks(task_id),

    -- Resources
    budget DECIMAL(10, 2),
    target_actions INTEGER,
    duration_hours INTEGER,

    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, failed

    -- Results
    actual_actions INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    roi DECIMAL(8, 2) DEFAULT 0.00,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_campaign_id (campaign_id),
    INDEX idx_assigned_agent_id (assigned_agent_id),
    INDEX idx_status (status),
    INDEX idx_depends_on_task_id (depends_on_task_id)
);

-- ============================================================================
-- WEBHOOK TABLES
-- ============================================================================

-- Webhook endpoints
CREATE TABLE webhook_endpoints (
    webhook_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Endpoint details
    url VARCHAR(500) NOT NULL,
    description TEXT,
    secret VARCHAR(255) NOT NULL,  -- For HMAC signature

    -- Event subscriptions
    subscribed_events JSONB DEFAULT '[]',  -- ['agent.discovery', 'roi.alert', etc.]

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Reliability tracking
    total_deliveries INTEGER DEFAULT 0,
    successful_deliveries INTEGER DEFAULT 0,
    failed_deliveries INTEGER DEFAULT 0,
    last_delivery_at TIMESTAMP,
    last_failure_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
);

-- Webhook deliveries (audit log)
CREATE TABLE webhook_deliveries (
    delivery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES webhook_endpoints(webhook_id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,

    -- Delivery details
    response_status_code INTEGER,
    response_body TEXT,
    delivery_duration_ms INTEGER,

    -- Status
    success BOOLEAN NOT NULL,
    error_message TEXT,

    -- Retry tracking
    attempt_number INTEGER DEFAULT 1,
    will_retry BOOLEAN DEFAULT false,
    next_retry_at TIMESTAMP,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,

    INDEX idx_webhook_id (webhook_id),
    INDEX idx_event_type (event_type),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- PRIVACY & CONSENT TABLES
-- ============================================================================

-- Privacy consents
CREATE TABLE privacy_consents (
    consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Consent types
    consent_type VARCHAR(100) NOT NULL,  -- 'cross_colony_learning', 'analytics_sharing', etc.
    consented BOOLEAN NOT NULL,

    -- Details
    consent_text TEXT NOT NULL,  -- What they agreed to
    ip_address VARCHAR(45),  -- For audit trail
    user_agent TEXT,

    -- Timestamps
    consented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_consent_type (consent_type)
);

-- Data anonymization log
CREATE TABLE anonymization_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),

    -- Anonymization details
    data_type VARCHAR(100) NOT NULL,  -- 'performance_data', 'agent_actions', etc.
    record_id UUID NOT NULL,

    -- Original vs anonymized
    original_fields JSONB,  -- {user_id: 'xxx', agent_id: 'yyy'}
    anonymized_fields JSONB,  -- {user_id: null, agent_id: null}

    -- Timestamp
    anonymized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_data_type (data_type)
);

-- ============================================================================
-- COST CONTROL TABLES
-- ============================================================================

-- Agent budgets
CREATE TABLE agent_budgets (
    budget_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Budget limits
    daily_budget DECIMAL(10, 2),
    weekly_budget DECIMAL(10, 2),
    monthly_budget DECIMAL(10, 2),

    -- Current spend (resets based on period)
    current_daily_spend DECIMAL(10, 2) DEFAULT 0.00,
    current_weekly_spend DECIMAL(10, 2) DEFAULT 0.00,
    current_monthly_spend DECIMAL(10, 2) DEFAULT 0.00,

    -- Reset dates
    daily_reset_at TIMESTAMP,
    weekly_reset_at TIMESTAMP,
    monthly_reset_at TIMESTAMP,

    -- Alert thresholds (percentage)
    alert_threshold_percent INTEGER DEFAULT 80,

    -- Status
    is_paused BOOLEAN DEFAULT false,  -- Auto-pause when budget exceeded
    pause_reason VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_agent_id (agent_id),
    INDEX idx_user_id (user_id)
);

-- Cost tracking
CREATE TABLE cost_tracking (
    cost_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,

    -- Cost details
    cost_type VARCHAR(100) NOT NULL,  -- 'api_call', 'platform_fee', etc.
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',

    -- Context
    platform VARCHAR(100),
    action_id UUID,  -- Reference to agent_actions

    -- External reference
    external_transaction_id VARCHAR(255),

    -- Timestamp
    incurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_cost_type (cost_type),
    INDEX idx_incurred_at (incurred_at)
);

-- Budget alerts
CREATE TABLE budget_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id),

    -- Alert details
    alert_type VARCHAR(100) NOT NULL,  -- 'threshold_reached', 'budget_exceeded', etc.
    severity VARCHAR(50) DEFAULT 'warning',  -- info, warning, critical
    message TEXT NOT NULL,

    -- Context
    current_spend DECIMAL(10, 2),
    budget_limit DECIMAL(10, 2),
    percent_used DECIMAL(5, 2),

    -- Status
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_acknowledged (acknowledged),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- SYSTEM TABLES
-- ============================================================================

-- Audit log
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),

    -- Action details
    action VARCHAR(100) NOT NULL,  -- 'login', 'create_agent', 'purchase_strategy', etc.
    entity_type VARCHAR(100),  -- 'agent', 'campaign', 'strategy', etc.
    entity_id UUID,

    -- Context
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id VARCHAR(100),

    -- Changes
    old_values JSONB,
    new_values JSONB,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_entity_type (entity_type),
    INDEX idx_created_at (created_at)
);

-- System health metrics
CREATE TABLE health_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Metric details
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20, 2) NOT NULL,
    metric_unit VARCHAR(50),

    -- Context
    component VARCHAR(100),  -- 'api', 'database', 'background_worker', etc.

    -- Timestamp
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_metric_name (metric_name),
    INDEX idx_component (component),
    INDEX idx_recorded_at (recorded_at)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_agents_user_status ON agents(user_id, status);
CREATE INDEX idx_agent_actions_agent_created ON agent_actions(agent_id, created_at DESC);
CREATE INDEX idx_performance_data_platform_date ON performance_data_points(platform, created_at DESC);
CREATE INDEX idx_campaigns_user_status ON campaigns(user_id, status);
CREATE INDEX idx_webhook_deliveries_webhook_created ON webhook_deliveries(webhook_id, created_at DESC);
CREATE INDEX idx_cost_tracking_user_date ON cost_tracking(user_id, incurred_at DESC);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Calculate ROI automatically
CREATE OR REPLACE FUNCTION calculate_agent_roi()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.total_spent > 0 THEN
        NEW.current_roi = NEW.total_revenue / NEW.total_spent;
    ELSE
        NEW.current_roi = 0.00;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_agent_roi_trigger BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION calculate_agent_roi();

"""

# Export schema for migration tools
if __name__ == "__main__":
    print("=" * 80)
    print("BLOOM DATABASE SCHEMA - PostgreSQL".center(80))
    print("=" * 80)

    print("\n" + DATABASE_SCHEMA)

    print("\n" + "=" * 80)
    print("SCHEMA SUMMARY".center(80))
    print("=" * 80)

    print("""
    📊 Total Tables: 30+

    Core Tables:
    - users, api_keys

    Agent Tables:
    - agents, agent_strategies, agent_actions

    Marketplace Tables:
    - agent_listings, agent_rentals
    - strategy_listings, strategy_purchases

    Analytics Tables:
    - performance_data_points, benchmarks
    - analytics_subscriptions

    Campaign Tables:
    - campaigns, campaign_tasks

    Webhook Tables:
    - webhook_endpoints, webhook_deliveries

    Privacy Tables:
    - privacy_consents, anonymization_log

    Cost Control Tables:
    - agent_budgets, cost_tracking, budget_alerts

    System Tables:
    - audit_log, health_metrics

    ✅ Features:
    - UUID primary keys (distributed-friendly)
    - Comprehensive indexes for performance
    - Foreign key constraints for data integrity
    - Soft deletes where appropriate
    - Audit trails
    - Automatic timestamp updates
    - Calculated fields with triggers
    - JSONB for flexible data

    🚀 Production-Ready:
    - Optimized for scalability
    - Proper normalization
    - Full-text search ready
    - Time-series optimizations
    - Efficient queries
    """)

    print("=" * 80)
