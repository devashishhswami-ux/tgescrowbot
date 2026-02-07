"""
Telethon Microservice for Telegram Group Creation
Runs as a separate Flask service to avoid event loop conflicts with main bot
"""
import os
import logging
from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChatAdminRights
from dotenv import load_dotenv
import asyncio
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telethon configuration
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')

# Global Telethon client and event loop
client = None
loop = None
loop_thread = None

def run_async_loop(loop):
    """Run event loop in background thread"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def run_coroutine_threadsafe(coro):
    """Run a coroutine in the background event loop thread"""
    global loop
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

async def init_client():
    """Initialize Telethon client"""
    global client
    if client is None or not client.is_connected():
        client = TelegramClient('user_session', API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            logger.error("Telethon client not authorized! Run auth_telethon.py first.")
            raise Exception("Client not authorized")
        logger.info("Telethon client initialized and authorized")
    return client

async def create_telegram_group_async(buyer_id, seller_id, bot_username, deal_id):
    """
    Create a Telegram group for escrow with anonymous creator and bot as admin
    
    Returns:
        tuple: (group_id, invite_link)
    """
    try:
        await init_client()
        
        logger.info(f"Creating group for deal #{deal_id}")
        
        # Create a private supergroup
        result = await client(CreateChannelRequest(
            title=f"Escrow #{deal_id}",
            about="Secure escrow transaction managed by Middle Crypto Bot",
            megagroup=True
        ))
        
        group = result.chats[0]
        group_id = group.id
        logger.info(f"✅ Created group: {group_id}")
        
        # Get channel entity
        channel_entity = await client.get_entity(group_id)
        
        # Step 1: Make creator anonymous
        try:
            me = await client.get_me()
            
            my_admin_rights = ChatAdminRights(
                change_info=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True,
                manage_call=True,
                anonymous=True
            )
            
            # Using positional arguments for EditAdminRequest
            await client(EditAdminRequest(
                channel_entity,
                me,
                my_admin_rights,
                f"Escrow #{deal_id}"
            ))
            logger.info(f"✅ Made creator anonymous")
            
        except Exception as anon_error:
            logger.warning(f"Could not make creator anonymous: {anon_error}")
        
        # Step 2: Add bot and promote to admin
        try:
            # Ensure bot username has @ prefix
            if not bot_username.startswith('@'):
                bot_username = f'@{bot_username}'
            
            logger.info(f"Adding bot: {bot_username}")
            
            # Get bot entity
            bot_entity = await client.get_entity(bot_username)
            logger.info(f"Got bot entity ID: {bot_entity.id}")
            
            # Invite bot to channel
            await client(InviteToChannelRequest(
                channel=channel_entity,
                users=[bot_entity]
            ))
            logger.info(f"✅ Bot added to group")
            
            # Promote bot to admin
            bot_admin_rights = ChatAdminRights(
                change_info=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False,
                manage_call=True,
                anonymous=False  # User said NOT for the bot
            )
            
            # Using positional arguments for EditAdminRequest
            await client(EditAdminRequest(
                channel_entity,
                bot_entity,
                bot_admin_rights,
                "Admin"
            ))
            logger.info(f"✅ Bot promoted to admin")
            
            # Wait for permissions to take effect
            await asyncio.sleep(2)
            
        except Exception as bot_error:
            logger.error(f"❌ Error adding/promoting bot: {bot_error}")
            import traceback
            traceback.print_exc()
            raise
        
        # Step 3: Send /start command automatically
        try:
            await client.send_message(channel_entity, '/start')
            logger.info(f"✅ Sent /start command")
            await asyncio.sleep(2)  # Wait for bot to process and respond
        except Exception as start_error:
            logger.warning(f"Could not send /start: {start_error}")
        
        # Step 4: Export invite link
        invite = await client(ExportChatInviteRequest(channel_entity))
        invite_link = invite.link
        logger.info(f"✅ Invite link: {invite_link}")
        
        return group_id, invite_link
        
    except Exception as e:
        logger.error(f"❌ Error creating group: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        is_connected = client is not None and client.is_connected()
        return jsonify({
            'status': 'ok',
            'telethon': 'connected' if is_connected else 'disconnected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/create-group', methods=['POST'])
def create_group():
    """Create a Telegram group with anonymous creator and bot as admin"""
    try:
        data = request.get_json()
        
        # Validate request
        required_fields = ['buyer_id', 'seller_id', 'bot_username', 'deal_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        buyer_id = data['buyer_id']
        seller_id = data['seller_id']
        bot_username = data['bot_username']
        deal_id = data['deal_id']
        
        # Create group using background event loop
        group_id, invite_link = run_coroutine_threadsafe(
            create_telegram_group_async(buyer_id, seller_id, bot_username, deal_id)
        )
        
        return jsonify({
            'success': True,
            'group_id': group_id,
            'invite_link': invite_link,
            'deal_id': deal_id
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in create_group endpoint:\n{error_traceback}")
        return jsonify({
            'success': False,
            'error': f"{str(e)}\n\nTraceback:\n{error_traceback}"
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Telethon Microservice Starting...")
    print("📍 URL: http://localhost:5001")
    print("🔐 Using session: user_session.session")
    print("=" * 60)
    
    # Start event loop in background thread
    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=run_async_loop, args=(loop,), daemon=True)
    loop_thread.start()
    logger.info("✅ Background event loop started")
    
    # Initialize client
    try:
        run_coroutine_threadsafe(init_client())
        logger.info("✅ Telethon client pre-initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)
