# ⏰ UPTIMEROBOT MONITORING SETUP

## What is UptimeRobot?

UptimeRobot is a free service that monitors your bot's uptime and sends you alerts if it goes down.

**Benefits:**
- ✅ Free monitoring (50 monitors)
- ✅ Email/SMS alerts when bot is down
- ✅ 5-minute check intervals
- ✅ Auto-pings to keep bot alive
- ✅ Uptime statistics

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Account
1. Go to: https://uptimerobot.com/
2. Click **Sign Up Free**
3. Verify your email

### Step 2: Add Bot Monitor

1. **Login** to UptimeRobot dashboard
2. Click **+ Add New Monitor**
3. Fill in the form:

| Field | Value |
|-------|-------|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | `Telegram Escrow Bot` |
| **URL (or IP)** | Your Koyeb bot URL (see below) |
| **Monitoring Interval** | `5 minutes` |

### Step 3: Get Your Koyeb Bot URL

Your bot URL depends on your Koyeb deployment:
- Format: `https://your-app-name.koyeb.app`
- Or go to Koyeb Dashboard → Your App → Copy URL

**Important:** Add `/health` to the end if you set up a health endpoint (optional).

Example: `https://escrow-bot-main.koyeb.app`

### Step 4: Configure Alerts

1. In UptimeRobot → **My Settings** → **Alert Contacts**
2. Add your email/phone
3. Choose when to get alerted:
   - ✅ When bot goes down
   - ✅ When bot comes back up

### Step 5: Save & Test

1. Click **Create Monitor**
2. Wait 5 minutes
3. Check if status shows "Up" (green)

---

## 📱 Optional: Add Health Endpoint to Bot

For better monitoring, add a health check endpoint to your bot:

### For bot.py (Flask/Web Server)

Add this to the end of your `bot.py`:

```python
from flask import Flask
import threading

# Create mini web server for health checks
health_app = Flask(__name__)

@health_app.route('/health')
def health():
    return {'status': 'ok', 'bot': 'running'}, 200

@health_app.route('/')
def root():
    return {'bot': 'Telegram Escrow Bot', 'status': 'active'}, 200

def run_health_server():
    health_app.run(host='0.0.0.0', port=8080)

# Start health server in background
if __name__ == '__main__':
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Start your bot normally
    application.run_polling()
```

Then monitor: `https://your-app.koyeb.app/health`

---

## 📊 Monitoring Best Practices

### Recommended Settings

- **Check Interval**: 5 minutes (free tier)
- **Alert After**: 2 consecutive failures (to avoid false alarms)
- **Notification**: Email + SMS if bot is critical

### What to Monitor

1. **Main Bot** - Your Koyeb deployment URL
2. **Admin Panel** - Your Vercel deployment URL  
3. **Supabase** (optional) - Check if database is responding

---

## 🆘 Troubleshooting

### Monitor Shows "Down"

**Possible Reasons:**
1. Bot crashed on Koyeb
2. Koyeb service is down
3. Bot has no health endpoint (monitors root URL)
4. Bot doesn't respond to HTTP requests

**Solutions:**
1. Check Koyeb logs
2. Restart bot on Koyeb
3. Verify webhook is deleted (use admin panel)
4. Check bot token is correct

### Monitor Shows "Paused"

- You manually paused it
- Free tier limit reached (50 monitors)
- Account issue

**Solution:** Resume from UptimeRobot dashboard

### False Alarms

- Set "Alert After" to 2-3 consecutive failures
- Increase check interval to reduce server load

---

## 📈 Dashboard Features

### Uptime Statistics
- Last 24 hours
- Last 7 days  
- Last 30 days
- Custom date range

### Response Time
- Average response time
- Response time graph
- Slow response alerts

### Downtime Alerts
- Email notifications
- SMS notifications (premium)
- Webhook notifications
- Slack/Discord integration

---

## 💡 Pro Tips

### Keep Bot Alive on Free Tier Platforms

Some platforms (like Render free tier) sleep after  inactivity. UptimeRobot pings prevent this:
- Set check interval to 5 minutes
- Bot gets pinged every 5 minutes
- Bot stays awake 24/7

### Multiple Monitors

Free tier allows 50 monitors. You can monitor:
1. Main bot
2. Admin panel
3. Telethon service (if separate)
4. Webhook URL (if using webhooks)

### Status Page

UptimeRobot offers public status pages:
- Show uptime to your users
- Build trust
- Transparent downtime reporting

---

## 🔐 Security Note

> [!WARNING]
> UptimeRobot only pings your URL, it doesn't need:
> - Bot token
> - API keys
> - Admin credentials
> 
> **Never share sensitive information with monitoring services!**

---

## ✅ Setup Checklist

- [ ] Create UptimeRobot account
- [ ] Add bot monitor with Koyeb URL
- [ ] Set monitoring interval to 5 minutes  
- [ ] Add email alert contact
- [ ] Enable "down" and "up" notifications
- [ ] Test monitor (wait 5 minutes, check status)
- [ ] (Optional) Add health endpoint to bot
- [ ] (Optional) Add admin panel monitor

---

## 📞 Support

**UptimeRobot Help:**
- Documentation: https://uptimerobot.com/help/
- Support: support@uptimerobot.com

**Your Bot Issues:**
- Check Koyeb logs first
- Use admin panel webhook fix
- Verify environment variables
- Check Supabase connection

---

**Your bot should now be monitored 24/7!** 🎉

You'll get instant alerts if it goes down, and UptimeRobot will keep it alive by pinging every 5 minutes.
