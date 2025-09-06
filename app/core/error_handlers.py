from flask import jsonify, render_template, request, current_app
from app.core.exceptions import (
    BaseApplicationError, ValidationError, AuthenticationError,
    NotFoundError, DatabaseError, ExpertSystemError, InvalidRequestError,
    SportNotSupportedError, SessionNotFoundError, SessionInactiveError,
    NoActiveSportError
)
from sqlalchemy.exc import OperationalError, IntegrityError


def register_error_handlers(app):
    """Register all error handlers with the app."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors."""
        current_app.logger.warning(f"Validation error: {error.message}")
        
        if request.is_json:
            return jsonify({
                'error': error.error_code,
                'message': error.message,
                'field': getattr(error, 'field', None)
            }), error.status_code
        
        # For form submissions, flash the error and re-render with form
        from flask import flash
        flash(error.message, 'error')
        
        # Determine which form to create based on the endpoint
        if request.endpoint == 'auth.register':
            from app.blueprints.auth.forms import RegisterForm
            form = RegisterForm()
            template = 'auth/register.html'
        elif request.endpoint == 'auth.login':
            from app.blueprints.auth.forms import LoginForm
            form = LoginForm()
            template = 'auth/login.html'
        else:
            # Fallback for other endpoints
            template = request.endpoint.split('.')[-1] + '.html'
            return render_template(template), error.status_code
        
        return render_template(template, form=form), error.status_code
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        """Handle authentication errors."""
        current_app.logger.warning(f"Authentication error: {error.message}")
        
        if request.is_json:
            return jsonify({
                'error': error.error_code,
                'message': error.message
            }), error.status_code
        
        from flask import flash
        from app.blueprints.auth.forms import LoginForm
        flash(error.message, 'error')
        form = LoginForm()
        
        # Preserve form data if available
        if request.method == 'POST':
            form.process(request.form)
            # Clear password field for security
            form.password.data = ''
        
        return render_template('auth/login.html', form=form), error.status_code
    
    @app.errorhandler(NotFoundError)
    @app.errorhandler(SessionNotFoundError)
    def handle_not_found_error(error):
        """Handle not found errors."""
        current_app.logger.info(f"Not found error: {error.message}")
        
        if request.is_json:
            return jsonify({
                'error': error.error_code,
                'message': error.message,
                'resource_type': getattr(error, 'resource_type', None)
            }), error.status_code
        
        return render_template('errors/404.html'), error.status_code
    
    @app.errorhandler(InvalidRequestError)
    def handle_invalid_request_error(error):
        """Handle invalid request errors."""
        current_app.logger.warning(f"Invalid request: {error.message}")
        
        return jsonify({
            'error': error.error_code,
            'message': error.message,
            'missing_param': getattr(error, 'missing_param', None)
        }), error.status_code
    
    @app.errorhandler(SportNotSupportedError)
    def handle_sport_not_supported_error(error):
        """Handle unsupported sport errors."""
        current_app.logger.warning(f"Unsupported sport: {error.message}")
        
        return jsonify({
            'error': error.error_code,
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(SessionInactiveError)
    def handle_session_inactive_error(error):
        """Handle inactive session errors."""
        current_app.logger.info(f"Session inactive: {error.message}")
        
        return jsonify({
            'error': error.error_code,
            'message': "La conversación ya terminó. Selecciona otro deporte para comenzar de nuevo.",
            'finished': True
        }), 200  # Return 200 for inactive sessions as it's expected behavior
    
    @app.errorhandler(NoActiveSportError)
    def handle_no_active_sport_error(error):
        """Handle no active sport errors."""
        current_app.logger.info(f"No active sport: {error.message}")
        
        return jsonify({
            'error': error.error_code,
            'message': error.message,
            'finished': False
        }), error.status_code
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        """Handle database errors."""
        current_app.logger.error(f"Database error: {error.message}")
        
        if request.is_json:
            return jsonify({
                'error': error.error_code,
                'message': "Database operation failed"
            }), error.status_code
        
        return render_template('errors/500.html'), error.status_code
    
    @app.errorhandler(ExpertSystemError)
    def handle_expert_system_error(error):
        """Handle expert system errors."""
        current_app.logger.error(f"Expert system error: {error.message}")
        
        # For expert system errors, return a graceful fallback response
        return jsonify({
            'message': 'Estoy procesando tu información...',
            'is_final': False,
            'next_fact': None
        }), 200
    
    @app.errorhandler(OperationalError)
    def handle_operational_error(error):
        """Handle SQLAlchemy operational errors."""
        current_app.logger.error(f"Database operational error: {str(error)}")
        
        if request.is_json:
            return jsonify({
                'error': 'database_connection_error',
                'message': 'Database connection failed'
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle SQLAlchemy integrity errors."""
        current_app.logger.warning(f"Database integrity error: {str(error)}")
        
        # Common integrity errors
        if 'UNIQUE constraint failed' in str(error) or 'unique constraint' in str(error).lower():
            message = "This record already exists"
        else:
            message = "Data integrity error"
        
        if request.is_json:
            return jsonify({
                'error': 'integrity_error',
                'message': message
            }), 400
        
        from flask import flash
        flash(message, 'error')
        
        # Create appropriate form based on endpoint
        if request.endpoint == 'auth.register':
            from app.blueprints.auth.forms import RegisterForm
            form = RegisterForm()
            if request.method == 'POST':
                form.process(request.form)
                # Clear password fields for security
                form.password.data = ''
                form.confirm.data = ''
            template = 'auth/register.html'
        elif request.endpoint == 'auth.login':
            from app.blueprints.auth.forms import LoginForm
            form = LoginForm()
            if request.method == 'POST':
                form.process(request.form)
                form.password.data = ''
            template = 'auth/login.html'
        else:
            # Fallback for other endpoints
            template = request.endpoint.split('.')[-1] + '.html'
            return render_template(template), 400
        
        return render_template(template, form=form), 400
    
    @app.errorhandler(BaseApplicationError)
    def handle_base_application_error(error):
        """Handle any other application errors."""
        current_app.logger.error(f"Application error: {error.message}")
        
        if request.is_json:
            return jsonify({
                'error': error.error_code or 'application_error',
                'message': error.message
            }), error.status_code
        
        return render_template('errors/500.html'), error.status_code
    
    @app.errorhandler(404)
    def handle_404_error(error):
        """Handle 404 errors."""
        current_app.logger.info(f"404 error: {request.url}")
        
        if request.is_json:
            return jsonify({
                'error': 'not_found',
                'message': 'Endpoint not found'
            }), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def handle_500_error(error):
        """Handle 500 errors."""
        current_app.logger.error(f"500 error: {str(error)}")
        
        # Rollback any pending database transactions
        from app.core.extensions import db
        try:
            db.session.rollback()
        except:
            pass
        
        if request.is_json:
            return jsonify({
                'error': 'internal_server_error',
                'message': 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors."""
        current_app.logger.exception(f"Unexpected error: {str(error)}")
        
        # Rollback any pending database transactions
        from app.core.extensions import db
        try:
            db.session.rollback()
        except:
            pass
        
        if request.is_json:
            return jsonify({
                'error': 'unexpected_error',
                'message': 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500
