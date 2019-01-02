import os
from flask import Flask
from flask_session import Session
from flask_cors import CORS
# from flask_restful import Api

# api = Api()


def create_app():
    """https://github.com/pallets/flask/blob/master/examples/tutorial/flaskr/__init__.py"""
    app = Flask(__name__)
    # api.init_app(app)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Read config
    if os.path.exists(os.path.join(os.path.dirname(app.config.root_path), 'config.py')) is False:
        print("Config file 'config.py' is missing! Cannot run application.")
        exit()

    app.config.from_object('config.Config')

    # Init session
    Session(app)

    # Example:
    # from yourapplication.model import db
    # db.init_app(app)
    #
    # from yourapplication.views.admin import admin
    # app.register_blueprint(admin)

    from . import views
    app.register_blueprint(views.general)

    return app