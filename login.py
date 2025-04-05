from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from functools import wraps
import os
from datetime import datetime, timedelta

# In-memory token storage as fallback
memory_tokens = {}

# Try to connect to MongoDB, use memory storage if it fails
try:
    # MongoDB connection - using environment variable for security
    MONGO_URI = os.environ.get('MONGO_URI', "MONGO_URI")
    client = MongoClient(MONGO_URI)
    db = client['terabox_bot']
    users_collection = db['users']
    
    # Test the connection
    client.admin.command('ping')
    print("MongoDB connection successful")
    use_mongodb = True
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    print("Using in-memory token storage instead")
    use_mongodb = False

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        
        token = session['token']
        
        # Check if token exists and is valid
        if use_mongodb:
            user_doc = users_collection.find_one({'token': token})
            is_valid = user_doc and user_doc.get('token_expiration', datetime.min) > datetime.now()
        else:
            user_doc = memory_tokens.get(token)
            is_valid = user_doc and user_doc.get('token_expiration') > datetime.now()
        
        if not is_valid:
            # Token not found or expired
            session.pop('token', None)
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def init_login_routes(app):
    # Template filter for timestamp conversion
    @app.template_filter('timestamp_to_date')
    def timestamp_to_date(timestamp):
        if isinstance(timestamp, datetime):
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            token = request.form.get('token')
            if not token:
                return render_template('login.html', error='Please enter a token')
            
            # Check if token exists and is valid
            if use_mongodb:
                user_doc = users_collection.find_one({'token': token})
                is_valid = user_doc and user_doc.get('token_expiration', datetime.min) > datetime.now()
            else:
                user_doc = memory_tokens.get(token)
                is_valid = user_doc and user_doc.get('token_expiration') > datetime.now()
            
            if is_valid:
                session['token'] = token
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid or expired token. Please get a new token from Telegram bot.')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('token', None)
        return redirect(url_for('login'))
        
    # Development testing route to create a token
    @app.route('/dev/create_token')
    def create_dev_token():
        if not app.debug:
            return "Only available in debug mode", 403
            
        # Create a token valid for 24 hours
        token = os.urandom(16).hex()
        token_expiration = datetime.now() + timedelta(hours=24)
        
        if use_mongodb:
            users_collection.update_one(
                {"user_id": 999999},  # Dev user ID
                {"$set": {
                    "token": token,
                    "token_expiration": token_expiration,
                    "verified_until": datetime.min
                }},
                upsert=True
            )
        else:
            memory_tokens[token] = {
                "user_id": 999999,
                "token": token,
                "token_expiration": token_expiration
            }
            
        return f"Development token created: {token} (valid for 24 hours)" 
