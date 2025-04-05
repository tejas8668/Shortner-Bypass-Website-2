from flask import Flask, render_template, request, jsonify, session
import cloudscraper
from bs4 import BeautifulSoup
import time
import os
import datetime
import threading
from login import token_required, init_login_routes

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # For session management

# Initialize login routes
init_login_routes(app)

# Store active sessions, retry attempts, and session creation times
active_sessions = {}
retry_attempts = {}
session_times = {}  # To track when each session was created

# Maximum session age in seconds (12 hours)
MAX_SESSION_AGE = 12 * 60 * 60
# Maximum retry attempts
MAX_RETRY_ATTEMPTS = 4

'''def Seturl_in(url, retry=False):
    client = cloudscraper.create_scraper(allow_brotli=False)
    DOMAIN = "https://set.seturl.in/"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{DOMAIN}/{code}"
    ref = "https://loan.creditsgoal.com/"
    h = {"referer": ref}
    
    try:
        resp = client.get(final_url, headers=h)
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all("input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        time.sleep(7)
        r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
        return str(r.json()["url"])
    except BaseException as e:
        if not retry:
            print(f"Error occurred: {e}. Retrying...")
            return Seturl_in(url, retry=True)
        else:
            return "Something went wrong, Please Wait For Few Seconds and try again..."'''
        
def Seturl_in(url, retry=False, session_id=None):
    # Get or create session
    if retry and session_id and session_id in active_sessions:
        client = active_sessions[session_id]
        
        # Check if max retries exceeded
        if retry_attempts.get(session_id, 0) >= MAX_RETRY_ATTEMPTS:
            return {
                "status": "error",
                "message": "Maximum retry attempts exceeded. Please refresh the page.",
                "session_id": session_id,
                "retry_count": retry_attempts.get(session_id, 0)
            }
    else:
        client = cloudscraper.create_scraper(allow_brotli=False)
        if session_id:
            active_sessions[session_id] = client
            retry_attempts[session_id] = 0
            session_times[session_id] = time.time()  # Record session creation time

    DOMAIN = "https://set.seturl.in/"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{DOMAIN}/{code}"
    ref = "https://loan.creditsgoal.com/"
    h = {"referer": ref}
    
    try:
        # Try to get the page
        resp = client.get(final_url, headers=h)
        
        # Check if we got Cloudflare challenge
        if "Just a moment" in resp.text or "Enable JavaScript" in resp.text:
            # Increment retry count if this is a retry
            if retry and session_id in retry_attempts:
                retry_attempts[session_id] += 1
                
            return {
                "status": "cloudflare",
                "message": "Cloudflare detected. Please try again.",
                "session_id": session_id,
                "retry_count": retry_attempts.get(session_id, 0)
            }
        
        # If we got past Cloudflare, process the response
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all("input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        time.sleep(7)
        r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
        return {
            "status": "success",
            "url": str(r.json()["url"])
        }
        
    except BaseException as e:
        # Increment retry count if this is a retry
        if retry and session_id in retry_attempts:
            retry_attempts[session_id] += 1
            
        return {
            "status": "error",
            "message": str(e),
            "session_id": session_id,
            "retry_count": retry_attempts.get(session_id, 0)
        }


def runurl(url, retry=False, session_id=None):
    # Get or create session
    if retry and session_id and session_id in active_sessions:
        client = active_sessions[session_id]
        
        # Check if max retries exceeded
        if retry_attempts.get(session_id, 0) >= MAX_RETRY_ATTEMPTS:
            return {
                "status": "error",
                "message": "Maximum retry attempts exceeded. Please refresh the page.",
                "session_id": session_id,
                "retry_count": retry_attempts.get(session_id, 0)
            }
    else:
        client = cloudscraper.create_scraper(allow_brotli=False)
        if session_id:
            active_sessions[session_id] = client
            retry_attempts[session_id] = 0
            session_times[session_id] = time.time()  # Record session creation time

    DOMAIN = "https://get.runurl.in/"
    url = url[:-1] if url[-1] == "/" else url
    code = url.split("/")[-1]
    final_url = f"{DOMAIN}/{code}"
    ref = "https://learna1.bgmi32bitapk.in/"
    h = {"referer": ref}
    
    try:
        # Try to get the page
        resp = client.get(final_url, headers=h)
        
        # Check if we got Cloudflare challenge
        if "Just a moment" in resp.text or "Enable JavaScript" in resp.text:
            # Increment retry count if this is a retry
            if retry and session_id in retry_attempts:
                retry_attempts[session_id] += 1
                
            return {
                "status": "cloudflare",
                "message": "Cloudflare detected. Please try again.",
                "session_id": session_id,
                "retry_count": retry_attempts.get(session_id, 0)
            }
        
        # If we got past Cloudflare, process the response
        soup = BeautifulSoup(resp.content, "html.parser")
        inputs = soup.find_all("input")
        data = {input.get("name"): input.get("value") for input in inputs}
        h = {"x-requested-with": "XMLHttpRequest"}
        time.sleep(7)
        r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
        return {
            "status": "success",
            "url": str(r.json()["url"])
        }
        
    except BaseException as e:
        # Increment retry count if this is a retry
        if retry and session_id in retry_attempts:
            retry_attempts[session_id] += 1
            
        return {
            "status": "error",
            "message": str(e),
            "session_id": session_id,
            "retry_count": retry_attempts.get(session_id, 0)
        }

@app.route('/')
@token_required
def home():
    return render_template('index.html')

@app.route('/process_url', methods=['POST'])
@token_required
def process_url():
    # Clean up old sessions before processing new requests
    cleanup_old_sessions()
    
    url = request.form.get('url')
    retry = request.form.get('retry', 'false').lower() == 'true'
    session_id = request.form.get('session_id')
    
    if not url:
        return jsonify({'error': 'Please provide a URL'})
    
    # Generate a new session ID if not provided
    if not session_id:
        session_id = os.urandom(16).hex()
    
    # Check which domain the URL belongs to
    if "runurl.in" in url:
        result = runurl(url, retry, session_id)
    elif "seturl.in" in url:
        result = Seturl_in(url, retry, session_id)
    else:
        return jsonify({'status': 'error', 'message': 'Unsupported URL. Only runurl.in and seturl.in are supported.'})
    
    # If no session ID in result, add it
    if result.get('status') in ['cloudflare', 'error'] and 'session_id' not in result:
        result['session_id'] = session_id
        
    # Add retry count if not already present
    if 'retry_count' not in result:
        result['retry_count'] = retry_attempts.get(session_id, 0)
    
    return jsonify(result)

@app.route('/reset_session', methods=['POST'])
@token_required
def reset_session():
    session_id = request.form.get('session_id')
    
    # Clean up the session
    cleanup_session(session_id)
        
    return jsonify({'status': 'success', 'message': 'Session reset successfully'})

# Cleanup function for a specific session
def cleanup_session(session_id):
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    if session_id in retry_attempts:
        del retry_attempts[session_id]
        
    if session_id in session_times:
        del session_times[session_id]

# Cleanup function for old sessions
def cleanup_old_sessions():
    current_time = time.time()
    sessions_to_remove = []
    
    # Find old sessions
    for session_id, creation_time in session_times.items():
        if current_time - creation_time > MAX_SESSION_AGE:
            sessions_to_remove.append(session_id)
    
    # Remove old sessions
    for session_id in sessions_to_remove:
        cleanup_session(session_id)
    
    if sessions_to_remove:
        print(f"Cleaned up {len(sessions_to_remove)} old sessions")

# Function to periodically clean up old sessions
def schedule_cleanup():
    while True:
        # Sleep for 1 hour
        time.sleep(3600)
        cleanup_old_sessions()

if __name__ == '__main__':
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
    cleanup_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 