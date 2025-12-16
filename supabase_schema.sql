-- ============================================================================
-- Nonprofit CRM Database Schema for Supabase
-- ============================================================================
-- This SQL file creates all necessary tables for the Nonprofit CRM system
-- Run this in your Supabase SQL Editor: https://app.supabase.com/project/_/sql
-- ============================================================================

-- Drop existing tables if they exist (optional - comment out if you want to preserve data)
-- DROP TABLE IF EXISTS opportunities CASCADE;
-- DROP TABLE IF EXISTS interactions CASCADE;
-- DROP TABLE IF EXISTS contributions CASCADE;
-- DROP TABLE IF EXISTS constituents CASCADE;

-- ============================================================================
-- CONSTITUENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS constituents (
    constituent_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    constituent_type VARCHAR(50) NOT NULL CHECK (constituent_type IN ('donor', 'volunteer', 'board_member', 'staff', 'other')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deceased')),
    notes TEXT,
    created_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_lifetime_giving NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for constituents
CREATE INDEX IF NOT EXISTS idx_constituents_email ON constituents(email);
CREATE INDEX IF NOT EXISTS idx_constituents_type ON constituents(constituent_type);
CREATE INDEX IF NOT EXISTS idx_constituents_created_date ON constituents(created_date);
CREATE INDEX IF NOT EXISTS idx_constituents_name ON constituents(last_name, first_name);

-- ============================================================================
-- CONTRIBUTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS contributions (
    contribution_id SERIAL PRIMARY KEY,
    constituent_id INTEGER NOT NULL REFERENCES constituents(constituent_id) ON DELETE CASCADE ON UPDATE CASCADE,
    contribution_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    contribution_type VARCHAR(50) NOT NULL CHECK (contribution_type IN ('cash', 'check', 'credit_card', 'stock', 'in_kind', 'other')),
    campaign VARCHAR(100),
    appeal VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for contributions
CREATE INDEX IF NOT EXISTS idx_contributions_constituent ON contributions(constituent_id);
CREATE INDEX IF NOT EXISTS idx_contributions_date ON contributions(contribution_date);
CREATE INDEX IF NOT EXISTS idx_contributions_campaign ON contributions(campaign);
CREATE INDEX IF NOT EXISTS idx_contributions_type ON contributions(contribution_type);
CREATE INDEX IF NOT EXISTS idx_contributions_amount ON contributions(amount);

-- ============================================================================
-- INTERACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id SERIAL PRIMARY KEY,
    constituent_id INTEGER NOT NULL REFERENCES constituents(constituent_id) ON DELETE CASCADE ON UPDATE CASCADE,
    interaction_date TIMESTAMP NOT NULL,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('email', 'phone', 'meeting', 'event', 'letter', 'other')),
    subject VARCHAR(200) NOT NULL,
    notes TEXT,
    outcome VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for interactions
CREATE INDEX IF NOT EXISTS idx_interactions_constituent ON interactions(constituent_id);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);

-- ============================================================================
-- OPPORTUNITIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    constituent_id INTEGER NOT NULL REFERENCES constituents(constituent_id) ON DELETE CASCADE ON UPDATE CASCADE,
    opportunity_name VARCHAR(200) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    probability INTEGER NOT NULL CHECK (probability >= 0 AND probability <= 100),
    stage VARCHAR(50) NOT NULL CHECK (stage IN ('prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost')),
    expected_close_date DATE NOT NULL,
    campaign VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for opportunities
CREATE INDEX IF NOT EXISTS idx_opportunities_constituent ON opportunities(constituent_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(stage);
CREATE INDEX IF NOT EXISTS idx_opportunities_close_date ON opportunities(expected_close_date);
CREATE INDEX IF NOT EXISTS idx_opportunities_amount ON opportunities(amount);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional but recommended for production
-- ============================================================================
-- Enable Row Level Security on all tables
ALTER TABLE constituents ENABLE ROW LEVEL SECURITY;
ALTER TABLE contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (adjust as needed for your security requirements)
-- These policies allow all authenticated users to read and write all data
-- You may want to customize these based on your specific needs

CREATE POLICY "Enable read access for authenticated users" ON constituents
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON constituents
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users" ON constituents
    FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users" ON constituents
    FOR DELETE TO authenticated USING (true);

CREATE POLICY "Enable read access for authenticated users" ON contributions
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON contributions
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users" ON contributions
    FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users" ON contributions
    FOR DELETE TO authenticated USING (true);

CREATE POLICY "Enable read access for authenticated users" ON interactions
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON interactions
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users" ON interactions
    FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users" ON interactions
    FOR DELETE TO authenticated USING (true);

CREATE POLICY "Enable read access for authenticated users" ON opportunities
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON opportunities
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Enable update access for authenticated users" ON opportunities
    FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable delete access for authenticated users" ON opportunities
    FOR DELETE TO authenticated USING (true);

-- ============================================================================
-- HELPER FUNCTION: Update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at columns
CREATE TRIGGER update_constituents_updated_at
    BEFORE UPDATE ON constituents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Check that all tables were created successfully
SELECT
    table_name,
    table_type
FROM
    information_schema.tables
WHERE
    table_schema = 'public'
    AND table_name IN ('constituents', 'contributions', 'interactions', 'opportunities')
ORDER BY
    table_name;

-- ============================================================================
-- DONE!
-- ============================================================================
-- Your database schema is now ready!
-- Next steps:
-- 1. Run your backend: uvicorn main:app --reload
-- 2. Load sample data: python load_data.py (if you have this script)
-- 3. Start frontend: cd frontend && npm run dev
-- ============================================================================
