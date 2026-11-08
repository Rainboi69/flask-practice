"""Recipe service functions."""

from ..models.recipe import Recipe


def recipe_to_dict(recipe):
    """Convert a Recipe ORM object into the existing API format."""
    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": bool(recipe.is_public),
        "owner_id": recipe.owner_id,
    }


def list_recipes(viewer_id=None):
    """Retrieve recipes the viewer is allowed to see, ordered by ID.

    viewer_id is None for anonymous callers (public recipes only), or the
    numeric user id from a verified JWT.
    """
    recipes = Recipe.query.order_by(Recipe.id).all()
    return [
        recipe_to_dict(recipe)
        for recipe in recipes
        if recipe.is_public
        or (viewer_id is not None and recipe.owner_id == viewer_id)
    ]

def get_recipe_by_id(recipe_id):
    """Retrieve a single recipe using SQLAlchemy."""
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if recipe is None:
        return None

    return recipe_to_dict(recipe)