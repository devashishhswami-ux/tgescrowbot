# 🗄️ SUPABASE SETUP - QUICK REFERENCE

## Your Supabase Credentials

**URL**: `https://odcytmpqzikvysukmqwr.supabase.co`  
**Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3l0bXBxemlrdnlzdWttcXdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODYzMzQsImV4cCI6MjA4NTk2MjMzNH0.twm0Q5vkCsMnjIYQjXa83tqfx2EACdIp4_i-NxUcZ0s`

---

## 🚀 Quick Setup (3 steps)

### 1. Go to SQL Editor
https://odcytmpqzikvysukmqwr.supabase.co/project/_/sql/new

### 2. Copy & Paste
Open `supabase_complete_schema.sql` and copy ALL content

### 3. Run
Click **Run** in Supabase

---

## ✅ What This Creates

**8 Tables Created:**
1. `users` - Escrow participants (buyers/sellers)
2. `bot_users` - Everyone who started the bot
3. `deals` - All escrow transactions
4. `statistics` - Bot stats (total deals, disputes)
5. `config` - Bot configuration
6. `media_files` - Uploaded videos/images
7. `editable_content` - Custom bot messages
8. `crypto_addresses` - Managed wallet addresses

**Default Data Inserted:**
- Admin password: `admin123`
- Total deals: 5542
- Disputes resolved: 158

---

## 🔍 Verify Setup

Run these queries in SQL Editor:

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- Check default config
SELECT * FROM config;

-- Check statistics  
SELECT * FROM statistics;
```

---

## 📊 Database Structure

```
users (escrow roles)
├── user_id (PK)
├── role (buyer/seller)
└── wallet_address

bot_users (all users)
├── user_id (PK)
├── username
├── first_name
└── last_name

deals (transactions)
├── deal_id (PK)
├── buyer_id
├── seller_id
├── group_id
├── buyer_address
├── seller_address
└── status

crypto_addresses (wallets)
├── id (PK)
├── currency (BTC, ETH, etc)
├── address
├── network (TRC20, ERC20, etc)
└── label
```

---

## 🔐 Security Notes

✅ **Already Using Supabase**  
- No SQLite or local database
- All data in cloud  
- Automatic backups
- Built-in security

✅ **Authentication**  
- Using anon key (safe for client apps)
- Service authenticated via environment variables

---

## ⚙️ What's Already Configured

Your bot is **100% configured** to use Supabase:

- ✅ `database.py` uses Supabase client
- ✅ All functions query Supabase tables
- ✅ No local database files needed
- ✅ Works on Koyeb/Vercel deployment

**You just need to run the SQL file once!**

---

## 🆘 Troubleshooting

**Error: "relation does not exist"**  
→ Tables not created yet. Run `supabase_complete_schema.sql`

**Error: "duplicate key value"**  
→ Tables already exist. This is OK!

**Can't connect to Supabase?**  
→ Check your credentials in `.env` file match the URLs above

---

## 🎯 Next Steps After Setup

1. ✅ Run `supabase_complete_schema.sql` (one time only)
2. Deploy bot to Koyeb with environment variables
3. Deploy admin panel to Vercel
4. Start using your bot!

All data will be stored in Supabase automatically.
