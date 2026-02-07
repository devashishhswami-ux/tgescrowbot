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

def get_credentials():
    """
    Get Telethon credentials from environment or database
    Returns: (api_id, api_hash) or (None, None)
    """
    # Try environment first
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    
    # If not in env, try database
    if not api_id or not api_hash:
        try:
            api_id = database.get_config('telegram_api_id')
            api_hash = database.get_config('telegram_api_hash')
        except Exception as e:
            logger.error(f"Error fetching API credentials from DB: {e}")
            
    if api_id and api_hash:
        try:
            return int(api_id), api_hash
        except ValueError:
            logger.error("API_ID must be an integer")
            return None, None
            
    logger.warning("API_ID or API_HASH not found in env or DB")
    return None, None

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
    """
    # Get credentials dynamically
    api_id, api_hash = get_credentials()
    
    if not api_id or not api_hash:
        return {
            'success': False,
            'error': 'Configuration Error: API ID or Hash is missing. Please set them in the Admin Dashboard > Settings > Telegram.'
        }
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
            api_id,
            api_hash
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

        # ------------------------------------------------------------------
        # ADD BOT AND PROMOTE TO ADMIN
        # ------------------------------------------------------------------
        if bot_username:
            try:
                # 1. Invite Bot
                from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
                from telethon.tl.types import ChatAdminRights
                
                logger.info(f"🤖 Adding bot @{bot_username} to group...")
                await client(InviteToChannelRequest(group_id, [bot_username]))
                
                # 2. Promote Bot to Admin
                # Give full rights (delete msgs, pin, invite, etc)
                rights = ChatAdminRights(
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=False,
                    anonymous=False,
                    manage_call=False,
                    other=True
                )
                
                logger.info(f"👑 Promoting bot @{bot_username} to Admin...")
                await client(EditAdminRequest(
                    channel=group_id,
                    user_id=bot_username,
                    admin_rights=rights,
                    rank="Escrow Bot"
                ))
                logger.info("✅ Bot added and promoted successfully!")
                
            except Exception as bot_err:
                logger.error(f"⚠️ Failed to add/promote bot: {bot_err}")
                # Continue execution, don't fail the whole process
        # ------------------------------------------------------------------
        
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
