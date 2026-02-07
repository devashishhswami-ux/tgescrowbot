"""
Error handling wrapper for all bot functions
Add this decorator to make any function crash-proof
"""
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Decorator to catch all errors in bot handlers"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            return await func(update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            try:
                # Try to send error message to user
                if update.message:
                    await update.message.reply_text(
                        "⚠️ An error occurred. Please try again later.",
                        parse_mode='HTML'
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        "⚠️ An error occurred. Please try again.",
                        show_alert=True
                    )
            except:
                # If we can't even send error message, just log it
                logger.error(f"Could not send error message to user")
    return wrapper

def safe_call(func):
    """Decorator for non-async functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            return None
    return wrapper
