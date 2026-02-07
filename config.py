# Config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your actual bot token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8470449689:AAEHH4KZJi2TCqcWOxpVO0MtHDcTukaEN0k")

# Telethon User Account Credentials (for creating groups)
# Get these from https://my.telegram.org
API_ID = int(os.getenv("API_ID", "0"))  # e.g., 12345678 - must be integer
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH_HERE")  # e.g., "a1b2c3d4e5f6..."
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "YOUR_PHONE_NUMBER_HERE")  # e.g., "+1234567890"

# Admin Configuration
ADMIN_USERNAMES = [os.getenv("ADMIN_USERNAMES", "@MiddleCryptoSupport")]  # Admin User IDs (numeric Telegram IDs, you need to populate this)
ADMIN_USER_IDS = []  # Example: ["123456789"]

# === Admin Panel Settings ===
ADMIN_PANEL_PASSWORD = "admin123"  # Change this to a secure password
MEDIA_DIR = "media"
MAX_VIDEO_SIZE_MB = 50  # Maximum video upload size in MB
