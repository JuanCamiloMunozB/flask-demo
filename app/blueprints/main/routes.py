from flask import redirect, url_for
from flask_login import current_user
from . import main


@main.route('/')
def index():
    """Root route - redirect based on authentication status."""
    if current_user.is_authenticated:
        return redirect(url_for('bot.index'))
    return redirect(url_for('auth.login'))


@main.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'healthy'}, 200
