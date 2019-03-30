"""Routes related to recipe data."""

import os
import traceback

from flask import request, current_app, Blueprint, session
import peewee as pw

from recapi import utils
from recapi.models import recipemodel

bp = Blueprint("recipe_data", __name__)


@bp.route("/recipe_data")
def recipe_data():
    """Return all available recipe data."""
    try:
        data = recipemodel.get_all_recipies()
        return utils.success_response(msg="Data loaded", data=data)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load data: {e}")


@bp.route("/preview_data", methods=['POST'])
def preview_data():
    """Generate recipe preview. Convert markdown data to html."""
    try:
        data = utils.recipe2html(request.form.to_dict())
        image_file = request.files.get("image")
        if image_file:
            filename = utils.make_filename(image_file)
            directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
            utils.save_upload_file(image_file, filename, directory)
            data["image"] = "tmp/" + filename
        return utils.success_response(msg="Data converted", data=data)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to convert data: {e}")


@bp.route("/view_recipe")
def view_recipe():
    """Generate view for one recipe. Convert markdown data to html."""
    return get_recipe_from_db(convert=True)


@bp.route("/get_recipe")
def get_recipe():
    """Get data for one recipe."""
    return get_recipe_from_db()


def get_recipe_from_db(convert=False):
    """Get data for one recipe. Convert to html if convert=True."""
    try:
        title = request.args.get("title")
        recipe = recipemodel.get_recipe(title)
        if convert:
            recipe = utils.recipe2html(recipe)
        if not recipe:
            return utils.error_response(f"Could not find recipe '{title}'."), 404
        # Remove password hash from response
        recipe.get("created_by", {}).pop("password")
        return utils.success_response(msg="Data loaded", data=recipe)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to load recipe: {e}"), 400


@bp.route("/add_recipe", methods=['POST'])
@utils.gatekeeper
def add_recpie():
    """Add new recipe to the data base."""
    recipe_id = None
    filename = None
    try:
        data = request.form.to_dict()
        data["user"] = session.get("uid")
        image_file = request.files.get("image")
        recipe_id = recipemodel.add_recipe(data)
        # Get filename and save image
        if image_file:
            filename = utils.make_filename(image_file, id=str(recipe_id))
            utils.save_upload_file(image_file, filename, current_app.config.get("IMAGE_PATH"))
            # Edit row to add image path
            data["image"] = "img/" + filename
            recipemodel.edit_recipe(recipe_id, data)
        return utils.success_response(msg="Recipe saved")

    except pw.IntegrityError:
        return utils.error_response("Recipe title already exists!"), 409

    except Exception as e:
        # Delete recipe data and image
        if recipe_id is not None:
            recipemodel.delete_recipe(recipe_id)
        if filename is not None:
            filepath = os.path.join(current_app.config.get("IMAGE_PATH"), filename)
            utils.remove_file(filepath)
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/edit_recipe", methods=['POST'])
@utils.gatekeeper
def edit_recpie():
    """Edit a recipe that already exists in the data base."""
    try:
        data = request.form.to_dict()
        # data["user"] = session.get("uid") # Make visible who edited last?
        image_file = request.files.get("image")
        recipemodel.edit_recipe(data["id"], data)
        # Save image
        if image_file:
            filename = utils.make_filename(image_file, id=str(data["id"]))
            utils.save_upload_file(image_file, filename, current_app.config.get("IMAGE_PATH"))
            # Edit row to add image path
            data["image"] = "img/" + filename
            recipemodel.edit_recipe(data["id"], data)
        return utils.success_response(msg="Recipe saved")

    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to save data: {e}"), 400


@bp.route("/delete_recipe")
@utils.gatekeeper
def delete_recpie():
    """Remove recipe from data base."""
    try:
        recipe_id = request.args.get("id")
        recipemodel.delete_recipe(recipe_id)
        return utils.success_response(msg="Recipe removed")
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Failed to remove recipe: {e}"), 400
