-- Supabase SQL Schema for Escrow Bot
-- Run this in your Supabase SQL Editor

-- Users table (buyer/seller roles)
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    role TEXT,
    wallet_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Deals table
CREATE TABLE IF NOT EXISTS deals (
    deal_id TEXT PRIMARY KEY,
    buyer_id BIGINT,
    seller_id BIGINT,
    buyer_address TEXT,
    seller_address TEXT,
    bot_address TEXT,
    amount DECIMAL,
    group_id BIGINT,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Config table
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Statistics table
CREATE TABLE IF NOT EXISTS statistics (
    key TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bot users table (all users who started the bot)
CREATE TABLE IF NOT EXISTS bot_users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    started_at TIMESTAMP DEFAULT NOW()
);

-- Media files table
CREATE TABLE IF NOT EXISTS media_files (
    id SERIAL PRIMARY KEY,
    file_type TEXT,
    file_path TEXT,
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Editable content table
CREATE TABLE IF NOT EXISTS editable_content (
    key TEXT PRIMARY KEY,
    content TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default config
INSERT INTO config (key, value) VALUES 
    ('admin_username', 'MiddleCryptoSupport'),
    ('admin_password', 'admin123')
ON CONFLICT (key) DO NOTHING;

-- Insert default statistics
INSERT INTO statistics (key, value) VALUES 
    ('total_deals', 5542),
    ('disputes_resolved', 158)
ON CONFLICT (key) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_group_id ON deals(group_id);
CREATE INDEX IF NOT EXISTS idx_bot_users_username ON bot_users(username);
CREATE INDEX IF NOT EXISTS idx_media_files_type ON media_files(file_type);
