import os

from flask import Flask, jsonify, redirect, render_template, url_for

from .config import Config
from .extensions import db, login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    if app.config["STORAGE_BACKEND"] == "local":
        os.makedirs(app.config["STORAGE_ROOT"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to manage your files."

    # Import models before creating tables so SQLAlchemy knows every model.
    from .models import User  # noqa: F401

    with app.app_context():
        db.create_all()

    from .auth import auth
    from .files import files

    app.register_blueprint(auth)
    app.register_blueprint(files)

    from .storage import build_storage

    app.extensions["file_storage"] = build_storage(app.config)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "service": "cloud-file-storage"})

    @app.errorhandler(413)
    def request_too_large(_error):
        return render_template(
            "message.html",
            title="File too large",
            message=f"The maximum upload size is {app.config['MAX_UPLOAD_MB']} MB.",
        ), 413

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template(
            "message.html", title="Not found", message="That page does not exist."
        ), 404

    return app
