import sys
import os

# Add parent directory to path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import database
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "escrow_bot_secret_key_change_this")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'}

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        admin_password = database.get_config('admin_password') or 'admin123'
        
        if password == admin_password:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'danger')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    stats = database.get_statistics()
    users = database.get_all_users()
    users_count = len(users)
    recent_users = users[:5] if users else []
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         users_count=users_count,
                         recent_users=recent_users)

@app.route('/users')
@login_required
def users():
    all_users = database.get_all_users()
    return render_template('admin_users.html', users=all_users)

@app.route('/videos', methods=['GET', 'POST'])
@login_required
def videos():
    if request.method == 'POST':
        file_type = request.form.get('file_type')
        description = request.form.get('description', '')
        
        if 'file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(url_for('videos'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('videos'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file.filename.rsplit('.', 1)[1]}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            database.save_media_file(file_type, filepath, description)
            flash(f'Video uploaded successfully: {filename}', 'success')
        else:
            flash('Invalid file type!', 'danger')
        
        return redirect(url_for('videos'))
    
    media_files = database.get_all_media()
    return render_template('admin_videos.html', media_files=media_files)

@app.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    if request.method == 'POST':
        content_key = request.form.get('content_key')
        content_value = request.form.get('content_value')
        
        database.update_content(content_key, content_value)
        flash(f'{content_key} updated successfully!', 'success')
        return redirect(url_for('content'))
    
    # Load current content
    instructions = database.get_content('instructions', '')
    terms = database.get_content('terms', '')
    welcome = database.get_content('welcome', '')
    
    return render_template('admin_content.html',
                         instructions=instructions,
                         terms=terms,
                         welcome=welcome)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_admin':
            admin_username = request.form.get('admin_username')
            database.set_config('admin_username', admin_username)
            flash('Admin username updated!', 'success')
        
        elif action == 'update_addresses':
            database.set_config('bot_address_btc', request.form.get('btc_address', ''))
            database.set_config('bot_address_ltc', request.form.get('ltc_address', ''))
            database.set_config('bot_address_usdt_trc20', request.form.get('usdt_trc20_address', ''))
            database.set_config('bot_address_usdt_bep20', request.form.get('usdt_bep20_address', ''))
            database.set_config('bot_address_ton', request.form.get('ton_address', ''))
            flash('Crypto addresses updated!', 'success')
        
        elif action == 'update_password':
            new_password = request.form.get('new_password')
            database.set_config('admin_password', new_password)
            flash('Password updated!', 'success')
        
        elif action == 'update_stats':
            database.increment_stat('total_deals')  # This would need custom implementation
            flash('Statistics updated!', 'success')
        
        return redirect(url_for('settings'))
    
    # Load current settings
    admin_username = database.get_config('admin_username') or 'MiddleCryptoSupport'
    stats = database.get_statistics()
    
    addresses = {
        'btc': database.get_config('bot_address_btc') or '',
        'ltc': database.get_config('bot_address_ltc') or '',
        'usdt_trc20': database.get_config('bot_address_usdt_trc20') or '',
        'usdt_bep20': database.get_config('bot_address_usdt_bep20') or '',
        'ton': database.get_config('bot_address_ton') or ''
    }
    
    return render_template('admin_settings.html',
                         admin_username=admin_username,
                         stats=stats,
                         addresses=addresses)

@app.route('/session-info')
@login_required
def session_info():
    """Display Telegram session information"""
    try:
        from telethon import TelegramClient
        import asyncio
        
        # Read session file
        session_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_session.session')
        
        if not os.path.exists(session_path):
            flash('No Telegram session found!', 'warning')
            return render_template('session_manager.html', session_data=None)
        
        # Get session info using Telethon
        async def get_session_data():
            client = TelegramClient('user_session', 
                                   int(os.getenv('API_ID', '0')), 
                                   os.getenv('API_HASH', ''))
            try:
                await client.connect()
                if await client.is_user_authorized():
                    me = await client.get_me()
                    return {
                        'phone': me.phone,
                        'user_id': me.id,
                        'first_name': me.first_name,
                        'last_name': me.last_name,
                        'username': me.username,
                        'connected': True
                    }
                else:
                    return {'connected': False}
            finally:
                await client.disconnect()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session_data = loop.run_until_complete(get_session_data())
        loop.close()
        
        return render_template('session_manager.html', session_data=session_data)
    
    except Exception as e:
        flash(f'Error reading session: {e}', 'danger')
        return render_template('session_manager.html', session_data=None)

@app.route('/telegram-logout', methods=['POST'])
@login_required
def telegram_logout():
    """Logout from Telegram session"""
    try:
        session_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_session.session')
        if os.path.exists(session_path):
            os.remove(session_path)
            flash('Telegram session cleared! Please restart services and re-authenticate.', 'success')
        else:
            flash('No session file found!', 'warning')
    except Exception as e:
        flash(f'Error removing session: {e}', 'danger')
    
    return redirect(url_for('session_info'))

@app.route('/crypto-addresses', methods=['GET', 'POST'])
@login_required
def crypto_addresses():
    """Manage crypto addresses"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            currency = request.form.get('currency')
            address = request.form.get('address')
            network = request.form.get('network', '')
            label = request.form.get('label', '')
            
            if database.add_crypto_address(currency, address, network, label):
                flash(f'{currency} address added successfully!', 'success')
            else:
                flash('Error adding address!', 'danger')
        
        elif action == 'delete':
            address_id = request.form.get('address_id')
            if database.delete_crypto_address(int(address_id)):
                flash('Address deleted successfully!', 'success')
            else:
                flash('Error deleting address!', 'danger')
        
        elif action == 'update':
            address_id = request.form.get('address_id')
            currency = request.form.get('currency')
            address = request.form.get('address')
            network = request.form.get('network', '')
            label = request.form.get('label', '')
            
            if database.update_crypto_address(int(address_id), currency, address, network, label):
                flash('Address updated successfully!', 'success')
            else:
                flash('Error updating address!', 'danger')
        
        return redirect(url_for('crypto_addresses'))
    
    # Get all addresses
    addresses = database.get_crypto_addresses()
    return render_template('crypto_addresses.html', addresses=addresses)

@app.route('/webhook-manager', methods=['GET', 'POST'])
@login_required
def webhook_manager():
    \"\"\"Manage bot webhook - fix webhook issues\"\"\"
    import requests
    from dotenv import load_dotenv
    
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    bot_token = os.getenv('BOT_TOKEN')
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            # Delete webhook
            try:
                response = requests.post(f'https://api.telegram.org/bot{bot_token}/deleteWebhook')
                if response.json().get('ok'):
                    flash('Webhook deleted successfully!', 'success')
                else:
                    flash(f'Error: {response.json().get(\"description\")}', 'danger')
            except Exception as e:
                flash(f'Error deleting webhook: {e}', 'danger')
        
        elif action == 'set':
            # Set new webhook
            webhook_url = request.form.get('webhook_url')
            if webhook_url:
                try:
                    response = requests.post(
                        f'https://api.telegram.org/bot{bot_token}/setWebhook',
                        json={'url': webhook_url}
                    )
                    if response.json().get('ok'):
                        flash(f'Webhook set to: {webhook_url}', 'success')
                    else:
                        flash(f'Error: {response.json().get(\"description\")}', 'danger')
                except Exception as e:
                    flash(f'Error setting webhook: {e}', 'danger')
        
        elif action == 'fix':
            # Fix webhook: Delete old and set to polling mode
            try:
                response = requests.post(f'https://api.telegram.org/bot{bot_token}/deleteWebhook')
                if response.json().get('ok'):
                    flash('Webhook deleted! Bot is now in polling mode. Please restart bot.', 'success')
                else:
                    flash(f'Error: {response.json().get(\"description\")}', 'danger')
            except Exception as e:
                flash(f'Error fixing webhook: {e}', 'danger')
        
        return redirect(url_for('webhook_manager'))
    
    # Get current webhook info
    webhook_info = {}
    try:
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/getWebhookInfo')
        if response.json().get('ok'):
            webhook_info = response.json().get('result', {})
    except Exception as e:
        flash(f'Error getting webhook info: {e}', 'warning')
    
    return render_template('webhook_manager.html', webhook_info=webhook_info)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Admin Panel Starting...")
    print("📍 URL: http://localhost:5000")
    print("🔐 Default Password: admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
