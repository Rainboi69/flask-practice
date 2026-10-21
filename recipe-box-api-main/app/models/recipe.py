"""SQLAlchemy model for recipes."""

from app.extensions import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, nullable=True)