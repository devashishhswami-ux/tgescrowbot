"""
Telegram Group Manager
Creates escrow groups using admin session from Supabase database
"""
import os
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl.types import InputPeerUser
import database

logger = logging.getLogger(__name__)

# Get Telethon credentials from environment or database
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

if not API_ID or not API_HASH:
    try:
        API_ID = database.get_config('telegram_api_id')
        API_HASH = database.get_config('telegram_api_hash')
        if API_ID:
            API_ID = int(API_ID)
    except Exception as e:
        logger.error(f"Error fetching API credentials from DB: {e}")

if not API_ID or not API_HASH:
    # Default placeholder or error
    API_ID = 0
    API_HASH = ''
    logger.warning("API_ID or API_HASH not found in env or DB")
else:
    API_ID = int(API_ID)

def get_admin_session():
    """
    Fetch the most recent admin Telegram session from Supabase
    Returns: session_string or None
    """
    try:
        session_data = database.get_telegram_admin_session()
        if session_data and session_data.get('session_string'):
            logger.info(f"✅ Found admin session for User ID: {session_data.get('user_id')}")
            return session_data['session_string']
        else:
            logger.error("❌ No admin Telegram session found in database")
            return None
    except Exception as e:
        logger.error(f"❌ Error fetching admin session: {e}")
        return None

async def create_escrow_group(deal_id, bot_username=None):
    """
    Create a Telegram escrow group using admin session
    
    Args:
        deal_id: Unique identifier for this deal
        bot_username: Username of the bot (without @)
    
    Returns:
        dict: {
            'success': bool,
            'group_id': int,
            'invite_link': str,
            'error': str (if failed)
        }
    """
    client = None
    try:
        # Get admin session from database
        session_string = get_admin_session()
        if not session_string:
            return {
                'success': False,
                'error': 'No admin session found. Please login via admin panel first.'
            }
        
        # Create Telethon client from session
        client = TelegramClient(
            StringSession(session_string),
            API_ID,
            API_HASH
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            return {
                'success': False,
                'error': 'Admin session expired. Please re-login via admin panel.'
            }
        
        # Create the escrow group
        logger.info(f"🔨 Creating escrow group for deal #{deal_id}...")
        
        result = await client(CreateChannelRequest(
            title=f"Escrow #{deal_id}",
            about=f"Escrow transaction #{deal_id}",
            megagroup=True  # Create as supergroup
        ))
        
        # Get the created group
        group = result.chats[0]
        group_id = group.id
        
        logger.info(f"✅ Group created! ID: {group_id}")
        
        # Get invite link
        try:
            full_channel = await client.get_entity(group_id)
            if hasattr(full_channel, 'username') and full_channel.username:
                invite_link = f"https://t.me/{full_channel.username}"
            else:
                # Create invite link
                from telethon.tl.functions.messages import ExportChatInviteRequest
                invite_result = await client(ExportChatInviteRequest(peer=group_id))
                invite_link = invite_result.link
        except Exception as link_error:
            # Fallback: try to export invite
            logger.warning(f"Could not get channel entity, exporting invite: {link_error}")
            from telethon.tl.functions.messages import ExportChatInviteRequest
            invite_result = await client(ExportChatInviteRequest(peer=group_id))
            invite_link = invite_result.link
        
        logger.info(f"🔗 Invite link: {invite_link}")
        
        await client.disconnect()
        
        return {
            'success': True,
            'group_id': group_id,
            'invite_link': invite_link
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating escrow group: {e}")
        if client and client.is_connected():
            await client.disconnect()
        
        return {
            'success': False,
            'error': str(e)
        }

def format_group_created_message(deal_id, invite_link):
    """
    Format the success message when a group is created
    Matches the reference bot format
    """
    return f"""<b>Created Escrow Group #{deal_id}</b>

<b>Group Link:</b> {invite_link}

Now Join this escrow group & Forward this message to buyer/seller.

Enjoy Safe Escrow 🍻"""
