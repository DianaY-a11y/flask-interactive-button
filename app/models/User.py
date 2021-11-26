from .base import db


class User(db.Model):
    """User Table."""

    __tablename__ = "user"

    id = db.Column(db.Integer, unique=True, primary_key=True)

    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(128), unique=True, nullable=False)
    messages = db.relationship('Message', backref="user", lazy=True)

    hashed_password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone, hashed_password):
        self.name = name
        self.phone = phone
        self.hashed_password = hashed_password


    def __repr__(self):
        return f"<User {self.name}>"