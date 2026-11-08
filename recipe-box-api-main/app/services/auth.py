
"""Authentication business logic."""

import sqlite3
import jwt

from datetime import datetime, timedelta, timezone

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from ..data.auth import create_user, get_user_by_username, get_user_by_id
from ..main import JWT_SECRET


# -------------------------
# REGISTER SERVICE
# -------------------------

def register_user(username, email, password):
    """Validate registration details and create a user."""

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        return {"status": "invalid"}

    username = username.strip()
    email = email.strip()

    password_hash = generate_password_hash(password)

    try:
        user_id = create_user(
            username,
            email,
            password_hash,
        )

    except sqlite3.IntegrityError:
        return {"status": "duplicate"}

    return {
        "status": "created",
        "user": {
            "id": user_id,
            "username": username,
            "email": email,
            "role": "user",
        },
    }


# -------------------------
# LOGIN SERVICE
# -------------------------

def login_user(username, password):
    """Validate credentials and generate a JWT."""

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(password, str)
        or not password
    ):
        return {"status": "invalid_input"}

    username = username.strip()

    user = get_user_by_username(username)

    if user is None:
        return {"status": "invalid_credentials"}

    if not check_password_hash(
        user.password_hash,
        password,
    ):
        return {"status": "invalid_credentials"}

    if not JWT_SECRET:
        return {"status": "missing_secret"}

    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )

    return {
        "status": "ok",
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }

def get_current_user_profile(user_id):
    """Return safe profile information for an authenticated user."""

    user = get_user_by_id(user_id)

    if user is None:
        return {"status": "not_found"}

    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }
