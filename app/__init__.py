import os

from flask import Flask, g, session

from .db import Database
from .security import init_security, load_secret_key
from .models import EventRepository, RequestRepository, UserRepository


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "portal.db"),
    )
    if config:
        app.config.update(config)

    if "SECRET_KEY" not in app.config:
        app.config["SECRET_KEY"] = load_secret_key(app.instance_path)

    app.db = Database(app.config["DATABASE"])
    app.db.init()
    app.users = UserRepository(app.db)
    app.events = EventRepository(app.db)
    app.requests_repo = RequestRepository(app.db)

    @app.before_request
    def load_user():
        user_id = session.get("user_id")
        g.user = app.users.by_id(user_id) if user_id else None

    init_security(app)

    from . import auth, main, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    return app
