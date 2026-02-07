# How to Create Telegram Groups with Saved Session

## Overview
After logging in through the admin panel, your Telegram session is saved in the database. You can use this session to create groups programmatically.

## Step 1: Get Your Saved Session

```python
from api.database import get_telegram_session

# Get the saved session
session_data = get_telegram_session()

if session_data:
    session_string = session_data['session_string']
    user_id = session_data['user_id']
    phone = session_data['phone']
    print(f"Logged in as User ID: {user_id}")
else:
    print("No active Telegram session found. Please login first.")
```

## Step 2: Create a Telegram Client

```python
import asyncio
from api.telegram_auth import get_telegram_client

async def main():
    session_data = get_telegram_session()
    if not session_data:
        return
    
    # Get client from saved session
    client = await get_telegram_client(session_data['session_string'])
    
    if client:
        # Client is ready to use!
        me = await client.get_me()
        print(f"Logged in as: {me.first_name}")
        
        # Don't forget to disconnect when done
        await client.disconnect()
    else:
        print("Session expired or invalid")

# Run it
asyncio.run(main())
```

## Step 3: Create an Escrow Group

```python
from api.telegram_auth import create_escrow_group

async def create_group_example():
    session_data = get_telegram_session()
    if not session_data:
        print("Please login first")
        return
    
    # Create a group
    result = await create_escrow_group(
        session_data['session_string'],
        title="Escrow #12345",
        description="Escrow transaction between Buyer and Seller"
    )
    
    if result['success']:
        print(f"✅ Group created! ID: {result['group_id']}")
        return result['group_id']
    else:
        print(f"❌ Error: {result['error']}")

# Run it
asyncio.run(create_group_example())
```

## Step 4: Complete Bot Integration Example

```python
# In your bot.py file
from api.database import get_telegram_session
from api.telegram_auth import get_telegram_client

async def create_escrow_transaction_group(deal_id, buyer_username, seller_username):
    """Create a group for an escrow transaction"""
    
    # Get saved admin session
    session_data = get_telegram_session()
    if not session_data:
        return None
    
    # Create client
    client = await get_telegram_client(session_data['session_string'])
    if not client:
        return None
    
    try:
        # Create the group
        title = f"Escrow Deal #{deal_id}"
        description = f"Transaction between @{buyer_username} and @{seller_username}"
        
        result = await client.create_channel(
            title=title,
            about=description,
            megagroup=True  # This makes it a supergroup
        )
        
        group_id = result.chats[0].id
        
        # Add the buyer and seller
        buyer = await client.get_entity(buyer_username)
        seller = await client.get_entity(seller_username)
        
        await client.add_chat_user(group_id, buyer)
        await client.add_chat_user(group_id, seller)
        
        # Send welcome message
        await client.send_message(group_id, 
            f"🛡️ **Escrow Deal #{deal_id}**\n\n"
            f"Buyer: @{buyer_username}\n"
            f"Seller: @{seller_username}\n\n"
            f"This group is for this transaction only. "
            f"All communication should happen here."
        )
        
        await client.disconnect()
        
        return group_id
        
    except Exception as e:
        print(f"Error creating group: {e}")
        if client.is_connected():
            await client.disconnect()
        return None

# Usage in your bot
async def handle_new_deal(deal_id, buyer_username, seller_username):
    group_id = await create_escrow_transaction_group(
        deal_id, 
        buyer_username, 
        seller_username
    )
    
    if group_id:
        # Save group_id to database with the deal
        print(f"✅ Created group {group_id} for deal {deal_id}")
    else:
        print(f"❌ Failed to create group for deal {deal_id}")
```

## Important Notes

### Session Persistence
✅ Session is stored in database (Supabase)
✅ Works across serverless function restarts
✅ Persists until you manually logout
✅ No files needed - perfect for Vercel!

### Security
🔒 Session string is sensitive - keep it secure
🔒 Don't log or expose session strings
🔒 Only the admin who logged in has those permissions

### Best Practices
1. Always disconnect the client when done
2. Use try-except blocks for error handling
3. Check if session exists before using it
4. Handle Telegram API rate limits

## Quick Reference

```python
# Get session
from api.database import get_telegram_session
session_data = get_telegram_session()

# Create client
from api.telegram_auth import get_telegram_client
client = await get_telegram_client(session_data['session_string'])

# Create group (quick method)
from api.telegram_auth import create_escrow_group
result = await create_escrow_group(session_string, "Group Name", "Description")

# Manual group creation
result = await client.create_channel(
    title="Group Name",
    about="Description", 
    megagroup=True
)
group_id = result.chats[0].id
```

## Saved Session Data Structure

```python
{
    'session_string': 'AQ11a2b3c4d...', # The actual Telegram session
    'phone': '+1234567890',              # Phone number
    'user_id': 123456789,                # Telegram User ID
    'username': 'myusername',            # Username (if set)
    'first_name': 'John',                # First name
    'last_name': 'Doe',                  # Last name (if set)
    'created_at': '2026-02-08...',       # When logged in
    'updated_at': '2026-02-08...'        # Last used
}
```

## Ready to Use!
After logging in through the admin panel's Telegram page, your session is automatically saved and ready to create groups! 🎉
