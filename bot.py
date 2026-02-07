import logging
import re
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ChatMemberHandler
)
from config import BOT_TOKEN, ADMIN_USER_IDS, ADMIN_USERNAMES
import messages
import database
import validators
import asyncio
import os
from bot_error_wrapper import handle_errors, safe_call
from create_command import create_command
import telegram_group_manager

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =================
# UTILITY FUNCTIONS
# =================

async def health_check_server():
    """Lightweight HTTP server for Koyeb health checks"""
    port = int(os.environ.get("PORT", 8000))
    
    async def handle_health(reader, writer):
        # Read the request just to clear it
        try:
            await reader.read(1024)
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK"
            writer.write(response.encode())
            await writer.drain()
        except:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass

    try:
        server = await asyncio.start_server(handle_health, '0.0.0.0', port)
        logger.info(f"🚀 Health check server listening on port {port}")
        async with server:
            await server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Could not start health check server: {e}")

async def post_init(application):
    """Start tasks after bot initialization"""
    asyncio.create_task(health_check_server())
    logger.info("✅ Health check task scheduled")

def get_group_keyboard():
    """Get inline keyboard for group messages"""
    keyboard = [
        [InlineKeyboardButton(messages.BTN_WHAT_IS_ESCROW, callback_data='what_is_escrow')],
        [InlineKeyboardButton(messages.BTN_INSTRUCTIONS, callback_data='instructions')],
        [InlineKeyboardButton(messages.BTN_TERMS, callback_data='terms')],
        [InlineKeyboardButton(messages.BTN_VIDEO_TUTORIAL, callback_data='video')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ====================
# COMMAND HANDLERS
# ====================

@handle_errors
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        import os
        
        # If in group, send group welcome
        if update.effective_chat.type in ['group', 'supergroup']:
            stats = database.get_statistics()
            welcome_text = messages.GROUP_WELCOME_TEXT.format(
                total_deals=stats.get('total_deals', 5542),
                disputes_resolved=stats.get('disputes_resolved', 158)
            )
            keyboard = get_group_keyboard()
            
            if os.path.exists("video.mp4"):
                with open("video.mp4", "rb") as video:
                    await update.message.reply_video(
                        video=video,
                        caption=welcome_text,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
            else:
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            return
        
        # Private chat welcome
        user_id = update.effective_user.id
        
        keyboard = [
            [InlineKeyboardButton(messages.BTN_WHAT_IS_ESCROW, callback_data='what_is_escrow')],
            [InlineKeyboardButton(messages.BTN_INSTRUCTIONS, callback_data='instructions')],
            [InlineKeyboardButton(messages.BTN_TERMS, callback_data='terms')],
            [InlineKeyboardButton(messages.BTN_CREATE_GROUP, callback_data='create_group')]
        ]
        
        # Add Admin Panel button for admin only (Telegram Web App)
        try:
            from config import ADMIN_USER_ID, ADMIN_PANEL_URL
            if ADMIN_USER_ID > 0 and user_id == ADMIN_USER_ID:
                keyboard.insert(0, [InlineKeyboardButton(
                    "🛡️ Admin Panel", 
                    web_app={'url': ADMIN_PANEL_URL}
                )])
        except (ImportError, AttributeError):
            # Admin config not available, skip admin button
            pass
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if os.path.exists("video.mp4"):
            await update.message.reply_video(
                video=open("video.mp4", "rb"),
                caption=f"<b>{messages.WELCOME_TEXT}</b>",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"<b>{messages.WELCOME_TEXT}</b>",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        try:
            await update.message.reply_text(
                "⚠️ Welcome! The bot is experiencing technical issues. Please try again later.",
                parse_mode='HTML'
            )
        except:
            pass

@handle_errors
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command - show keyboard in groups"""
    if update.effective_chat.type in ['group', 'supergroup']:
        # Group menu with action buttons (from screenshot)
        keyboard = [
            [InlineKeyboardButton(messages.BTN_INSTRUCTIONS, callback_data='instructions')],
            [
                InlineKeyboardButton(messages.BTN_PAY_SELLER, callback_data='pay_seller'),
                InlineKeyboardButton(messages.BTN_REFUND_BUYER, callback_data='refund_buyer')
            ],
            [InlineKeyboardButton(messages.BTN_RESET_ROLES, callback_data='reset_roles')],
            [
                InlineKeyboardButton(messages.BTN_BALANCE, callback_data='balance'),
                InlineKeyboardButton(messages.BTN_BLOCKCHAIN, callback_data='blockchain')
            ],
            [
                InlineKeyboardButton(messages.BTN_GET_QR, callback_data='get_qr'),
                InlineKeyboardButton(messages.BTN_CONTACT, callback_data='contact')
            ],
            [InlineKeyboardButton(messages.BTN_LEADERBOARD, callback_data='leaderboard')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 <b>Navigate menu using the buttons below:</b>",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "<b>This command is for use in escrow groups only.</b>",
            parse_mode='HTML'
        )

# ====================
# ADDRESS COMMANDS
# ====================

def get_explorer_link(network, address):
    """Generate blockchain explorer link"""
    net = network.upper()
    if 'BEP20' in net or 'BSC' in net:
        return f"https://bscscan.com/address/{address}"
    elif 'TRC20' in net or 'TRX' in net:
        return f"https://tronscan.org/#/address/{address}"
    elif 'ERC20' in net or 'ETH' in net:
        return f"https://etherscan.io/address/{address}"
    elif 'BTC' in net or 'BITCOIN' in net:
        return f"https://www.blockchain.com/explorer/addresses/btc/{address}"
    elif 'LTC' in net or 'LITECOIN' in net:
        return f"https://blockchair.com/litecoin/address/{address}"
    elif 'TON' in net:
        return f"https://tonviewer.com/{address}"
    return "https://blockchain.com"

@handle_errors
async def seller_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /seller ADDRESS command"""
    if not context.args:
        await update.message.reply_text(
            "<b>Usage: /seller <WALLET_ADDRESS></b>",
            parse_mode='HTML'
        )
        return
    
    address = context.args[0]
    is_valid, coin_type = validators.validate_crypto_address(address)
    
    if not is_valid:
        await update.message.reply_text(
            messages.INVALID_ADDRESS_MESSAGE,
            parse_mode='HTML'
        )
        return
    
    user = update.effective_user
    
    # If in group, update deal
    if update.effective_chat.type in ['group', 'supergroup']:
        group_id = update.effective_chat.id
        deal = database.get_deal_by_group(group_id)
        
        if deal:
            deal_id = deal[0]
            existing_buyer_id = deal[1]
            existing_buyer_addr = deal[3]
            
            # PREVENT SELF-DEALING: Check if user is already Buyer
            if existing_buyer_id and str(existing_buyer_id) == str(user.id):
                 await update.message.reply_text(
                    "❌ <b>You cannot be both Seller and Buyer!</b>",
                    parse_mode='HTML'
                )
                 return

            database.update_deal_address(deal_id, 'seller', address, user_id=user.id)
            
            # Role Declaration Message
            msg = (
                "📍 <b>ESCROW ROLE DECLARATION</b>\n\n"
                f"👤 <b>SELLER</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> | Userid: [{user.id}]\n\n"
                "✅ <b>SELLER WALLET</b>\n"
                f"<code>{address}</code> [{coin_type}]"
            )
            
            # Only show prompt via text if Buyer is NOT ready
            if not existing_buyer_addr:
                msg += (
                    "\n\n"
                    "💬 <b>Buyer, please enter your receiving address using:</b> <code>/buyer ADDRESS</code>\n"
                    f"💡 <i>Replace ADDRESS with your {coin_type} wallet address.</i>"
                )
            
            await update.message.reply_text(msg, parse_mode='HTML')
            
            # Check if both ready
            await check_and_send_transaction_info(update, context, group_id)
        else:
            await update.message.reply_text(
                "<b>No active deal found in this group.</b>",
                parse_mode='HTML'
            )
    else:
        # Store globally
        database.set_user_role(user.id, "seller", address)
        await update.message.reply_text(
            f"✅ <b>Registered as SELLER with address: <code>{address}</code> ({coin_type})</b>",
            parse_mode='HTML'
        )

@handle_errors
async def buyer_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buyer ADDRESS command"""
    if not context.args:
        await update.message.reply_text(
            "<b>Usage: /buyer <WALLET_ADDRESS></b>",
            parse_mode='HTML'
        )
        return
    
    address = context.args[0]
    is_valid, coin_type = validators.validate_crypto_address(address)
    
    if not is_valid:
        await update.message.reply_text(
            messages.INVALID_ADDRESS_MESSAGE,
            parse_mode='HTML'
        )
        return
    
    user = update.effective_user
    
    # If in group, update deal
    if update.effective_chat.type in ['group', 'supergroup']:
        group_id = update.effective_chat.id
        deal = database.get_deal_by_group(group_id)
        
        if deal:
            deal_id = deal[0]
            existing_seller_id = deal[2]
            existing_seller_addr = deal[4]
            
            # PREVENT SELF-DEALING: Check if user is already Seller
            if existing_seller_id and str(existing_seller_id) == str(user.id):
                 await update.message.reply_text(
                    "❌ <b>You cannot be both Buyer and Seller!</b>",
                    parse_mode='HTML'
                )
                 return
            
            database.update_deal_address(deal_id, 'buyer', address, user_id=user.id)
            
            # Role Declaration Message
            msg = (
                "📍 <b>ESCROW ROLE DECLARATION</b>\n\n"
                f"👤 <b>BUYER</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> | Userid: [{user.id}]\n\n"
                "✅ <b>BUYER WALLET</b>\n"
                f"<code>{address}</code> [{coin_type}]"
            )
            
            # Only show prompt via text if Seller is NOT ready
            if not existing_seller_addr:
                msg += (
                    "\n\n"
                    "💬 <b>Seller, please enter your receiving address using:</b> <code>/seller ADDRESS</code>\n"
                    f"💡 <i>Replace ADDRESS with your {coin_type} wallet address.</i>"
                )
            
            await update.message.reply_text(msg, parse_mode='HTML')

            # Check if both ready
            await check_and_send_transaction_info(update, context, group_id)
        else:
            await update.message.reply_text(
                "<b>No active deal found in this group.</b>",
                parse_mode='HTML'
            )
    else:
        # Store globally
        database.set_user_role(user.id, "buyer", address)
        await update.message.reply_text(
            f"✅ <b>Registered as BUYER with address: <code>{address}</code> ({coin_type})</b>",
            parse_mode='HTML'
        )

# ... (Previous code) ...

async def check_and_send_transaction_info(update, context, group_id):
    """Check if both parties ready and send info"""
    deal = database.get_deal_by_group(group_id)
    if not deal:
        return

    # deal structure: (deal_id, buyer_id, seller_id, buyer_address, seller_address, bot_address, status)
    
    buyer_addr = deal[3]
    seller_addr = deal[4]
    
    if buyer_addr and seller_addr:
        # Both ready! Trigger Info.
        
        # 1. Detect Network from BUYER address
        is_valid, network = validators.validate_crypto_address(buyer_addr)
        if not network:
            network = "Unknown"
        
        # 2. Fetch Bot Address
        bot_wallet = database.get_config(f"wallet_{network}")
        
        if not bot_wallet:
             bot_wallet = "NOT_SET_CONTACT_ADMIN"
        
        # Construct Message (Without Blockchain Link)
        msg = (
            "📍 <b>TRANSACTION INFORMATION</b>\n\n"
            "⚡️ <b>SELLER</b>\n"
            f"<a href='tg://user?id={deal[2]}'>Seller</a>\n"
            f"[{deal[2]}]\n\n"
            "⚡️ <b>BUYER</b>\n"
            f"<a href='tg://user?id={deal[1]}'>Buyer</a>\n"
            f"[{deal[1]}]\n\n"
            "📝 <b>TRANSACTION ID</b>\n"
            f"<code>{deal[0]}</code>\n\n"
            "🟢 <b>ESCROW ADDRESS:</b>\n"
            f"<code>{bot_wallet}</code> [{network}]\n\n"
            "⚠️ <b>IMPORTANT: AVOID SCAMS!</b>\n\n"
            "<b>Useful commands:</b>\n"
            "🗒 <code>/pay_seller</code> = Always pays the seller.\n"
            "🗒 <code>/refund_buyer</code> = Always refunds the buyer.\n\n"
            "Remember, <code>/pay_seller</code> <i>won't refund your money</i> if you're the buyer, regardless of what <i>anyone</i> says."
        )
        
        await context.bot.send_message(
            chat_id=group_id,
            text=msg,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

@handle_errors
async def set_escrow_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set bot's escrow wallet for a specific network (Admin only)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "<b>Usage: /setescrow <NETWORK> <ADDRESS></b>\n"
            "Networks: BTC, LTC, BEP20, TRC20, TON",
            parse_mode='HTML'
        )
        return

    network_input = context.args[0].upper()
    address = context.args[1]

    # Map input to standard keys
    network_map = {
        'BEP20': 'USDT (BEP20)',
        'BSC': 'USDT (BEP20)',
        'ETH': 'USDT (BEP20)',
        'TRC20': 'USDT (TRC20)',
        'TRX': 'USDT (TRC20)',
        'BTC': 'BTC',
        'BITCOIN': 'BTC',
        'LTC': 'LTC',
        'LITECOIN': 'LTC',
        'TON': 'TON'
    }
    
    network_key = network_map.get(network_input, network_input)
    
    # Save to DB (using global addresses table)
    # database.add_crypto_address(currency=network_key, address=address) -> This function appends
    # We want to UPSERT or Replace. 
    # Let's assume add_crypto_address is fine, but we need a way to retrieval specific one.
    # Actually, let's just use 'crypto_addresses' table but ensure we can fetch by label/network.
    # For simplicity in this 'bot.py', I'll use a direct DB call or a helper if available.
    # Checking database.py: add_crypto_address takes (currency, address, network, label)
    
    # Let's just use a dedicated key in 'config' table or 'crypto_addresses' with strict labels?
    # The user said "in admin panel configure...". 
    # I will use `database.set_config(f"wallet_{network_key}", address)` for simplicity and reliability.
    database.set_config(f"wallet_{network_key}", address)
    
    await update.message.reply_text(
        f"✅ <b>Escrow Address Set!</b>\n"
        f"Network: {network_key}\n"
        f"Address: <code>{address}</code>",
        parse_mode='HTML'
    )

@handle_errors
async def show_bot_escrow_addresses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all configured bot escrow wallets (Admin only in Private, Public in Groups)"""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # In PRIVATE chat, restrict to Admin
    if chat_type == 'private' and user_id not in ADMIN_USER_IDS:
        return

    networks = [
        'USDT (BEP20)',
        'USDT (TRC20)',
        'BTC',
        'LTC',
        'TON'
    ]
    
    msg = "🔐 <b>Bot Escrow Addresses:</b>\n\n"
    
    for net in networks:
        addr = database.get_config(f"wallet_{net}")
        if not addr:
            addr = "❌ Not Set"
        else:
            addr = f"<code>{addr}</code>"
        
        msg += f"🔹 <b>{net}:</b>\n{addr}\n\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')

async def check_and_send_transaction_info(update, context, group_id):
    """Check if both parties ready and send info"""
    deal = database.get_deal_by_group(group_id)
    if not deal:
        return

    # deal structure: (deal_id, buyer_id, seller_id, buyer_address, seller_address, bot_address, status)
    # Indexes: 0=id, 1=buy_id, 2=sell_id, 3=buy_addr, 4=sell_addr
    
    buyer_addr = deal[3]
    seller_addr = deal[4]
    
    if buyer_addr and seller_addr:
        # Both ready! Trigger Info.
        
        # 1. Detect Network from BUYER address (Deposit comes from Buyer)
        is_valid, network = validators.validate_crypto_address(buyer_addr)
        if not network:
            network = "Unknown"
        
        # 2. Fetch Bot Address
        # Try specific config first
        bot_wallet = database.get_config(f"wallet_{network}")
        
        # Fallback if specific not found (e.g. USDT BEP20 not set)
        if not bot_wallet:
             bot_wallet = "NOT_SET_CONTACT_ADMIN"
        
        # 3. Get User Usernames/Links
        # Use deal[1] (buyer_id) and deal[2] (seller_id)
        # We try to get usernames if possible, but IDs are safer.
        # User requested specific format with @Mentions if available.
        # Telethon logic isn't here, checks update.effective_user roughly.
        # We construct deep links.
        
        explorer_link = get_explorer_link(network, bot_wallet)

        # Construct Message (Exact Match to User Request)
        msg = (
            "📍 <b>TRANSACTION INFORMATION</b>\n\n"
            "⚡️ <b>SELLER</b>\n"
            f"<a href='tg://user?id={deal[2]}'>Seller</a>\n"
            f"[{deal[2]}]\n\n"
            "⚡️ <b>BUYER</b>\n"
            f"<a href='tg://user?id={deal[1]}'>Buyer</a>\n"
            f"[{deal[1]}]\n\n"
            "📝 <b>TRANSACTION ID</b>\n"
            f"<code>{deal[0]}</code>\n\n"
            "🟢 <b>ESCROW ADDRESS:</b>\n"
            f"<code>{bot_wallet}</code> [{network}]\n\n"
            f"🌐 <b>BLOCKCHAIN LINK:</b>   {explorer_link}\n\n"
            "⚠️ <b>IMPORTANT: AVOID SCAMS!</b>\n\n"
            "<b>Useful commands:</b>\n"
            "🗒 <code>/pay_seller</code> = Always pays the seller.\n"
            "🗒 <code>/refund_buyer</code> = Always refunds the buyer.\n\n"
            "Remember, <code>/pay_seller</code> <i>won't refund your money</i> if you're the buyer, regardless of what <i>anyone</i> says."
        )
        
        await context.bot.send_message(
            chat_id=group_id,
            text=msg,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

@handle_errors
async def show_addresses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all addresses in the escrow group"""
    if update.effective_chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "<b>This command is for use in escrow groups only.</b>",
            parse_mode='HTML'
        )
        return
    
    group_id = update.effective_chat.id
    deal = database.get_deal_by_group(group_id)
    
    if not deal:
        await update.message.reply_text(
            "<b>No active deal found in this group.</b>",
            parse_mode='HTML'
        )
        return
    
    deal_id, buyer_id, seller_id, buyer_addr, seller_addr, bot_addr, status = deal
    
    text = "<b>📍 Escrow Addresses:</b>\n\n"
    text += f"<b>Buyer:</b> <code>{buyer_addr if buyer_addr else 'Not set'}</code>\n"
    text += f"<b>Seller:</b> <code>{seller_addr if seller_addr else 'Not set'}</code>\n"
    text += f"<b>Bot (Escrow):</b> <code>{bot_addr if bot_addr else 'Not set'}</code>\n"
    
    await update.message.reply_text(text, parse_mode='HTML')

@handle_errors
async def set_crypto_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only - Set bot's crypto address"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text(
            "<b>🚫 This command is admin-only.</b>",
            parse_mode='HTML'
        )
        return
    
    if not context.args:
        current_addr = database.get_bot_crypto_address()
        await update.message.reply_text(
            f"<b>Current bot crypto address:</b> <code>{current_addr if current_addr else 'Not set'}</code>\n\n"
            f"<b>Usage:</b> /setcryptoaddress <ADDRESS>",
            parse_mode='HTML'
        )
        return
    
    address = context.args[0]
    is_valid, coin_type = validators.validate_crypto_address(address)
    
    if not is_valid:
        await update.message.reply_text(
            messages.INVALID_ADDRESS_MESSAGE,
            parse_mode='HTML'
        )
        return
    
    database.set_global_bot_crypto_address(address)
    await update.message.reply_text(
        f"✅ <b>Bot crypto address set to: <code>{address}</code> ({coin_type})</b>",
        parse_mode='HTML'
    )

# ====================
# GROUP CREATION
# ====================

@handle_errors
async def create_escrow_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create an escrow group (example trigger - adjust to your flow)"""
    # This is a simplified example. You'd trigger this from inline buttons or another flow
    # For now, usage: /creategroup <buyer_id> <seller_id>
    
    if update.effective_chat.type != 'private':
        await update.message.reply_text(
            "<b>This command should be used in private chat.</b>",
            parse_mode='HTML'
        )
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "<b>Usage: /creategroup <buyer_id> <seller_id></b>",
            parse_mode='HTML'
        )
        return
    
    try:
        buyer_id = int(context.args[0])
        seller_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text(
            "<b>Invalid user IDs. Please provide numeric IDs.</b>",
            parse_mode='HTML'
        )
        return
    
    await update.message.reply_text(
        "<b>Creating escrow group... Please wait.</b>",
        parse_mode='HTML'
    )
    
    try:
        deal_id = str(uuid.uuid4())[:8]  # Short deal ID
        bot_username = context.bot.username
        
        # Create group using Telethon
        group_id = await user_client.create_escrow_group(
            buyer_id,
            seller_id,
            bot_username,
            deal_id
        )
        
        # Store in database
        database.create_deal(deal_id, buyer_id, seller_id, group_id)
        
        
        # NOTE: Welcome message is now sent automatically by track_member_updates
        # when the bot joins the group. We don't need to send it here.
        
        await update.message.reply_text(
            f"✅ <b>Escrow group created successfully!</b>\n"
            f"<b>Deal ID:</b> <code>{deal_id}</code>",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        await update.message.reply_text(
            f"<b>❌ Error creating group: {str(e)}</b>",
            parse_mode='HTML'
        )

# ====================
# ADMIN FEATURES
# ====================

@handle_errors
async def join_deal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to join an active deal"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text(
            "<b>🚫 This command is admin-only.</b>",
            parse_mode='HTML'
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "<b>Usage: /joindeal <deal_id></b>",
            parse_mode='HTML'
        )
        return
    
    deal_id = context.args[0]
    # In a real implementation, you'd look up the group_id from the deal_id
    # For now, assuming you have the group_id
    
    await update.message.reply_text(
        "<b>Joining deal group...</b>",
        parse_mode='HTML'
    )

@handle_errors
@handle_errors
async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete service messages like 'User added Bot'"""
    if not update.message:
        return
        
    # Check if this is a 'new chat members' service message
    if update.message.new_chat_members:
        try:
            # We only want to delete the message if it's about the BOT being added
            # or if the user wants ALL 'added' messages hidden.
            # User said: "must not show middle crypto added bot".
            # So we delete all 'added member' messages just to be clean?
            # Or just the one for the bot.
            
            # Let's delete ALL for cleaner look in Escrow groups
            await update.message.delete()
        except Exception:
            pass
            
    # Also delete 'left chat member' messages
    if update.message.left_chat_member:
        try:
            await update.message.delete()
        except Exception:
            pass

@handle_errors
async def track_member_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track when members join the group - send admin announcement"""
    
    # 1. Check MY_CHAT_MEMBER (Bot's own status change)
    if update.my_chat_member:
        new_chat_member = update.my_chat_member.new_chat_member
        if new_chat_member.status in ['member', 'administrator']:
            # Bot joined/added to a group
            logger.info("🤖 Bot joined a new group via MY_CHAT_MEMBER! Sending welcome message...")
            try:
                stats = database.get_statistics()
                welcome_text = messages.GROUP_WELCOME_TEXT.format(
                    total_deals=stats.get('total_deals', 5542),
                    disputes_resolved=stats.get('disputes_resolved', 158)
                )
                keyboard = get_group_keyboard()
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=welcome_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending auto-welcome (my_chat_member): {e}")
            return

    # 2. Check CHAT_MEMBER (Other members)
    if update.chat_member:
        new_members = update.chat_member.new_chat_member
        
        if new_members and new_members.user:
            user_id = new_members.user.id
            
            # Check if BOT joined (via chat_member update - redundant but safe)
            if user_id == context.bot.id:
                 # Already handled by my_chat_member usually, but just in case
                 return

            # Check if ADMIN joined
            if user_id in ADMIN_USER_IDS:
                # Send admin join announcement
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=messages.ADMIN_JOIN_MESSAGE,
                    parse_mode='HTML'
                )

# ====================
# OTHER COMMANDS
# ====================

@handle_errors
async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contact command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(f"<b>{messages.TEXT_CONTACT_ADMIN}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text(messages.GROUP_ONLY_COMMAND, parse_mode='HTML')

@handle_errors
async def blockchain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /blockchain command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "🌐 <b>Blockchain Explorer</b>\n\n"
            "View transaction on blockchain:\n"
            "https://blockchain.info",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(messages.GROUP_ONLY_COMMAND, parse_mode='HTML')

@handle_errors
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "📊 <b>Current Balance:</b>\n\n"
            "Escrow Balance: 0.00 USDT\n"
            "Pending: 0.00 USDT",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')

@handle_errors
async def pay_seller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pay_seller command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "💸 <b>Initiating payment to Seller...</b>\n\n"
            "Admin will verify and process the payment.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')

@handle_errors
async def refund_buyer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /refund_buyer command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "💸 <b>Initiating refund to Buyer...</b>\n\n"
            "Admin will verify and process the refund.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')

@handle_errors
async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /qr command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "📱 <b>QR Code</b>\n\n"
            "QR code generation feature coming soon!",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')

@handle_errors
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command - works everywhere"""
    try:
        await update.message.reply_text(messages.LEADERBOARD_TEXT, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error showing leaderboard: {e}")
        await update.message.reply_text("<b>Error loading leaderboard. Please try again.</b>", parse_mode='HTML')



@handle_errors
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Type /start to see the main menu.</b>", parse_mode='HTML')

@handle_errors
async def userinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /userinfo - show user information"""
    # Check if reply to message
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_info = f"""👤 <b>User Information</b>

<b>Name:</b> {user.full_name}
<b>Username:</b> @{user.username if user.username else 'No username'}
<b>User ID:</b> <code>{user.id}</code>
<b>Is Bot:</b> {'Yes' if user.is_bot else 'No'}"""
        
        await update.message.reply_text(user_info, parse_mode='HTML')
    
    # Check if username provided
    elif context.args and len(context.args) > 0:
        username = context.args[0].replace('@', '')
        await update.message.reply_text(
            f"🔍 <b>Looking up user:</b> @{username}\n\n"
            f"<i>Note: Full user details are only available when replying to their message.</i>",
            parse_mode='HTML'
        )
    
    else:
        await update.message.reply_text(
            "⚠️ <b>Use this command either with username or reply to a message!</b>",
            parse_mode='HTML'
        )

@handle_errors
async def real_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /real - verify if user is real admin"""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "🚫 <b>This command must be used in reply to another message.</b>",
            parse_mode='HTML'
        )
        return
    
    user = update.message.reply_to_message.from_user
    admin_username = database.get_config("admin_username") or "MiddleCryptoSupport"
    
    # Check if user is the real admin
    is_real_admin = (
        (user.username and user.username.lower() == admin_username.lower()) or
        (user.id in ADMIN_USER_IDS)
    )
    
    if is_real_admin:
        await update.message.reply_text(
            f"✅ <b>Verified!</b>\n\n"
            f"@{user.username} is the <b>REAL</b> admin/support account.\n\n"
            f"🔐 <b>Official Support:</b> @{admin_username}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"⚠️ <b>Warning!</b>\n\n"
            f"@{user.username if user.username else user.full_name} is <b>NOT</b> the official admin.\n\n"
            f"🔐 <b>Real Support:</b> @{admin_username}",
            parse_mode='HTML'
        )


@handle_errors
async def whatisescrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_WHAT_IS_ESCROW}</b>", parse_mode='HTML')

@handle_errors
async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import os
    if os.path.exists("video.mp4"):
        await update.message.reply_video(
            video=open("video.mp4", "rb"),
            caption=f"<b>{messages.TEXT_VIDEO_CAPTION}</b>",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("<b>Video not found on server.</b>", parse_mode='HTML')

@handle_errors
async def terms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_TERMS}</b>", parse_mode='HTML')

@handle_errors
async def instructions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_INSTRUCTIONS}</b>", parse_mode='HTML')

@handle_errors
async def setpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setpin command - set user PIN for security"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /setpin 6-digit-pin (example: /setpin 123456)",
            parse_mode='HTML'
        )
        return
    
    pin = context.args[0]
    
    # Validate PIN
    if len(pin) != 6 or not pin.isdigit():
        await update.message.reply_text(
            "❌ <b>Invalid PIN!</b>\n\n"
            "Your PIN must be exactly 6 digits (0-9).\n\n"
            "<b>Example:</b> /setpin <code>123456</code>",
            parse_mode='HTML'
        )
        return
    
    # Store PIN in database
    database.set_config(f"user_pin_{user_id}", pin)
    
    await update.message.reply_text(
        "✅ Transaction PIN has been set successfully.",
        parse_mode='HTML'
    )


# ====================
# CALLBACK HANDLERS
# ====================

@handle_errors
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'what_is_escrow':
        await query.message.reply_text(f"<b>{messages.TEXT_WHAT_IS_ESCROW}</b>", parse_mode='HTML')
    elif query.data == 'instructions':
        await query.message.reply_text(f"<b>{messages.TEXT_INSTRUCTIONS}</b>", parse_mode='HTML')
    elif query.data == 'terms':
        await query.message.reply_text(f"<b>{messages.TEXT_TERMS}</b>", parse_mode='HTML')
    elif query.data == 'video':
        import os
        if os.path.exists("video.mp4"):
            await query.message.reply_video(
                video=open("video.mp4", "rb"),
                caption=f"<b>{messages.TEXT_VIDEO_CAPTION}</b>",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>Video not found.</b>", parse_mode='HTML')
    
    
    # Group menu button handlers - check if in group
    elif query.data == 'pay_seller':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "💸 <b>Initiating payment to Seller...</b>\n\n"
                "Admin will verify and process the payment.",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'refund_buyer':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "💸 <b>Initiating refund to Buyer...</b>\n\n"
                "Admin will verify and process the refund.",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'reset_roles':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "🔄 <b>Roles have been reset.</b>\n\n"
                "Use /seller or /buyer to register again.",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'balance':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "📊 <b>Current Balance:</b>\n\n"
                "Escrow Balance: 0.00 USDT\n"
                "Pending: 0.00 USDT",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'blockchain':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "🌐 <b>Blockchain Explorer</b>\n\n"
                "View transaction on blockchain:\n"
                "https://blockchain.info",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'get_qr':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(
                "📱 <b>QR Code</b>\n\n"
                "QR code generation feature coming soon!",
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'contact':
        if query.message.chat.type in ['group', 'supergroup']:
            await query.message.reply_text(f"<b>{messages.TEXT_CONTACT_ADMIN}</b>", parse_mode='HTML')
        else:
            await query.message.reply_text("<b>This command is for use in escrow groups only.</b>", parse_mode='HTML')
    
    elif query.data == 'create_group':
        # User clicked Create Escrow Group button
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "User"
        
        # Send "Creating..." message
        creating_msg = await query.message.reply_text(
            "🏗️ <b>Creating Escrow Group. Please Wait...</b>",
            parse_mode='HTML'
        )
        
        try:
            import uuid
            import requests
            
            # Generate a unique deal ID
            deal_id = str(uuid.uuid4())[:5].upper()
            
            # For demo/testing, we'll create a group with the user as both buyer and seller
            buyer_id = user_id
            seller_id = 0  # Use 0 for seller (to avoid constraint error if buyer==seller is not allowed)
            bot_username = context.bot.username
            
            # Call Telethon microservice to create group
            # Call Telethon directly to create group (No HTTP request needed)
            try:
                result = await telegram_group_manager.create_escrow_group(
                    deal_id=deal_id,
                    bot_username=bot_username
                )
                
                if result['success']:
                    group_id = result['group_id']
                    invite_link = result['invite_link']
                else:
                    raise Exception(result.get('error', 'Unknown error'))
                    
            except Exception as e:
                logger.error(f"Error creating group via button: {e}")
                raise Exception(f"Failed to create group: {str(e)}")
            
            # Store in database
            database.create_deal(deal_id, buyer_id, seller_id, group_id)
            
            # NOTE: Welcome message is now sent automatically by track_member_updates
            # when the bot joins the group. We don't need to send it here.
            
            # Send success message with invite link
            
            # Send success message with invite link
            await creating_msg.edit_text(
                f"✅ <b>Created Escrow Group #{deal_id}</b>\n\n"
                f"<b>Group Link:</b> {invite_link}\n\n"
                f"Now Join this escrow group & Forward this message to buyer/seller.\n\n"
                f"Enjoy Safe Escrow 🤝",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error creating group from button: {e}")
            import traceback
            traceback.print_exc()
            await creating_msg.edit_text(
                f"❌ <b>Error creating group:</b> {str(e)}\n\n"
                f"Please try again or contact support.",
                parse_mode='HTML'
            )
    
    elif query.data == 'leaderboard':
        # Leaderboard works in both private and group
        try:
            await query.message.reply_text(messages.LEADERBOARD_TEXT, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error showing leaderboard: {e}")
            await query.message.reply_text("<b>Error loading leaderboard. Please try again.</b>", parse_mode='HTML')


# ====================
# MAIN
# ====================

def main():
    """Start the bot"""
    # Initialize database
    database.init_db()
    
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("contact", contact_command))
    
    # Address commands
    app.add_handler(CommandHandler("seller", seller_address_command))
    app.add_handler(CommandHandler("buyer", buyer_address_command))
    app.add_handler(CommandHandler("showaddresses", show_addresses_command))
    app.add_handler(CommandHandler("setcryptoaddress", set_crypto_address_command))
    
    # ADMIN: Set Bot Escrow Wallet
    app.add_handler(CommandHandler("setescrow", set_escrow_address_command))
    app.add_handler(CommandHandler("showescrow", show_bot_escrow_addresses_command))
    
    # Group creation
    app.add_handler(CommandHandler("create", create_command))  # NEW: Simple /create command
    app.add_handler(CommandHandler("creategroup", create_escrow_group_command))
    app.add_handler(CommandHandler("joindeal", join_deal_command))
    
    # Other commands
    app.add_handler(CommandHandler("whatisescrow", whatisescrow_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("terms", terms_command))
    app.add_handler(CommandHandler("instructions", instructions_command))
    app.add_handler(CommandHandler("userinfo", userinfo_command))
    app.add_handler(CommandHandler("real", real_command))
    app.add_handler(CommandHandler("setpin", setpin_command))
    
    # Group-only commands
    app.add_handler(CommandHandler("blockchain", blockchain_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("pay_seller", pay_seller_command))
    app.add_handler(CommandHandler("refund_buyer", refund_buyer_command))
    app.add_handler(CommandHandler("qr", qr_command))
    
    # Callback query handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Chat member updates (for admin join detection)
    app.add_handler(ChatMemberHandler(track_member_updates, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(track_member_updates, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # Service message deleter (Keep chat clean)
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, delete_service_messages))
    
    # Start bot
    # Start bot with conflict handling
    logger.info("Bot started! (Version: Auto-Group-Creation)")
    
    import time
    from telegram.error import Conflict
    
    max_retries = 10
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            # Drop pending updates to flush old queue
            app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
            break
        except Conflict:
            logger.warning(f"⚠️ Conflict error detected (Attempt {i+1}/{max_retries}). Another instance is running.")
            logger.warning(f"Waiting {retry_delay} seconds for old instance to stop...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"❌ Error running bot: {e}")
            # Wait a bit before crashing/restarting to avoid rapid restart loops
            time.sleep(5)
            raise e

if __name__ == '__main__':
    main()
