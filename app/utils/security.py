import hmac
import hashlib
import os
from flask import session, current_app, request, abort

def generate_csrf_token():
    """Generates a CSRF token for the current session if one doesn't exist."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(32).hex()
    return session['_csrf_token']

def verify_csrf_token():
    """Verifies the CSRF token in the request against the session token."""
    if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
        return

    # Check both form field and header (for AJAX)
    token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    
    stored_token = session.get('_csrf_token')
    
    if not stored_token or not token or not hmac.compare_digest(stored_token, token):
        current_app.logger.warning(f"CSRF validation failed for IP: {request.remote_addr}")
        abort(403, description="CSRF validation failed. Request denied.")
