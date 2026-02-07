# 🚀 QUICK SUPABASE SETUP (2 MINUTES)

## Your Credentials (Already Saved)
- **URL**: `https://odcytmpqzikvysukmqwr.supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3l0bXBxemlrdnlzdWttcXdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODYzMzQsImV4cCI6MjA4NTk2MjMzNH0.twm0Q5vkCsMnjIYQjXa83tqfx2EACdIp4_i-NxUcZ0s`

---

## ⚡ SETUP STEPS (Follow These)

### Step 1: Open Supabase SQL Editor
1. Go to: https://odcytmpqzikvysukmqwr.supabase.co
2. Login with your Supabase account
3. Click **SQL Editor** in left sidebar
4. Click **+ New Query**

### Step 2: Run SQL Setup
1. Open the file: **`setup_supabase.sql`** (in your project root)
2. **Select ALL content** (Ctrl+A)
3. **Copy** (Ctrl+C)
4. **Paste** in Supabase SQL Editor
5. Click **RUN** (or press Ctrl+Enter)

### Step 3: Verify Success
You should see:
```
SUCCESS: All tables created!
```

Then run this to confirm:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;
```

You should see **8 tables**:
- bot_users
- config
- crypto_addresses
- deals
- editable_content
- media_files
- statistics
- users

---

## ✅ What Was Created

### Tables (8):
1. **users** - Escrow participant roles (buyers/sellers)
2. **bot_users** - Everyone who started the bot  
3. **deals** - All escrow transactions
4. **stat istics** - Bot metrics (total deals, disputes)
5. **config** - Bot configuration (admin password, etc)
6. **media_files** - Uploaded videos/images
7. **editable_content** - Custom bot messages
8. **crypto_addresses** - Managed wallet addresses

### Auto-Features:
- ✅ Created indexes for fast queries
- ✅ Auto-update timestamps
- ✅ Default data inserted (admin password: admin123)
- ✅ Statistics pre-populated (5542 deals, 158 disputes)

---

## 🎯 After Setup

### Your Bot is Now Configured!
- ✅ Database is ready
- ✅ All tables created
- ✅ Default data inserted
- ✅ Bot can connect immediately

### Next Steps:
1. Deploy bot to Koyeb
2. Deploy admin panel to Vercel
3. Set environment variables
4. Start using your bot!

---

## 🔍 Quick Check

Run this in SQL Editor to see your config:
```sql
SELECT * FROM config;
SELECT * FROM statistics;
```

You should see:
- Admin password: `admin123` (change this!)
- Total deals: `5542`
- Disputes resolved: `158`

---

## 🆘 If You See Errors

### "relation already exists"
✅ **This is OK!** Tables are already created. Skip to verification.

### "permission denied"  
❌ Check you're logged in with correct account

### "syntax error"
❌ Make sure you copied the ENTIRE SQL file

---

## 📊 Database is Now Ready!

Your Supabase database is fully configured and ready to use. The bot will automatically connect using the credentials in your `.env` file.

**No more setup needed for database!** 🎉
