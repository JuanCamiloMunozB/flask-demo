from app.models.user import User
from app.core.extensions import db
from app.core.exceptions import AuthenticationError, ValidationError
from sqlalchemy.exc import IntegrityError


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register_user(username: str, password: str) -> User:    
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValidationError("Username already exists")
        
        user = User(username=username)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValidationError("Username already exists")
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """Authenticate a user with username and password."""
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid credentials")
        
        return user
