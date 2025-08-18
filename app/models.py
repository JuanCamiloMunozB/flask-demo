from sqlalchemy import func
from flask_login import UserMixin
from .extensions import db, bcrypt

class User(UserMixin, db.Model):
	__tablename__ = 'app_users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	def set_password(self, password: str):
		self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

	def check_password(self, password: str) -> bool:
		return bcrypt.check_password_hash(self.password_hash, password)

	def __repr__(self):
		return f"<User {self.username}>"


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id = db.Column(db.BigInteger, primary_key=True)

    # FIX AQUÍ: apuntar a 'users.id' (tabla plural)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False, default="Nueva conversación")
    sport = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now(), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)

    messages = db.relationship(
        "ChatMessage",
        backref="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(
        db.BigInteger,
        db.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    role = db.Column(db.String(16), nullable=False)   # 'user' | 'assistant' | 'system'
    content = db.Column(db.Text, nullable=False)
    meta = db.Column(db.JSON, default=dict, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)