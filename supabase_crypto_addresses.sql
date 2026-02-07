-- Crypto Addresses Table
CREATE TABLE IF NOT EXISTS crypto_addresses (
    id BIGSERIAL PRIMARY KEY,
    currency VARCHAR(10) NOT NULL,
    address TEXT NOT NULL,
    network VARCHAR(50) DEFAULT '',
    label VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_crypto_addresses_currency ON crypto_addresses(currency);
CREATE INDEX IF NOT EXISTS idx_crypto_addresses_network ON crypto_addresses(currency, network);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_crypto_addresses_updated_at BEFORE UPDATE ON crypto_addresses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
