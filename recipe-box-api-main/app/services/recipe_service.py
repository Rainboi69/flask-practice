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


def list_recipes():
    """Retrieve all recipes as dictionaries, ordered by ID."""
    recipes = Recipe.query.order_by(Recipe.id).all()
    return [recipe_to_dict(recipe) for recipe in recipes]

def get_recipe_by_id(recipe_id):
    """Retrieve a single recipe using SQLAlchemy."""
    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if recipe is None:
        return None

    return recipe_to_dict(recipe)