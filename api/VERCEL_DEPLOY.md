# Admin Panel - Vercel Deployment Guide

## Quick Deploy

1. **Push your code to GitHub** (if not already done)
2. **Go to Vercel** and import your repository
3. **Set Root Directory** to the repository root (not admin-panel)
4. **Add Environment Variables** (see below)
5. **Deploy!**

## Environment Variables

Add these in Vercel → Settings → Environment Variables:

```
SUPABASE_URL=https://odcytmpqzikvysukmqwr.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3l0bXBxemlrdnlzdWttcXdyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODYzMzQsImV4cCI6MjA4NTk2MjMzNH0.twm0Q5vkCsMnjIYQjXa83tqfx2EACdIp4_i-NxUcZ0s
SECRET_KEY=your-random-secret-key-here
ADMIN_PANEL_PASSWORD=admin123
BOT_TOKEN=8470449689:AAEHH4KZJi2TCqcWOxpVO0MtHDcTukaEN0k
API_ID=34829504
API_HASH=79800fb3038d1085079ec2c9e6936ce7
```

> ⚠️ Change `SECRET_KEY` to a random string before deploying!

## Files Updated

- ✅ Created `vercel.json` at repository root
- ✅ This points Vercel to `admin-panel/app.py`

## After Deployment

Once deployed, you can access your admin panel at: `https://your-project.vercel.app`

Login with the password you set in `ADMIN_PANEL_PASSWORD` (default: `admin123`)
