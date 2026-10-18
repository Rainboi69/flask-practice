"""Recipe Box API — BE104 course project."""

import os
import sqlite3
import jwt

from datetime import datetime, timedelta, timezone
from functools import wraps

from dotenv import load_dotenv
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------
# CONFIGURATION
# -------------------------

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

bp = Blueprint("main", __name__)


# -------------------------
# DATABASE
# -------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"],
    }


# -------------------------
# AUTHENTICATION HELPER
# -------------------------

def get_authenticated_user():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (
            jsonify({
                "error": "missing or invalid token"
            }),
            401,
        )

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
        )

        return payload, None

    except jwt.ExpiredSignatureError:
        return None, (
            jsonify({
                "error": "token expired, please log in again"
            }),
            401,
        )

    except jwt.PyJWTError:
        return None, (
            jsonify({
                "error": "invalid token"
            }),
            401,
        )


# -------------------------
# AUTHENTICATION DECORATOR
# -------------------------

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, error = get_authenticated_user()

        if error:
            return error

        return f(payload, *args, **kwargs)

    return wrapper


# -------------------------
# HOME
# -------------------------

@bp.get("/")
def hello():
    return jsonify({
        "message": "Recipe Box API",
        "recipes": "/recipes",
    })


