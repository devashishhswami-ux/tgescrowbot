# 🚀 Deployment Guide

## Project Structure

```
Middle Crypto Bot/
├── bot.py                  # Main bot (Deploy to Koyeb)
├── database.py             # Supabase integration
├── config.py
├── messages.py
├── validators.py
├── user_client.py
├── requirements.txt
├── supabase_schema.sql
├── .env.example
└── admin-panel/            # Separate admin panel (Deploy anywhere)
    ├── app.py
    ├── requirements.txt
    ├── templates/
    └── static/
```

---

##  1. Setup Supabase Database

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy your **Project URL** and **anon/public key**

### Step 2: Run SQL Schema
1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `supabase_schema.sql`
3. Run the SQL to create all tables

### Step 3: Get Credentials
- **SUPABASE_URL**: Your project URL (e.g., `https://xxx.supabase.co`)
- **SUPABASE_KEY**: Your anon/public key

---

## 2. Deploy Bot to Koyeb

### Prerequisites
- Koyeb account
- Bot token from @BotFather
- Supabase credentials

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add bot.py database.py config.py messages.py validators.py user_client.py requirements.txt
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Koyeb Service**
   - Go to [Koyeb Dashboard](https://app.koyeb.com)
   - Click "Create Service"
   - Select "GitHub" as source
   - Connect your repository
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python bot.py`

3. **Set Environment Variables** in Koyeb:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   BOT_TOKEN=your_telegram_bot_token
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   PHONE_NUMBER=+1234567890
   ```

4. **Deploy**: Click "Deploy"

---

## 3. Deploy Admin Panel

The admin panel can be deployed to:
- **Vercel** (Recommended - Free)
- **Render**
- **Heroku**
-  **Railway**

### Deploy to Vercel

1. **Create `vercel.json`** in `admin-panel/`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

2. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

3. **Deploy**:
   ```bash
   cd admin-panel
   vercel
   ```

4. **Set Environment Variables** in Vercel Dashboard:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   SECRET_KEY=your_random_secret_key_here
   ```

### Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create "New Web Service"
3. Connect GitHub repo
4. **Root Directory**: `admin-panel`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `gunicorn app:app`
7. Add environment variables
8. Deploy

---

## 4. Configuration

### Update Config
After deployment, access admin panel:
1. Login with default password: `admin123`
2. Go to **Settings**
3. Update:
   - Admin username
   - Bot crypto addresses
   - Change admin password

### Update Bot
The bot will automatically:
- Track users in Supabase
- Load videos from database
- Use content from admin panel

---

## 5. Usage

### Access Admin Panel
- **URL**: Your deployed admin panel URL
- **Login**: Use password from Settings

### Manage Bot
1. **Users**: View all users who started the bot
2. **Videos**: Upload videos for /start, /video, what is escrow
3. **Content**: Edit instructions, terms, welcome message
4. **Settings**: Update addresses, stats, password

---

## 6. File Uploads

For production, configure file storage:

### Option 1: Supabase Storage
```python
# In admin-panel/app.py
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Upload file
with open(filepath, 'rb') as f:
    supabase.storage.from_('media').upload(filename, f)
```

### Option 2: AWS S3 / Cloudinary
Update `admin-panel/app.py` to use cloud storage

---

## 7. Security

### Production Checklist
- ✅ Change default admin password
- ✅ Use strong SECRET_KEY for Flask
- ✅ Enable Supabase Row Level Security (RLS)
- ✅ Use environment variables, not hardcoded values
- ✅ Enable HTTPS on admin panel

---

## 8. Troubleshooting

### Bot Not Starting
- Check Koyeb logs
- Verify SUPABASE_URL and KEY
- Ensure BOT_TOKEN is correct

### Admin Panel 500 Error
- Check environment variables
- Verify Supabase connection
- Check application logs

### Database Connection Failed
- Verify Supabase credentials
- Check if SQL schema was run
- Ensure Supabase project is active

---

## 📞 Support

For issues:
1. Check Koyeb/Vercel logs
2. Verify environment variables
3. Test Supabase connection

**Admin Panel Default Login**: `admin123`
