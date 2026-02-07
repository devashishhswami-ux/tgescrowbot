"""
Telethon User Client for creating Telegram groups
Handles group creation and user management using a user account
"""
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl.types import InputPeerUser, InputUser
from config import API_ID, API_HASH, PHONE_NUMBER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from bot_error_wrapper import handle_errors, safe_call

# Initialize Telethon client
client = None

@handle_errors
async def init_user_client():
    """Initialize the Telethon user client"""
    global client
    if client is None:
        client = TelegramClient('user_session', API_ID, API_HASH)
        await client.start(phone=PHONE_NUMBER)
        logger.info("Telethon user client initialized")
    return client

@handle_errors
async def create_escrow_group(buyer_id, seller_id, bot_username, deal_id):
    """
    Create a private supergroup for escrow
    
    Args:
        buyer_id: Telegram user ID of the buyer
        seller_id: Telegram user ID of the seller
        bot_username: Username of the bot (without @)
        deal_id: Unique deal identifier
        
    Returns:
        group_id: The created group's ID
    """
    try:
        await init_user_client()
        
        # Create a private supergroup
        result = await client(CreateChannelRequest(
            title=f"Escrow Deal #{deal_id}",
            about="Secure escrow transaction managed by Middle Crypto Bot",
            megagroup=True  # Create as supergroup
        ))
        
        group = result.chats[0]
        group_id = group.id
        logger.info(f"Created escrow group: {group_id}")
        
        # Export invite link FIRST before trying to add anyone
        invite_link = None
        try:
            from telethon.tl.functions.messages import ExportChatInviteRequest
            channel_entity = await client.get_entity(group_id)
            invite = await client(ExportChatInviteRequest(channel_entity))
            invite_link = invite.link
            logger.info(f"Exported invite link: {invite_link}")
        except Exception as e:
            logger.error(f"Error exporting invite link: {e}")
            # Try alternative method
            try:
                invite_link = f"https://t.me/c/{str(group_id)[4:]}/"
            except:
                invite_link = "Contact admin for invite"
        
        # Return both group_id and invite_link 
        # We can't add them directly, they'll join via the link
        return group_id, invite_link
        
    except Exception as e:
        logger.error(f"Error creating escrow group: {e}")
        raise


@handle_errors
async def add_user_to_group(group_id, user_id):
    """
    Add a user (e.g., admin) to an existing group
    
    Args:
        group_id: The group ID
        user_id: The user ID to add
    """
    try:
        await init_user_client()
        
        # Get the group entity
        group = await client.get_entity(group_id)
        
        # Add user to the group
        await client(InviteToChannelRequest(
            channel=group,
            users=[user_id]
        ))
        
        logger.info(f"Added user {user_id} to group {group_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding user to group: {e}")
        return False

@handle_errors
async def close_user_client():
    """Close the Telethon client"""
    global client
    if client:
        await client.disconnect()
        logger.info("Telethon client disconnected")
