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
        
        # Read password ONLY from environment variable
        admin_password = os.getenv('ADMIN_PANEL_PASSWORD', 'admin123')
        
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
    users = database.get_all_bot_users()
    return render_template('admin_dashboard.html', stats=stats, users=users)

@app.route('/users')
@login_required
def users():
    all_users = database.get_all_bot_users()
    return render_template('admin_users.html', users=all_users)

@app.route('/videos', methods=['GET', 'POST'])
@login_required
def videos():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        file = request.files['video']
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash(f'Video uploaded: {filename}', 'success')
        else:
            flash('Invalid file type!', 'danger')
            
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
    return render_template('admin_videos.html', files=uploaded_files)

@app.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    if request.method == 'POST':
        key = request.form.get('key')
        content = request.form.get('content')
        
        if database.update_editable_content(key, content):
            flash('Content updated successfully!', 'success')
        else:
            flash('Error updating content!', 'danger')
            
    all_content = database.get_all_editable_content()
    return render_template('admin_content.html', contents=all_content)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        if new_password:
            if database.update_config('admin_password', new_password):
                flash('Password updated successfully!', 'success')
            else:
                flash('Error updating password!', 'danger')
                
    config = {
        'admin_username': database.get_config('admin_username'),
        'admin_password': database.get_config('admin_password')
    }
    return render_template('admin_settings.html', config=config)

@app.route('/session-info')
@login_required
def session_info():
    """Display Telegram session information"""
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_session.session')
    session_exists = os.path.exists(session_file)
    
    session_data = {
        'exists': session_exists,
        'phone': None,
        'user_id': None,
        'name': None,
        'username': None
    }
    
    if session_exists:
        try:
            from telethon.sync import TelegramClient
            from config import API_ID, API_HASH
            
            client = TelegramClient('user_session', API_ID, API_HASH)
            client.connect()
            
            if client.is_user_authorized():
                me = client.get_me()
                session_data.update({
                    'phone': me.phone,
                    'user_id': me.id,
                    'name': f"{me.first_name or ''} {me.last_name or ''}".strip(),
                    'username': me.username or 'N/A'
                })
            
            client.disconnect()
        except Exception as e:
            flash(f'Error reading session: {e}', 'warning')
    
    return render_template('session_manager.html', session_data=session_data)

@app.route('/telegram-config', methods=['GET', 'POST'])
@login_required
def telegram_config():
    """Configure Telegram API credentials for group creation"""
    if request.method == 'POST':
        api_id = request.form.get('api_id')
        api_hash = request.form.get('api_hash')
        phone = request.form.get('phone')
        
        # Save to config table
        if api_id:
            database.update_config('telegram_api_id', api_id)
        if api_hash:
            database.update_config('telegram_api_hash', api_hash)
        if phone:
            database.update_config('telegram_phone', phone)
        
        flash('Telegram credentials saved! These will be used for group creation.', 'success')
        return redirect(url_for('telegram_config'))
    
    # Get current config
    config = {
        'api_id': database.get_config('telegram_api_id') or '',
        'api_hash': database.get_config('telegram_api_hash') or '',
        'phone': database.get_config('telegram_phone') or ''
    }
    
    return render_template('telegram_config.html', config=config)

@app.route('/telegram-logout', methods=['POST'])
@login_required
def telegram_logout():
    """Logout from Telegram session"""
    session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_session.session')
    
    try:
        if os.path.exists(session_file):
            os.remove(session_file)
            flash('Telegram session cleared! Please re-authenticate with auth_telethon.py', 'success')
        else:
            flash('No session file found!', 'warning')
    except Exception as e:
        flash(f'Error clearing session: {e}', 'danger')
    
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
                flash('Address added successfully!', 'success')
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
    """Manage bot webhook - fix webhook issues"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    bot_token = os.getenv('BOT_TOKEN')
    base_url = 'https://api.telegram.org/bot' + bot_token
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'delete':
            # Delete webhook
            try:
                response = requests.post(base_url + '/deleteWebhook')
                result = response.json()
                if result.get('ok'):
                    flash('Webhook deleted successfully!', 'success')
                else:
                    error_desc = result.get('description', 'Unknown error')
                    flash('Error: ' + error_desc, 'danger')
            except Exception as e:
                flash('Error deleting webhook: ' + str(e), 'danger')
        
        elif action == 'set':
            # Set new webhook
            webhook_url = request.form.get('webhook_url')
            if webhook_url:
                try:
                    response = requests.post(base_url + '/setWebhook', json={'url': webhook_url})
                    result = response.json()
                    if result.get('ok'):
                        flash('Webhook set to: ' + webhook_url, 'success')
                    else:
                        error_desc = result.get('description', 'Unknown error')
                        flash('Error: ' + error_desc, 'danger')
                except Exception as e:
                    flash('Error setting webhook: ' + str(e), 'danger')
        
        elif action == 'fix':
            # Fix webhook: Delete old and set to polling mode
            try:
                response = requests.post(base_url + '/deleteWebhook')
                result = response.json()
                if result.get('ok'):
                    flash('Webhook deleted! Bot is now in polling mode. Please restart bot.', 'success')
                else:
                    error_desc = result.get('description', 'Unknown error')
                    flash('Error: ' + error_desc, 'danger')
            except Exception as e:
                flash('Error fixing webhook: ' + str(e), 'danger')
        
        return redirect(url_for('webhook_manager'))
    
    # Get current webhook info
    webhook_info = {}
    try:
        response = requests.get(base_url + '/getWebhookInfo')
        result = response.json()
        if result.get('ok'):
            webhook_info = result.get('result', {})
    except Exception as e:
        flash('Error getting webhook info: ' + str(e), 'warning')
    
    return render_template('webhook_manager.html', webhook_info=webhook_info)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Admin Panel Starting...")
    print("📍 URL: http://localhost:5000")
    print("🔐 Default Password: admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
