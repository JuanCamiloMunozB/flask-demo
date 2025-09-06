from sqlalchemy import func
from app.core.extensions import db


class ChatSession(db.Model):
    """Chat session model."""
    
    __tablename__ = "chat_sessions"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False, default="Nueva conversación")
    sport = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    messages = db.relationship(
        "ChatMessage",
        backref="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )


class ChatMessage(db.Model):
    """Chat message model."""
    
    __tablename__ = "chat_messages"
    
    id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(
        db.BigInteger,
        db.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    role = db.Column(db.String(16), nullable=False)  # 'user' | 'assistant' | 'system'
    content = db.Column(db.Text, nullable=False)
    meta = db.Column(db.JSON, default=dict, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
