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
import user_client
import asyncio

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =================
# UTILITY FUNCTIONS
# =================

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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
    keyboard = [
        [InlineKeyboardButton(messages.BTN_WHAT_IS_ESCROW, callback_data='what_is_escrow')],
        [InlineKeyboardButton(messages.BTN_INSTRUCTIONS, callback_data='instructions')],
        [InlineKeyboardButton(messages.BTN_TERMS, callback_data='terms')],
        [InlineKeyboardButton(messages.BTN_CREATE_GROUP, callback_data='create_group')]
    ]
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
            database.update_deal_address(deal_id, 'seller', address)
            await update.message.reply_text(
                f"✅ <b>Seller address registered: <code>{address}</code> ({coin_type})</b>",
                parse_mode='HTML'
            )
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
            database.update_deal_address(deal_id, 'buyer', address)
            await update.message.reply_text(
                f"✅ <b>Buyer address registered: <code>{address}</code> ({coin_type})</b>",
                parse_mode='HTML'
            )
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
        
        # Send welcome message to the group
        stats = database.get_statistics()
        welcome_text = messages.GROUP_WELCOME_TEXT.format(
            total_deals=stats.get('total_deals', 5542),
            disputes_resolved=stats.get('disputes_resolved', 158)
        )
        keyboard = get_group_keyboard()
        
        await context.bot.send_message(
            chat_id=group_id,
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
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

async def track_member_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track when members join the group - send admin announcement"""
    new_members = update.chat_member.new_chat_member
    
    if new_members and new_members.user:
        user_id = new_members.user.id
        
        # Check if user is an admin
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

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contact command - group only"""
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text(f"<b>{messages.TEXT_CONTACT_ADMIN}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text(messages.GROUP_ONLY_COMMAND, parse_mode='HTML')

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

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command - works everywhere"""
    try:
        await update.message.reply_text(messages.LEADERBOARD_TEXT, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error showing leaderboard: {e}")
        await update.message.reply_text("<b>Error loading leaderboard. Please try again.</b>", parse_mode='HTML')



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Type /start to see the main menu.</b>", parse_mode='HTML')

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


async def whatisescrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_WHAT_IS_ESCROW}</b>", parse_mode='HTML')

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

async def terms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_TERMS}</b>", parse_mode='HTML')

async def instructions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>{messages.TEXT_INSTRUCTIONS}</b>", parse_mode='HTML')

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
            seller_id = user_id  # Same user for testing
            bot_username = context.bot.username
            
            # Call Telethon microservice to create group
            try:
                response = requests.post(
                    'http://localhost:5001/create-group',
                    json={
                        'buyer_id': buyer_id,
                        'seller_id': seller_id,
                        'bot_username': bot_username,
                        'deal_id': deal_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        group_id = data['group_id']
                        invite_link = data['invite_link']
                    else:
                        raise Exception(data.get('error', 'Unknown error'))
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', 'Unknown service error')
                    except:
                        error_msg = response.text or 'Unknown service error'
                    raise Exception(f"Service Error: {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                raise Exception("Telethon service is not running. Please start it first.")
            except requests.exceptions.Timeout:
                raise Exception("Group creation timed out. Please try again.")
            
            # Store in database
            database.create_deal(deal_id, buyer_id, seller_id, group_id)
            
            # Send welcome message to the group
            stats = database.get_statistics()
            welcome_text = messages.GROUP_WELCOME_TEXT.format(
                total_deals=stats.get('total_deals', 5542),
                disputes_resolved=stats.get('disputes_resolved', 158)
            )
            keyboard = get_group_keyboard()
            
            await context.bot.send_message(
                chat_id=group_id,
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
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
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
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
    
    # Group creation
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
    
    # Start bot
    logger.info("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
