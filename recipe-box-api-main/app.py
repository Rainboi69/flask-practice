"""Recipe Box API — BE104 course project."""

import os
import sqlite3
import jwt

from datetime import datetime, timedelta, timezone
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------
# CONFIGURATION
# -------------------------

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
DATABASE = "recipes.db"

app = Flask(__name__)


# -------------------------
# DATABASE
# -------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


@app.teardown_appcontext
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

@app.get("/")
def hello():
    return jsonify({
        "message": "Recipe Box API",
        "recipes": "/recipes",
    })


# -------------------------
# REGISTER
# -------------------------

@app.post("/register")
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

@app.post("/login")
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


# -------------------------
# GET ALL RECIPES
# -------------------------

@app.get("/recipes")
def get_recipes():
    rows = get_db().execute(
        """
        SELECT *
        FROM recipes
        ORDER BY id
        """
    ).fetchall()

    return jsonify([
        recipe_to_dict(row)
        for row in rows
    ])


# -------------------------
# GET ONE RECIPE
# -------------------------

@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    db = get_db()

    recipe = db.execute(
        """
        SELECT *
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    if recipe is None:
        return jsonify({
            "error": "recipe not found"
        }), 404

    # Public recipes can be viewed by anyone.
    if recipe["is_public"]:
        return jsonify(recipe_to_dict(recipe)), 200

    # Private recipes require authentication.
    payload, error = get_authenticated_user()

    if error:
        return jsonify({
            "error": "you do not have permission to view this recipe"
        }), 403

    is_owner = recipe["owner_id"] == payload["user_id"]
    is_admin = payload.get("role") == "admin"

    if not is_owner and not is_admin:
        return jsonify({
            "error": "you do not have permission to view this recipe"
        }), 403

    return jsonify(recipe_to_dict(recipe)), 200


# -------------------------
# CREATE RECIPE
# -------------------------

@app.post("/recipes")
def create_recipe():
    payload, error = get_authenticated_user()

    if error:
        return error

    data = request.get_json(silent=True)

    if (
        not data
        or not data.get("title")
        or not data.get("ingredients")
    ):
        return jsonify({
            "error": "title and ingredients are required"
        }), 400

    db = get_db()

    try:
        cur = db.execute(
            """
            INSERT INTO recipes
            (
                title,
                ingredients,
                instructions,
                is_public,
                owner_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
                payload["user_id"],
            ),
        )

        db.commit()

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    row = db.execute(
        """
        SELECT *
        FROM recipes
        WHERE id = ?
        """,
        (cur.lastrowid,),
    ).fetchone()

    return jsonify(recipe_to_dict(row)), 201


# -------------------------
# UPDATE RECIPE
# -------------------------

@app.patch("/recipes/<int:recipe_id>")
@token_required
def update_recipe(payload, recipe_id):
    db = get_db()

    recipe = db.execute(
        """
        SELECT *
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    if recipe is None:
        return jsonify({
            "error": "recipe not found"
        }), 404

    # Owner OR admin may edit.
    is_owner = recipe["owner_id"] == payload["user_id"]
    is_admin = payload.get("role") == "admin"

    if not is_owner and not is_admin:
        return jsonify({
            "error": "you do not have permission to edit this recipe"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "a JSON body is required"
        }), 400

    fields = []
    values = []

    for column in (
        "title",
        "ingredients",
        "instructions",
    ):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])

    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(
            1 if data["is_public"] else 0
        )

    if not fields:
        return jsonify({
            "error": "nothing to update"
        }), 400

    values.append(recipe_id)

    try:
        db.execute(
            f"""
            UPDATE recipes
            SET {', '.join(fields)}
            WHERE id = ?
            """,
            values,
        )

        db.commit()

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    row = db.execute(
        """
        SELECT *
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    return jsonify(recipe_to_dict(row)), 200


# -------------------------
# DELETE RECIPE
# -------------------------

@app.delete("/recipes/<int:recipe_id>")
def delete_recipe(recipe_id):
    payload, error = get_authenticated_user()

    if error:
        return error

    db = get_db()

    recipe = db.execute(
        """
        SELECT *
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    if recipe is None:
        return jsonify({
            "error": "recipe not found"
        }), 404

    # Owner OR admin may delete.
    is_owner = recipe["owner_id"] == payload["user_id"]
    is_admin = payload.get("role") == "admin"

    if not is_owner and not is_admin:
        return jsonify({
            "error": "you do not have permission to delete this recipe"
        }), 403

    db.execute(
        """
        DELETE FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    )

    db.commit()

    return "", 204


# -------------------------
# RUN APPLICATION
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)