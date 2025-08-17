from sqlalchemy import func
from flask_login import UserMixin
from .extensions import db, bcrypt

class User(UserMixin, db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	def set_password(self, password: str):
		self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

	def check_password(self, password: str) -> bool:
		return bcrypt.check_password_hash(self.password_hash, password)

	def __repr__(self):
		return f"<User {self.username}>"
