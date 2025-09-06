from typing import List, Optional
from app.models.chat import ChatSession, ChatMessage
from app.core.extensions import db
from app.core.exceptions import DatabaseError
from sqlalchemy.exc import SQLAlchemyError


class ChatService:
    """Service for handling chat operations."""
    
    @staticmethod
    def create_session(user_id: int, sport: str, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session."""
        if not title:
            title = f"{sport.capitalize()} • Usuario"
        
        try:
            session = ChatSession(
                user_id=user_id,
                sport=sport,
                title=title
            )
            db.session.add(session)
            db.session.flush()  # Get the ID
            db.session.commit()
            return session
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create chat session: {str(e)}")
    
    @staticmethod
    def add_message(session_id: int, role: str, content: str, meta: Optional[dict] = None) -> ChatMessage:
        """Add a message to a chat session."""
        if meta is None:
            meta = {}
        
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                meta=meta
            )
            db.session.add(message)
            db.session.commit()
            return message
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to add message: {str(e)}")
    
    @staticmethod
    def get_user_sessions(user_id: int, limit: int = 50) -> List[ChatSession]:
        """Get chat sessions for a user."""
        try:
            return (ChatSession.query
                   .filter_by(user_id=user_id)
                   .order_by(ChatSession.updated_at.desc())
                   .limit(limit)
                   .all())
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get user sessions: {str(e)}")
    
    @staticmethod
    def get_session_by_id(session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a specific chat session by ID for a user."""
        try:
            return ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get session: {str(e)}")
    
    @staticmethod
    def get_session_messages(session_id: int) -> List[ChatMessage]:
        """Get all messages for a chat session."""
        try:
            return (ChatMessage.query
                   .filter_by(session_id=session_id)
                   .order_by(ChatMessage.created_at.asc())
                   .all())
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get session messages: {str(e)}")
    
    @staticmethod
    def end_session(session_id: int, user_id: int) -> bool:
        """End a chat session."""
        try:
            session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
            if session:
                session.is_active = False
                session.ended_at = db.func.now()
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to end session: {str(e)}")
    
    @staticmethod
    def get_latest_active_session(user_id: int) -> Optional[ChatSession]:
        """Get the latest active session for a user."""
        try:
            return (ChatSession.query
                   .filter_by(user_id=user_id, is_active=True)
                   .order_by(ChatSession.updated_at.desc())
                   .first())
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get latest active session: {str(e)}")
