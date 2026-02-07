# 🚀 Deployment Guide

## Prerequisites
- Supabase account and project
- Koyeb account (for bot)
- Vercel account (for admin panel)
- GitHub repository (recommended)

## 1. Supabase Setup

### Create Tables
Run the following SQL in Supabase SQL Editor:

```sql
-- Run the crypto_addresses table creation
-- File: supabase_crypto_addresses.sql
```

Execute the `supabase_crypto_addresses.sql` file in your Supabase SQL editor.

### Get Credentials
1. Go to Project Settings → API
2. Copy `Project URL` → This is your `SUPABASE_URL`
3. Copy `anon/public key` → This is your `SUPABASE_KEY`

## 2. Deploy Bot to Koyeb

### Prepare Session File
1. Run `python auth_telethon.py` locally to create `user_session.session`
2. This file will be uploaded to Koyeb persistent storage

### Deploy Steps
1. Push code to GitHub repository
2. Go to Koyeb Dashboard → New App
3. Select "GitHub" as source
4. Choose your repository
5. Configure Services:
   - **Main Bot**: Use `Dockerfile.bot`
   - **Telethon Service**: Use `Dockerfile.telethon`

### Environment Variables (Koyeb)
Add these as **secrets** in Koyeb:
- `BOT_TOKEN` - Your Telegram bot token
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `PHONE_NUMBER` - Your phone number
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SECRET_KEY` - Random secret for Flask sessions

### Upload Session File
1. In Koyeb, go to your service → Volumes
2. Upload `user_session.session` to `/app/sessions/`

## 3. Deploy Admin Panel to Vercel

### Prepare for Deployment
1. Make sure `admin-panel/vercel.json` exists
2. Ensure `admin-panel/requirements.txt` is present

### Deploy Steps
1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to project root
3. Run: `vercel`
4. Follow prompts, select admin-panel folder

### Environment Variables (Vercel)
Add in Vercel Dashboard → Settings → Environment Variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`
- `API_ID`
- `API_HASH`

### Alternative: GitHub Integration
1. Push to GitHub
2. Go to Vercel → New Project
3. Import from GitHub
4. Select repository
5. Set Root Directory to `admin-panel`
6. Add environment variables
7. Deploy

## 4. Post-Deployment

### Test Bot
1. Message your bot on Telegram
2. Verify group creation works
3. Check Supabase for data

### Test Admin Panel
1. Visit your Vercel URL
2. Login with admin password (default: `admin123`)
3. Check Session Manager shows your Telegram account
4. Test Crypto Address management

### Update Crypto Addresses
1. Go to admin panel → Crypto Addresses
2. Add your wallet addresses
3. These will be used in the bot

## 5. Troubleshooting

### Bot Not Starting
- Check Koyeb logs
- Verify all environment variables are set
- Ensure Supabase is accessible

### Admin Panel Errors
- Check Vercel deployment logs
- Verify environment variables
- Test Supabase connection

### Session Issues
- Re-run `auth_telethon.py` locally
- Upload new session file to Koyeb
- Restart Telethon service

## 6. Security Notes

> [!WARNING]
> - Never commit `.env` or session files to GitHub
> - Change default admin password immediately
> - Use strong secrets for `SECRET_KEY`
> - Enable 2FA on all service accounts
> - Regularly rotate API keys

## 7. Monitoring

### Koyeb
- Monitor service health in dashboard
- Check logs for errors
- Set up alerts for downtime

### Vercel
- View deployment logs
- Monitor function invocations
- Check error rates

### Supabase
- Monitor database size
- Check API request counts
- Review logs for issues

## Need Help?
- Check logs first
- Verify environment variables
- Test Supabase connection
-Contact support if issues persist
