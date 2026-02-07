import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

# Import database with error handling
try:
    import database
    DB_AVAILABLE = True
except Exception as e:
    print(f"Database import error: {e}")
    DB_AVAILABLE = False
    class database:
        @staticmethod
        def get_statistics():
            return {'total_deals': 0, 'disputes_resolved': 0}
        @staticmethod
        def get_all_bot_users():
            return []
        @staticmethod
        def get_config(key):
            return None
        @staticmethod
        def update_config(key, value):
            return False
        @staticmethod
        def get_all_editable_content():
            return []
        @staticmethod
        def update_editable_content(key, content):
            return False

# MONKEY PATCH: Ensure update_config exists regardless of which database.py is loaded
if DB_AVAILABLE and not hasattr(database, 'update_config'):
    print("⚠️ Monkey-patching database.update_config")
    def _update_config(key, value):
        try:
            if hasattr(database, 'set_config'):
                return database.set_config(key, value)
            if hasattr(database, 'supabase') and database.supabase:
                database.supabase.table('config').upsert({'key': key, 'value': value}).execute()
                return True
        except Exception as e:
            print(f"Error in monkey-patched update_config: {e}")
        return False
    database.update_config = _update_config
            return False
        @staticmethod
        def get_crypto_addresses():
            return []
        @staticmethod
        def add_crypto_address(currency, address, network='', label=''):
            return False
        @staticmethod
        def delete_crypto_address(address_id):
            return False
        @staticmethod
        def update_crypto_address(address_id, currency, address, network='', label=''):
            return False

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "escrow_bot_secret_key_change_this_in_production")
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'}

# Create uploads directory safely
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except:
    pass

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'escrow-admin-panel', 'db_available': DB_AVAILABLE}), 200

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            password = request.form.get('password')
            admin_password = os.getenv('ADMIN_PANEL_PASSWORD', 'admin123')
            
            if password == admin_password:
                session['logged_in'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password!', 'danger')
        
        return render_template('admin_login.html')
    except Exception as e:
        print(f"Login error: {e}")
        return f"Login error: {str(e)}", 500

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    try:
        stats = database.get_statistics() or {'total_deals': 0, 'disputes_resolved': 0}
        users = database.get_all_bot_users() or []
        return render_template('admin_dashboard.html', stats=stats, users=users)
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return f"Dashboard error: {str(e)}<br>DB Available: {DB_AVAILABLE}", 500

@app.route('/users')
@login_required
def users():
    try:
        all_users = database.get_all_bot_users() or []
        return render_template('admin_users.html', users=all_users)
    except Exception as e:
        print(f"Users error: {e}")
        return f"Error loading users: {str(e)}", 500

@app.route('/videos', methods=['GET', 'POST'])
@login_required
def videos():
    try:
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
                
        uploaded_files = []
        try:
            uploaded_files = os.listdir(app.config['UPLOAD_FOLDER']) if os.path.exists(app.config['UPLOAD_FOLDER']) else []
        except:
            pass
        return render_template('admin_videos.html', files=uploaded_files)
    except Exception as e:
        print(f"Videos error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    try:
        if request.method == 'POST':
            key = request.form.get('key')
            content_text = request.form.get('content')
            
            if database.update_editable_content(key, content_text):
                flash('Content updated successfully!', 'success')
            else:
                flash('Error updating content!', 'danger')
                
        all_content = database.get_all_editable_content() or []
        return render_template('admin_content.html', contents=all_content)
    except Exception as e:
        print(f"Content error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    try:
        if request.method == 'POST':
            # Password Update
            new_password = request.form.get('new_password')
            if new_password:
                if database.update_config('admin_password', new_password):
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Error updating password!', 'danger')
            
            # Telegram Config Update
            api_id = request.form.get('api_id')
            api_hash = request.form.get('api_hash')
            phone = request.form.get('phone')
            
            if api_id:
                database.update_config('telegram_api_id', api_id)
            if api_hash:
                database.update_config('telegram_api_hash', api_hash)
            if phone:
                database.update_config('telegram_phone', phone)
            
            if api_id or api_hash or phone:
                flash('Telegram settings updated!', 'success')
                    
        config = {
            'admin_username': database.get_config('admin_username') or 'admin',
            'admin_password': database.get_config('admin_password') or 'Not set',
            'api_id': database.get_config('telegram_api_id') or '',
            'api_hash': database.get_config('telegram_api_hash') or '',
            'phone': database.get_config('telegram_phone') or ''
        }
        return render_template('admin_settings.html', config=config)
    except Exception as e:
        print(f"Settings error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/telegram-config', methods=['GET', 'POST'])
@login_required
def telegram_config():
    try:
        if request.method == 'POST':
            api_id = request.form.get('api_id')
            api_hash = request.form.get('api_hash')
            phone = request.form.get('phone')
            
            if api_id:
                database.update_config('telegram_api_id', api_id)
            if api_hash:
                database.update_config('telegram_api_hash', api_hash)
            if phone:
                database.update_config('telegram_phone', phone)
            
            flash('Telegram credentials saved!', 'success')
            return redirect(url_for('telegram_config'))
        
        config = {
            'api_id': database.get_config('telegram_api_id') or '',
            'api_hash': database.get_config('telegram_api_hash') or '',
            'phone': database.get_config('telegram_phone') or ''
        }
        
        return render_template('telegram_config.html', config=config)
    except Exception as e:
        print(f"Telegram config error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/telegram-logout', methods=['POST'])
@login_required
def telegram_logout():
    try:
        if 'tg_phone' in session:
            database.delete_telegram_session(session['tg_phone'])
        
        session.pop('tg_step', None)
        session.pop('tg_phone', None)
        session.pop('tg_phone_code_hash', None)
        session.pop('tg_temp_session', None)
        
        flash('Logged out from Telegram', 'success')
        return redirect(url_for('telegram_login'))
    except Exception as e:
        flash(f"Error logging out: {e}", 'danger')
        return redirect(url_for('telegram_login'))

@app.route('/telegram-login', methods=['GET', 'POST'])
@login_required
def telegram_login():
    """Telegram login page with working authentication"""
    try:
        import asyncio
        import sys
        import os
        
        # Add current directory to path for imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from telegram_auth import TelegramAuth
    except ImportError as e:
        flash(f'Telegram authentication module not available: {str(e)}', 'danger')
        return render_template('telegram_login.html', session_data=None, login_step='phone', phone=None)
    
    # Check for existing session
    session_data = database.get_telegram_admin_session()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'start_over':
            # Clear all telegram session data
            session.pop('tg_step', None)
            session.pop('tg_phone', None)
            session.pop('tg_phone_code_hash', None)
            session.pop('tg_temp_session', None)
            flash('Started over. Please enter your phone number.', 'info')
            return redirect(url_for('telegram_login'))
        
        if action == 'send_code':
            phone = request.form.get('phone')
            if not phone:
                flash('Please enter your phone number', 'danger')
                return redirect(url_for('telegram_login'))
            
            # Send verification code
            auth = TelegramAuth()
            try:
                result = asyncio.run(auth.send_code(phone))
                if result['success']:
                    session['tg_phone'] = phone
                    session['tg_temp_session'] = result['temp_session']
                    session['tg_phone_code_hash'] = result['phone_code_hash']
                    session['tg_step'] = 'code'
                    flash(f"✅ Code sent to {phone}! Enter it below.", 'success')
                else:
                    flash(f"Error: {result.get('error', 'Unknown error')}", 'danger')
            except Exception as e:
                flash(f"Error sending code: {str(e)}", 'danger')
            
            return redirect(url_for('telegram_login'))
        
        elif action == 'verify_code':
            phone = session.get('tg_phone')
            temp_session = session.get('tg_temp_session')
            phone_code_hash = session.get('tg_phone_code_hash')
            code = request.form.get('code')
            
            if not all([phone, temp_session, phone_code_hash, code]):
                flash('Session expired. Please start over.', 'danger')
                session.pop('tg_step', None)
                return redirect(url_for('telegram_login'))
            
            # Verify code
            auth = TelegramAuth()
            try:
                result = asyncio.run(auth.verify_code(temp_session, phone, code, phone_code_hash))
                
                if result['success']:
                    # Save session
                    save_result = database.save_telegram_session(
                        result['session_string'],
                        phone,
                        result['user_data']
                    )
                    
                    if save_result:
                        flash(f'🎉 SUCCESS! Logged in as User ID: {result["user_data"]["id"]}', 'success')
                    else:
                        flash('⚠️ Login successful but failed to save session.', 'warning')
                    
                    # Clear session data
                    session.pop('tg_step', None)
                    session.pop('tg_phone', None)
                    session.pop('tg_temp_session', None)
                    session.pop('tg_phone_code_hash', None)
                elif result.get('requires_password'):
                    session['tg_step'] = 'password'
                    session['tg_temp_session'] = result['temp_session']
                    flash('2FA enabled. Enter your password.', 'info')
                else:
                    flash(result.get('error', 'Invalid code'), 'danger')
            except Exception as e:
                flash(f"Error: {str(e)}", 'danger')
            
            return redirect(url_for('telegram_login'))
            
        elif action == 'verify_password':
            password = request.form.get('password')
            temp_session = session.get('tg_temp_session')
            
            if not password or not temp_session:
                flash('Please enter your password', 'danger')
                return redirect(url_for('telegram_login'))
            
            auth = TelegramAuth()
            try:
                result = asyncio.run(auth.verify_password(temp_session, password))
                
                if result['success']:
                    phone = session.get('tg_phone')
                    database.save_telegram_session(
                        result['session_string'],
                        phone,
                        result['user_data']
                    )
                    flash('Successfully logged in with 2FA!', 'success')
                    session.pop('tg_step', None)
                    session.pop('tg_phone', None)
                    session.pop('tg_phone_code_hash', None)
                    session.pop('tg_temp_session', None)
                else:
                    flash(f"Error: {result.get('error', 'Invalid password')}", 'danger')
            except Exception as e:
                flash(f"Error verifying password: {str(e)}", 'danger')
            
            return redirect(url_for('telegram_login'))
            
        elif action == 'logout':
             if session_data:
                database.delete_telegram_session(session_data['phone'])
                flash('Logged out from Telegram', 'success')
             return redirect(url_for('telegram_login'))

    # GET request
    login_step = session.get('tg_step', 'phone')
    return render_template('telegram_login.html',
                         session_data=session_data,
                         login_step=login_step,
                         phone=session.get('tg_phone'))

@app.route('/crypto-addresses', methods=['GET', 'POST'])
@login_required
def crypto_addresses():
    try:
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
        
        addresses = database.get_crypto_addresses() or []
        return render_template('crypto_addresses.html', addresses=addresses)
    except Exception as e:
        print(f"Crypto addresses error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/webhook-manager', methods=['GET', 'POST'])
@login_required
def webhook_manager():
    try:
        import requests
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            flash('BOT_TOKEN not configured in environment variables', 'danger')
            return render_template('webhook_manager.html', webhook_info={})
        
        base_url = 'https://api.telegram.org/bot' + bot_token
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'delete':
                try:
                    response = requests.post(base_url + '/deleteWebhook', timeout=10)
                    result = response.json()
                    if result.get('ok'):
                        flash('Webhook deleted successfully!', 'success')
                    else:
                        flash('Error: ' + result.get('description', 'Unknown error'), 'danger')
                except Exception as e:
                    flash('Error deleting webhook: ' + str(e), 'danger')
            
            elif action == 'set':
                webhook_url = request.form.get('webhook_url')
                if webhook_url:
                    try:
                        response = requests.post(base_url + '/setWebhook', json={'url': webhook_url}, timeout=10)
                        result = response.json()
                        if result.get('ok'):
                            flash('Webhook set to: ' + webhook_url, 'success')
                        else:
                            flash('Error: ' + result.get('description', 'Unknown error'), 'danger')
                    except Exception as e:
                        flash('Error setting webhook: ' + str(e), 'danger')
            
            elif action == 'fix':
                try:
                    response = requests.post(base_url + '/deleteWebhook', timeout=10)
                    result = response.json()
                    if result.get('ok'):
                        flash('Webhook deleted! Bot is now in polling mode.', 'success')
                    else:
                        flash('Error: ' + result.get('description', 'Unknown error'), 'danger')
                except Exception as e:
                    flash('Error fixing webhook: ' + str(e), 'danger')
            
            return redirect(url_for('webhook_manager'))
        
        webhook_info = {}
        try:
            response = requests.get(base_url + '/getWebhookInfo', timeout=10)
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
        except Exception as e:
            flash('Error getting webhook info: ' + str(e), 'warning')
        
        return render_template('webhook_manager.html', webhook_info=webhook_info)
    except Exception as e:
        print(f"Webhook manager error: {e}")
        return f"Error: {str(e)}", 500

# For local testing
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Admin Panel Starting...")
    print("📍 URL: http://localhost:5000")
    print("🔐 Default Password: admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
