from flask import Flask

from web.routes import base_bp


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.register_blueprint(base_bp)
    return app
