from flask import Flask
from dashboard.routes import bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.register_blueprint(bp)
    return app
