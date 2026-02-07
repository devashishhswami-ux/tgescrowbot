# Middle Crypto Bot Setup

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Configuration
Open `config.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual Telegram Bot Token from @BotFather.

```python
BOT_TOKEN = "123456789:ABC..." 
```

## 3. Run the Bot
```bash
python bot.py
```

## Features Implemented
- **Exact UI Replication**: Matches the "Middle Crypto Bot" text and emojis.
- **Role Registration**: 
    - `/seller <address>`
    - `/buyer <address>`
    - **Auto-Detection**: Paste a crypto address, and the bot offers buttons to register.
- **Inline Buttons**:
    - `WHAT IS ESCROW`, `INSTRUCTIONS`, `TERMS`.
    - `CREATE ESCROW GROUP`: Links to add the bot to a group.

## Database
The bot uses `escrow.db` (SQLite) to store user roles. This file is created automatically.
