-- =============================================
-- COMPLETE SUPABASE SETUP - RUN THIS ONCE
-- Telegram Escrow Bot Database
-- =============================================

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    role VARCHAR(20),
    wallet_address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. BOT_USERS TABLE  
CREATE TABLE IF NOT EXISTS bot_users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. DEALS TABLE
CREATE TABLE IF NOT EXISTS deals (
    id BIGSERIAL PRIMARY KEY,
    deal_id VARCHAR(50) UNIQUE NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    group_id BIGINT,
    buyer_address TEXT,
    seller_address TEXT,
    bot_address TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. STATISTICS TABLE
CREATE TABLE IF NOT EXISTS statistics (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO statistics (key, value) VALUES 
    ('total_deals', 5542),
    ('disputes_resolved', 158)
ON CONFLICT (key) DO NOTHING;

-- 5. CONFIG TABLE
CREATE TABLE IF NOT EXISTS config (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO config (key, value) VALUES 
    ('admin_username', 'MiddleCryptoSupport')
ON CONFLICT (key) DO NOTHING;

-- 6. MEDIA_FILES TABLE
CREATE TABLE IF NOT EXISTS media_files (
    id BIGSERIAL PRIMARY KEY,
    file_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 7. EDITABLE_CONTENT TABLE
CREATE TABLE IF NOT EXISTS editable_content (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    content TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 8. CRYPTO_ADDRESSES TABLE
CREATE TABLE IF NOT EXISTS crypto_addresses (
    id BIGSERIAL PRIMARY KEY,
    currency VARCHAR(10) NOT NULL,
    address TEXT NOT NULL,
    network VARCHAR(50) DEFAULT '',
    label VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- CREATE INDEXES
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_bot_users_username ON bot_users(username);
CREATE INDEX IF NOT EXISTS idx_deals_deal_id ON deals(deal_id);
CREATE INDEX IF NOT EXISTS idx_deals_group_id ON deals(group_id);
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status);
CREATE INDEX IF NOT EXISTS idx_media_files_type ON media_files(file_type);
CREATE INDEX IF NOT EXISTS idx_crypto_addresses_currency ON crypto_addresses(currency);
CREATE INDEX IF NOT EXISTS idx_crypto_addresses_network ON crypto_addresses(currency, network);

-- AUTO-UPDATE TRIGGERS
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bot_users_updated_at BEFORE UPDATE ON bot_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_statistics_updated_at BEFORE UPDATE ON statistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_config_updated_at BEFORE UPDATE ON config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_editable_content_updated_at BEFORE UPDATE ON editable_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_crypto_addresses_updated_at BEFORE UPDATE ON crypto_addresses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- VERIFICATION
SELECT 'SUCCESS: All tables created!' AS status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
