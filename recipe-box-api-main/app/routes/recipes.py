import sqlite3

from flask import Blueprint, jsonify, request

from ..main import (
    get_db,
    recipe_to_dict,
    token_required,
    get_authenticated_user,
)
from ..services.recipe_service import list_recipes, get_recipe_by_id


recipes_bp = Blueprint("recipes", __name__)

def current_user_id(payload):
    """User id from a verified token: 'sub' (users service) or 'user_id' (monolith)."""
    return int(payload.get("sub", payload.get("user_id")))


# -------------------------
# GET ALL RECIPES
# -------------------------

@recipes_bp.get("/recipes")
def get_recipes():
    viewer_id = None

    if request.headers.get("Authorization"):
        payload, error = get_authenticated_user()
        if error:
            return error
        viewer_id = current_user_id(payload)

    return jsonify(list_recipes(viewer_id))


# -------------------------
# GET ONE RECIPE
# -------------------------

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        return jsonify({
            "error": "recipe not found"
        }), 404

    if not recipe["is_public"]:
        payload, error = get_authenticated_user()
        if error:
            return error

        if recipe["owner_id"] != current_user_id(payload):
            return jsonify({
                "error": "you do not have permission to view this recipe"
            }), 403

    return jsonify(recipe), 200


# -------------------------
# CREATE RECIPE
# -------------------------

@recipes_bp.post("/recipes")
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
                current_user_id(payload),
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

@recipes_bp.patch("/recipes/<int:recipe_id>")
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
    is_owner = recipe["owner_id"] == current_user_id(payload)
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

@recipes_bp.delete("/recipes/<int:recipe_id>")
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
    is_owner = recipe["owner_id"] == current_user_id(payload)
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
