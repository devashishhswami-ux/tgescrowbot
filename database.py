import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL_HERE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

from bot_error_wrapper import safe_call

@safe_call
def init_db():
    """Initialize database tables in Supabase"""
    # Tables are created via Supabase dashboard or SQL editor
    # This function can be used to insert default data
    try:
        # Check if config exists, if not insert defaults
        result = supabase.table('config').select('*').eq('key', 'admin_username').execute()
        if not result.data:
            supabase.table('config').insert([
                {'key': 'admin_username', 'value': 'MiddleCryptoSupport'},
                {'key': 'admin_password', 'value': 'admin123'}
            ]).execute()
        
        # Check if statistics exist
        result = supabase.table('statistics').select('*').eq('key', 'total_deals').execute()
        if not result.data:
            supabase.table('statistics').insert([
                {'key': 'total_deals', 'value': 5542},
                {'key': 'disputes_resolved', 'value': 158}
            ]).execute()
        
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database init error: {e}")

@safe_call
def set_user_role(user_id, role, address):
    """Set user role and wallet address"""
    try:
        supabase.table('users').upsert({
            'user_id': user_id,
            'role': role,
            'wallet_address': address
        }).execute()
    except Exception as e:
        print(f"Error setting user role: {e}")

@safe_call
def get_user_role(user_id):
    """Get user role and wallet address"""
    try:
        result = supabase.table('users').select('role, wallet_address').eq('user_id', user_id).execute()
        if result.data:
            return (result.data[0]['role'], result.data[0]['wallet_address'])
        return None
    except Exception as e:
        print(f"Error getting user role: {e}")
        return None

@safe_call
def set_config(key, value):
    """Set configuration value"""
    try:
        supabase.table('config').upsert({'key': key, 'value': value}).execute()
    except Exception as e:
        print(f"Error setting config: {e}")

# Alias for compatibility
update_config = set_config

@safe_call
def get_config(key):
    """Get configuration value"""
    try:
        result = supabase.table('config').select('value').eq('key', key).execute()
        return result.data[0]['value'] if result.data else None
    except Exception as e:
        print(f"Error getting config: {e}")
        return None

@safe_call
def create_deal(deal_id, buyer_id, seller_id, group_id):
    """Create a new escrow deal"""
    try:
        supabase.table('deals').insert({
            'deal_id': deal_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'group_id': group_id,
            'status': 'active'
        }).execute()
    except Exception as e:
        print(f"Error creating deal: {e}")

@safe_call
def update_deal_address(deal_id, role, address, user_id=None):
    """Update buyer or seller address AND user_id for a deal"""
    try:
        data = {}
        if role == 'buyer':
            data['buyer_address'] = address
            if user_id:
                data['buyer_id'] = user_id
            supabase.table('deals').update(data).eq('deal_id', deal_id).execute()
        elif role == 'seller':
            data['seller_address'] = address
            if user_id:
                data['seller_id'] = user_id
            supabase.table('deals').update(data).eq('deal_id', deal_id).execute()
    except Exception as e:
        print(f"Error updating deal address: {e}")

@safe_call
def get_deal_by_group(group_id):
    """Get deal information by group ID (Flexible check)"""
    try:
        # Try finding by exact group_id
        result = supabase.table('deals').select('*').eq('group_id', group_id).execute()
        
        # If not found, try alternative format (e.g. without -100 prefix)
        if not result.data:
            alt_id = int(str(group_id).replace('-100', ''))  # e.g. -100123 -> 123
            if alt_id != group_id:
                result = supabase.table('deals').select('*').eq('group_id', alt_id).execute()
                
        if result.data:
            d = result.data[0]
            return (d['deal_id'], d['buyer_id'], d['seller_id'], d['buyer_address'], 
                   d['seller_address'], d['bot_address'], d['status'])
        return None
    except Exception as e:
        print(f"Error getting deal: {e}")
        return None

@safe_call
def get_statistics():
    """Get current bot statistics"""
    try:
        result = supabase.table('statistics').select('*').execute()
        return {row['key']: row['value'] for row in result.data}
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}

@safe_call
def track_user(user_id, username, first_name, last_name=None):
    """Track user who started the bot"""
    try:
        supabase.table('bot_users').upsert({
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }).execute()
    except Exception as e:
        print(f"Error tracking user: {e}")

@safe_call
def get_all_users():
    """Get all users who started the bot"""
    try:
        result = supabase.table('bot_users').select('*').order('started_at', desc=True).execute()
        return [(u['user_id'], u['username'], u['first_name'], u['last_name'], u['started_at']) 
                for u in result.data]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

# Alias for compatibility
get_all_bot_users = get_all_users

@safe_call
def save_media_file(file_type, file_path, description=""):
    """Save media file info"""
    try:
        # Delete old file of same type
        supabase.table('media_files').delete().eq('file_type', file_type).execute()
        # Insert new
        supabase.table('media_files').insert({
            'file_type': file_type,
            'file_path': file_path,
            'description': description
        }).execute()
    except Exception as e:
        print(f"Error saving media file: {e}")

@safe_call
def get_media_file(file_type):
    """Get media file path by type"""
    try:
        result = supabase.table('media_files').select('file_path').eq('file_type', file_type).order('uploaded_at', desc=True).limit(1).execute()
        return result.data[0]['file_path'] if result.data else None
    except Exception as e:
        print(f"Error getting media file: {e}")
        return None

@safe_call
def update_content(key, content):
    """Update editable content"""
    try:
        supabase.table('editable_content').upsert({
            'key': key,
            'content': content,
            'updated_at': datetime.now().isoformat()
        }).execute()
    except Exception as e:
        print(f"Error updating content: {e}")

@safe_call
def get_content(key, default=""):
    """Get editable content"""
    try:
        result = supabase.table('editable_content').select('content').eq('key', key).execute()
        return result.data[0]['content'] if result.data else default
    except Exception as e:
        print(f"Error getting content: {e}")
        return default

@safe_call
def get_all_media():
    """Get all media files"""
    try:
        result = supabase.table('media_files').select('*').order('uploaded_at', desc=True).execute()
        return [(m['file_type'], m['file_path'], m['description'], m['uploaded_at']) 
                for m in result.data]
    except Exception as e:
        print(f"Error getting all media: {e}")
        return []

@safe_call
def increment_stat(key):
    """Increment a statistic"""
    try:
        result = supabase.table('statistics').select('value').eq('key', key).execute()
        if result.data:
            new_value = result.data[0]['value'] + 1
            supabase.table('statistics').update({'value': new_value}).eq('key', key).execute()
    except Exception as e:
        print(f"Error incrementing stat: {e}")

# Telegram Session Management
@safe_call
def get_telegram_admin_session():
    """
    Get the most recent admin Telegram session from database
    Returns: dict with session_string, user_id, phone, etc. or None
    """
    try:
        result = supabase.table('telegram_sessions').select('*').order('updated_at', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting telegram admin session: {e}")
        return None

# -------------------------------------------------------------------------
# Merged features from api/database.py
# -------------------------------------------------------------------------

@safe_call
def update_editable_content(key, content):
    """Update editable content"""
    try:
        supabase.table('editable_content').upsert({
            'key': key,
            'content': content,
            'updated_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error updating editable content: {e}")
        return False

@safe_call
def get_all_editable_content():
    """Get all editable content"""
    try:
        result = supabase.table('editable_content').select('*').order('updated_at', desc=True).execute()
        return [(c['key'], c['content'], c['updated_at']) for c in result.data]
    except Exception as e:
        print(f"Error getting editable content: {e}")
        return []

@safe_call
def get_crypto_addresses():
    """Get all crypto addresses"""
    try:
        result = supabase.table('crypto_addresses').select('*').order('created_at', desc=True).execute()
        return [(a['id'], a['currency'], a['address'], a['network'], a['label'], a['created_at']) 
                for a in result.data]
    except Exception as e:
        print(f"Error getting crypto addresses: {e}")
        return []

@safe_call
def add_crypto_address(currency, address, network='', label=''):
    """Add a new crypto address"""
    try:
        supabase.table('crypto_addresses').insert({
            'currency': currency,
            'address': address,
            'network': network,
            'label': label
        }).execute()
        return True
    except Exception as e:
        print(f"Error adding crypto address: {e}")
        return False

@safe_call
def delete_crypto_address(address_id):
    """Delete a crypto address"""
    try:
        supabase.table('crypto_addresses').delete().eq('id', address_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting crypto address: {e}")
        return False

@safe_call
def update_crypto_address(address_id, currency, address, network='', label=''):
    """Update a crypto address"""
    try:
        supabase.table('crypto_addresses').update({
            'currency': currency,
            'address': address,
            'network': network,
            'label': label
        }).eq('id', address_id).execute()
        return True
    except Exception as e:
        print(f"Error updating crypto address: {e}")
        return False
