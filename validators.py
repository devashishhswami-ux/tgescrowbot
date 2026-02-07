"""
Crypto Address Validators
Validates BTC, LTC, USDT (TRC20), USDT (BEP20), and TON addresses
"""
import re

# Crypto address regex patterns
PATTERNS = {
    'BTC': r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$',
    'LTC': r'^(L|M)[a-km-zA-HJ-NP-Z1-9]{26,33}$',
    'USDT_TRC20': r'^T[A-Za-z1-9]{33}$',
    'USDT_BEP20': r'^0x[a-fA-F0-9]{40}$',
    'TON': r'^EQ[a-zA-Z0-9_-]{46}$'
}

def validate_crypto_address(address):
    """
    Validate a crypto address against known patterns.
    
    Args:
        address (str): The crypto address to validate
        
    Returns:
        tuple: (is_valid, coin_type) - is_valid is bool, coin_type is str or None
    """
    if not address or not isinstance(address, str):
        return (False, None)
    
    address = address.strip()
    
    for coin_type, pattern in PATTERNS.items():
        if re.match(pattern, address):
            return (True, coin_type)
    
    return (False, None)

def get_supported_coins():
    """Returns a list of supported coin types"""
    return list(PATTERNS.keys())
