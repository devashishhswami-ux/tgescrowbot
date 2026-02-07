"""
Telegram Authentication Module
Uses Telethon with StringSession for serverless compatibility
Fixed for stateless serverless environment
"""
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError

class TelegramAuth:
    def __init__(self):
        self.api_id = os.getenv('API_ID', '34829504')
        self.api_hash = os.getenv('API_HASH', '')
        self.client = None
        self.phone = None
        
    async def send_code(self, phone):
        """Send verification code to phone number"""
        try:
            # Create client with empty StringSession for new login
            self.client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await self.client.connect()
            
            # Send code
            self.phone = phone
            result = await self.client.send_code_request(phone)
            
            # Important: disconnect but save the phone_code_hash
            phone_code_hash = result.phone_code_hash
            await self.client.disconnect()
            
            return {
                'success': True,
                'phone_code_hash': phone_code_hash,
                'message': f'Verification code sent to {phone}'
            }
        except Exception as e:
            if self.client:
                await self.client.disconnect()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_code(self, phone, code):
        """Verify the code and complete login - simplified for serverless"""
        try:
            # Create a fresh client for this request
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await client.connect()
            
            # Sign in with phone and code - let Telegram handle the code_hash internally
            try:
                await client.send_code_request(phone)  # Re-request to establish session
                result = await client.sign_in(phone, code)
                
                # Get session string
                session_string = client.session.save()
                
                # Get user info
                me = await client.get_me()
                user_data = {
                    'id': me.id,
                    'phone': me.phone,
                    'username': me.username,
                    'first_name': me.first_name,
                    'last_name': me.last_name
                }
                
                await client.disconnect()
                
                return {
                    'success': True,
                    'session_string': session_string,
                    'user_data': user_data,
                    'message': 'Successfully logged in!'
                }
                
            except SessionPasswordNeededError:
                # Save the session temporarily for 2FA continuation
                temp_session = client.session.save()
                await client.disconnect()
                
                return {
                    'success': False,
                    'requires_password': True,
                    'temp_session': temp_session,
                    'message': '2FA enabled. Please enter your password.'
                }
            
        except PhoneCodeInvalidError:
            if 'client' in locals():
                await client.disconnect()
            return {
                'success': False,
                'error': 'Invalid verification code. Please try again.'
            }
        except PhoneCodeExpiredError:
            if 'client' in locals():
                await client.disconnect()
            return {
                'success': False,
                'error': 'Verification code expired. Please request a new code.'
            }
        except Exception as e:
            if 'client' in locals():
                await client.disconnect()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_password(self, temp_session, password):
        """Verify 2FA password using temporary session"""
        try:
            # Restore the client from temporary session
            client = TelegramClient(StringSession(temp_session), self.api_id, self.api_hash)
            await client.connect()
            
            # Sign in with password
            await client.sign_in(password=password)
            
            # Get final session string
            session_string = client.session.save()
            
            # Get user info
            me = await client.get_me()
            user_data = {
                'id': me.id,
                'phone': me.phone,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
            
            await client.disconnect()
            
            return {
                'success': True,
                'session_string': session_string,
                'user_data': user_data,
                'message': 'Successfully logged in with 2FA!'
            }
            
        except Exception as e:
            if 'client' in locals():
                await client.disconnect()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_session_info(self, session_string):
        """Get info about an existing session"""
        try:
            client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return None
            
            me = await client.get_me()
            user_data = {
                'id': me.id,
                'phone': me.phone,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name
            }
            
            await client.disconnect()
            return user_data
            
        except Exception as e:
            print(f"Error getting session info: {e}")
            return None
