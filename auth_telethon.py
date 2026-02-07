import os
import asyncio
from telethon.sync import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE_NUMBER')
PASSWORD = 'DEVASHISHSWAMIOP'

async def main():
    client = TelegramClient('user_session', API_ID, API_HASH)
    await client.start(phone=PHONE, password=PASSWORD)
    print('✅ Successfully authenticated!')
    print(f'Connected: {await client.is_user_authorized()}')
    me = await client.get_me()
    print(f'Logged in as: {me.first_name}')
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
