
"""Authentication routes for Recipe Box API."""

from flask import Blueprint, jsonify, request

from ..main import get_authenticated_user

from ..services.auth import (
    register_user,
    login_user,
    get_current_user_profile,
)


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

    result = register_user(
        data.get("username"),
        data.get("email"),
        data.get("password"),
    )

    if result["status"] == "invalid":
        return jsonify({
            "error": "username, email, and password are required"
        }), 400

    if result["status"] == "duplicate":
        return jsonify({
            "error": "username or email already exists"
        }), 409

    return jsonify(result["user"]), 201


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

    result = login_user(
        data.get("username"),
        data.get("password"),
    )

    if result["status"] == "invalid_input":
        return jsonify({
            "error": "username and password are required"
        }), 400

    if result["status"] == "invalid_credentials":
        return jsonify({
            "error": "invalid credentials"
        }), 401

    if result["status"] == "missing_secret":
        return jsonify({
            "error": "JWT secret is not configured"
        }), 500

    return jsonify({
        "message": "login successful",
        "token": result["token"],
        "user": result["user"],
    }), 200


# -------------------------
# CURRENT USER PROFILE
# -------------------------

@auth_bp.get("/auth/me")
def current_user():
    payload, error = get_authenticated_user()

    if error:
        return error

    result = get_current_user_profile(
        payload["user_id"]
    )

    if result["status"] == "not_found":
        return jsonify({
            "error": "user not found"
        }), 404

    return jsonify(result["user"]), 200
