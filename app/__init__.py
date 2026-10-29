import os

from flask import Flask, g, session

from .db import Database
from .models import EventRepository, RequestRepository, UserRepository


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "portal.db"),
    )
    if config:
        app.config.update(config)

    app.db = Database(app.config["DATABASE"])
    app.db.init()
    app.users = UserRepository(app.db)
    app.events = EventRepository(app.db)
    app.requests_repo = RequestRepository(app.db)

    @app.before_request
    def load_user():
        user_id = session.get("user_id")
        g.user = app.users.by_id(user_id) if user_id else None

    from . import auth, main, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    return app
