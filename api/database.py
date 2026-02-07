import os
from supabase import create_client, Client
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL_HERE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY_HERE")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def set_config(key, value):
    """Set configuration value"""
    try:
        supabase.table('config').upsert({'key': key, 'value': value}).execute()
    except Exception as e:
        print(f"Error setting config: {e}")

def get_config(key):
    """Get configuration value"""
    try:
        result = supabase.table('config').select('value').eq('key', key).execute()
        return result.data[0]['value'] if result.data else None
    except Exception as e:
        print(f"Error getting config: {e}")
        return None

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

def update_deal_address(deal_id, role, address):
    """Update buyer or seller address for a deal"""
    try:
        if role == 'buyer':
            supabase.table('deals').update({'buyer_address': address}).eq('deal_id', deal_id).execute()
        elif role == 'seller':
            supabase.table('deals').update({'seller_address': address}).eq('deal_id', deal_id).execute()
    except Exception as e:
        print(f"Error updating deal address: {e}")

def get_deal_by_group(group_id):
    """Get deal information by group ID"""
    try:
        result = supabase.table('deals').select('*').eq('group_id', group_id).execute()
        if result.data:
            d = result.data[0]
            return (d['deal_id'], d['buyer_id'], d['seller_id'], d['buyer_address'], 
                   d['seller_address'], d['bot_address'], d['status'])
        return None
    except Exception as e:
        print(f"Error getting deal: {e}")
        return None

def get_statistics():
    """Get current bot statistics"""
    try:
        result = supabase.table('statistics').select('*').execute()
        return {row['key']: row['value'] for row in result.data}
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}

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

def get_all_users():
    """Get all users who started the bot"""
    try:
        result = supabase.table('bot_users').select('*').order('started_at', desc=True).execute()
        return [(u['user_id'], u['username'], u['first_name'], u['last_name'], u['started_at']) 
                for u in result.data]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

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

def get_media_file(file_type):
    """Get media file path by type"""
    try:
        result = supabase.table('media_files').select('file_path').eq('file_type', file_type).order('uploaded_at', desc=True).limit(1).execute()
        return result.data[0]['file_path'] if result.data else None
    except Exception as e:
        print(f"Error getting media file: {e}")
        return None

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

def get_content(key, default=""):
    """Get editable content"""
    try:
        result = supabase.table('editable_content').select('content').eq('key', key).execute()
        return result.data[0]['content'] if result.data else default
    except Exception as e:
        print(f"Error getting content: {e}")
        return default

def get_all_media():
    """Get all media files"""
    try:
        result = supabase.table('media_files').select('*').order('uploaded_at', desc=True).execute()
        return [(m['file_type'], m['file_path'], m['description'], m['uploaded_at']) 
                for m in result.data]
    except Exception as e:
        print(f"Error getting all media: {e}")
        return []

def increment_stat(key):
    """Increment a statistic"""
    try:
        result = supabase.table('statistics').select('value').eq('key', key).execute()
        if result.data:
            new_value = result.data[0]['value'] + 1
            supabase.table('statistics').update({'value': new_value}).eq('key', key).execute()
    except Exception as e:
        print(f"Error incrementing stat: {e}")
