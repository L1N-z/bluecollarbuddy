-- Supabase Database Setup for Bob's Beehive Dashboard
-- Run this in your Supabase SQL editor

-- Enable Row Level Security (RLS)
ALTER TABLE IF EXISTS bob_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agent_settings ENABLE ROW LEVEL SECURITY;

-- Create bob_accounts table
CREATE TABLE IF NOT EXISTS bob_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT DEFAULT '',
    role_description TEXT DEFAULT '',
    profile TEXT NOT NULL,
    services_type TEXT NOT NULL DEFAULT 'pricing' CHECK (services_type IN ('pricing', 'list', 'none')),
    services JSONB DEFAULT '[]'::jsonb,
    services_not_provided TEXT DEFAULT '',
    location TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agent_settings table
CREATE TABLE IF NOT EXISTS agent_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    enabled BOOLEAN DEFAULT true,
    delay_time INTEGER DEFAULT 2 CHECK (delay_time >= 0 AND delay_time <= 10),
    default_greeting TEXT NOT NULL DEFAULT 'Hi! I''m Bob, your friendly beehive builder. How can I help you today?',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bob_accounts_created_at ON bob_accounts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_settings_created_at ON agent_settings(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_bob_accounts_updated_at 
    BEFORE UPDATE ON bob_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_settings_updated_at 
    BEFORE UPDATE ON agent_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS policies for bob_accounts
CREATE POLICY "Allow all operations on bob_accounts" ON bob_accounts
    FOR ALL USING (true);

-- Create RLS policies for agent_settings
CREATE POLICY "Allow all operations on agent_settings" ON agent_settings
    FOR ALL USING (true);

-- Insert default agent settings if table is empty
INSERT INTO agent_settings (enabled, delay_time, default_greeting)
SELECT true, 2, 'Hi! I''m Bob, your friendly beehive builder. How can I help you today?'
WHERE NOT EXISTS (SELECT 1 FROM agent_settings);

-- Grant necessary permissions
GRANT ALL ON bob_accounts TO authenticated;
GRANT ALL ON agent_settings TO authenticated;
GRANT ALL ON bob_accounts TO anon;
GRANT ALL ON agent_settings TO anon; 