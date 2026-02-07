# 📦 Middle Crypto Bot - Admin Panel

This folder contains the admin panel web application that can be deployed separately from the bot.

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_KEY="your_supabase_key"
   export SECRET_KEY="your_secret_key"
   ```

3. **Run Locally**:
   ```bash
   python app.py
   ```

4. **Access**: http://localhost:5000

## Features

- 👥 **Users**: View all bot users
- 🎥 **Videos**: Upload videos for bot commands
- 📝 **Content**: Edit instructions, terms, messages
- ⚙️ **Settings**: Manage addresses, stats, password

## Deployment

See `../DEPLOYMENT.md` for deployment instructions.

## Default Login

- **Password**: `admin123`

**⚠️ Change this immediately in Settings!**
