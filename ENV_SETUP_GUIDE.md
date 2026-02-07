# 🚀 ENVIRONMENT VARIABLES SETUP GUIDE

## 📋 Your Supabase Information (ALREADY CONFIGURED)

✅ **Supabase URL**: `https://odcytmpqzikvysukmqwr.supabase.co`
✅ **Supabase Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3l0bXBxemlrdnlzdWttcXdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODYzMzQsImV4cCI6MjA4NTk2MjMzNH0.twm0Q5vkCsMnjIYQjXa83tqfx2EACdIp4_i-NxUcZ0s`

---

## 🔧 STEP 1: Create Database Tables in Supabase

### A. Open Supabase SQL Editor
1. Go to your Supabase dashboard: https://odcytmpqzikvysukmqwr.supabase.co
2. Click **SQL Editor** in the left sidebar
3. Click **+ New Query**

### B. Run Complete Schema
1. Open the file: `supabase_complete_schema.sql`
2. **Copy the ENTIRE file** (all ~200 lines)
3. **Paste** into Supabase SQL Editor
4. Click **Run** (or press Ctrl+Enter)
5. Wait for "Success. No rows returned" message

### C. Verify Tables Created
Run this query to check:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see 8 tables:
- ✅ `bot_users`
- ✅ `config`
- ✅ `crypto_addresses`
- ✅ `deals`
- ✅ `editable_content`
- ✅ `media_files`
- ✅ `statistics`
- ✅ `users`

### D. Check Default Data
```sql
SELECT * FROM config;
SELECT * FROM statistics;
```

You should see default admin password and statistics.

**✅ DATABASE SETUP COMPLETE!** The bot is now fully configured to use Supabase.

---

## 🌐 STEP 2: Deploy Bot to Koyeb

### A. Before Deployment - Create Session File

**Run this locally FIRST**:
```bash
cd "e:\TG ESCROW Bot"
python auth_telethon.py
```
This creates `user_session.session` file which you'll upload to Koyeb later.

### B. Koyeb Deployment

1. **Go to**: https://app.koyeb.com/
2. **Click**: New App
3. **Select**: GitHub
4. **Repository**: `kofficialworke-ship-it/TGBOTESCROW`
5. **Builder**: Docker
6. **Dockerfile**: `Dockerfile.bot`

### C. Add Environment Variables in Koyeb

Click **Environment Variables** and add these as **SECRETS**:

| Variable Name | Value | Where to Get It |
|--------------|-------|-----------------|
| `BOT_TOKEN` | Your bot token | Get from [@BotFather](https://t.me/BotFather) |
| `API_ID` | Your Telegram API ID | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Your Telegram API Hash | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `PHONE_NUMBER` | Your phone number | Format: `+1234567890` (with + and country code) |
| `SUPABASE_URL` | `https://odcytmpqzikvysukmqwr.supabase.co` | ✅ Already provided |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | ✅ Copy from above |
| `SECRET_KEY` | Any random string | Generate: `openssl rand -hex 32` or use random text |

### D. Configure Persistent Storage (Koyeb)

1. In Koyeb app settings → **Volumes**
2. Add volume:
   - **Mount Path**: `/app/sessions`
   - **Size**: 1 GB
3. **Upload** the `user_session.session` file you created earlier

### E. Deploy

Click **Deploy** and wait for deployment to complete.

---

## ▲ STEP 3: Deploy Admin Panel to Vercel

### A. Vercel Deployment

#### Option 1: Using Vercel CLI
```bash
npm install -g vercel
cd "e:\TG ESCROW Bot"
vercel
```

#### Option 2: Using Vercel Dashboard (Recommended)
1. Go to: https://vercel.com/new
2. **Import Git Repository**
3. Select: `kofficialworke-ship-it/TGBOTESCROW`
4. **Root Directory**: `admin-panel`
5. Click **Deploy**

### B. Add Environment Variables in Vercel

After deployment, go to:
**Project Settings → Environment Variables**

Add these variables:

| Variable Name | Value | Production | Preview | Development |
|--------------|-------|------------|---------|-------------|
| `SUPABASE_URL` | `https://odcytmpqzikvysukmqwr.supabase.co` | ✅ | ✅ | ✅ |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | ✅ | ✅ | ✅ |
| `SECRET_KEY` | Random string (same as Koyeb) | ✅ | ✅ | ✅ |
| `API_ID` | Your Telegram API ID | ✅ | ✅ | ✅ |
| `API_HASH` | Your Telegram API Hash | ✅ | ✅ | ✅ |

**Check all three boxes** (Production, Preview, Development) for each variable.

### C. Redeploy

After adding environment variables:
1. Go to **Deployments**
2. Click **...** on latest deployment
3. Click **Redeploy**

---

## 🎯 STEP 4: Get Your Telegram API Credentials

If you don't have API_ID and API_HASH yet:

1. Go to: https://my.telegram.org/auth
2. Log in with your phone number
3. Click **API development tools**
4. Fill in the form:
   - **App title**: `Escrow Bot`
   - **Short name**: `escrowbot`
   - **Platform**: `Other`
5. Click **Create application**
6. Copy:
   - **App api_id** → This is your `API_ID`
   - **App api_hash** → This is your `API_HASH`

---

## 🤖 STEP 5: Get Your Bot Token

If you don't have a bot token yet:

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send: `/newbot`
3. Follow instructions to choose name and username
4. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. This is your `BOT_TOKEN`

---

## ✅ STEP 6: Verify Deployment

### Test Bot (Koyeb)
1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Bot should respond

### Test Admin Panel (Vercel)
1. Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
2. Login with password: `admin123`
3. Navigate to **Session Manager** - should show your Telegram account
4. Navigate to **Crypto Addresses** - should load without errors

---

## 📝 Summary Checklist

- [ ] Create tables in Supabase using `supabase_crypto_addresses.sql`
- [ ] Run `python auth_telethon.py` locally to create session file
- [ ] Get Telegram API_ID and API_HASH from my.telegram.org
- [ ] Get BOT_TOKEN from @BotFather
- [ ] Deploy to Koyeb with all environment variables
- [ ] Upload session file to Koyeb volumes
- [ ] Deploy to Vercel with all environment variables  
- [ ] Test bot on Telegram
- [ ] Test admin panel login
- [ ] Change admin password in admin panel settings

---

## ⚠️ Important Notes

1. **Never share** your session file or API credentials publicly
2. **Change admin password** immediately after first login
3. **Session file** must be uploaded to Koyeb volumes for bot to work
4. **Environment variables** must be added BEFORE deployment or require redeploy
5. **Supabase tables** must be created before bot can store data

---

## 🆘 Troubleshooting

### Bot not starting on Koyeb?
- Check logs in Koyeb dashboard
- Verify all environment variables are set
- Ensure session file is uploaded to volumes

### Admin panel errors on Vercel?
- Check deployment logs
- Verify environment variables are set
- Make sure Supabase tables exist

### Can't login to admin panel?
- Default password is `admin123`
- Make sure SUPABASE_URL and SUPABASE_KEY are correct

Need help? Check the logs first - they usually show the exact error!
