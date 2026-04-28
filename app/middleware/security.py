from flask import session, request, redirect, url_for, flash


def register_security_hooks(app):
    """Registers before/after request security hooks on the app."""

    @app.before_request
    def verify_session_integrity():
        """
        Session Hijacking Protection:
        Locks the session to the user's IP and User-Agent.
        If a cookie is stolen and replayed from a different device,
        the mismatch triggers an automatic logout.
        """
        if 'user_id' in session:
            if (session.get('ip') != request.remote_addr or
                    session.get('user_agent') != request.headers.get('User-Agent')):
                session.clear()
                flash('Security Alert: Session terminated due to suspicious activity.', 'error')
                return redirect(url_for('auth.login'))

    @app.after_request
    def add_security_headers(response):
        """Adds production-grade security headers to every response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response
