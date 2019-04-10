"""Offline management of database."""

import os

import peewee as pw
import playhouse.migrate

from recapi.models import DATABASE
import config
# Overwrite with instance config
if os.path.exists(os.path.join("instance", "config.py")):
    import instance.config as config


def init_db():
    """Initialise database."""
    DATABASE.init(
        config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT)
    config.SQLDB = DATABASE


def update_recipes():
    """Update all recipes, e.g. when values of a column are converted."""
    from recapi.models import recipemodel
    recipes = recipemodel.Recipe.select()
    for recipe in recipes:

        # Example: copy int value in 'portions' column to 'portions_text' and convert to str
        recipe.portions_text = str(recipe.portions)
        recipe.save()


def update_users():
    """Example: convert all roles to admin."""
    from recapi.models import usermodel
    users = usermodel.User.select()
    for user in users:
        user.admin = True
        user.save()


if __name__ == '__main__':
    init_db()

    # Check documentation for more info:
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations
    migrator = playhouse.migrate.MySQLMigrator(config.SQLDB)

    # Some examples for altering data
    # from recapi.models import usermodel
    # playhouse.migrate.migrate(
    #     # Add column with or without foreign key
    #     # migrator.add_column("recipe", "changed_by_id", pw.ForeignKeyField(usermodel.User, null=True, field=usermodel.User.id)),
    #     # migrator.add_column("recipe", "changed", pw.DateTimeField(null=True)),
    #
    #     # Drop column
    #     # migrator.drop_column("recipe", "changed_by"),
    # )
    # update_recipes()

    # playhouse.migrate.migrate(
    #     migrator.add_column("user", "admin", pw.BooleanField(default=False)),
    # )
    #
    # update_users()
    #
    # playhouse.migrate.migrate(
    #     migrator.add_column("recipe", "published", pw.BooleanField(default=True)),
    # )