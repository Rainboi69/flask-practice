import sqlite3
import jwt

from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from ..main import get_db, JWT_SECRET


auth_bp = Blueprint("auth", __name__)


# -------------------------
# REGISTER
# -------------------------

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "a JSON body is required"
        }), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        return jsonify({
            "error": "username, email, and password are required"
        }), 400

    username = username.strip()
    email = email.strip()

    password_hash = generate_password_hash(password)

    db = get_db()

    try:
        cur = db.execute(
            """
            INSERT INTO users
            (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
            ),
        )

        db.commit()

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "username or email already exists"
        }), 409

    return jsonify({
        "id": cur.lastrowid,
        "username": username,
        "email": email,
        "role": "user",
    }), 201


# -------------------------
# LOGIN
# -------------------------

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "a JSON body is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(password, str)
        or not password
    ):
        return jsonify({
            "error": "username and password are required"
        }), 400

    username = username.strip()

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    if user is None:
        return jsonify({
            "error": "invalid credentials"
        }), 401

    if not check_password_hash(
        user["password_hash"],
        password,
    ):
        return jsonify({
            "error": "invalid credentials"
        }), 401

    if not JWT_SECRET:
        return jsonify({
            "error": "JWT secret is not configured"
        }), 500

    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )

    return jsonify({
        "message": "login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }), 200