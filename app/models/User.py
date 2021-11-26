from .base import db


class User(db.Model):
    """User Table."""

    __tablename__ = "user"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    emails = db.relationship("Email", backref="emails")

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"<User {self.name}>"