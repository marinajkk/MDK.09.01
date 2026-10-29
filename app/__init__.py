import os

from flask import Flask, g, render_template, session

from .db import Database
from .security import init_security, load_secret_key
from .models import EventRepository, RequestRepository, ReviewRepository, UserRepository


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "portal.db"),
    )
    if config:
        app.config.update(config)

    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = load_secret_key(app.instance_path)

    app.db = Database(app.config["DATABASE"])
    app.db.init()
    app.users = UserRepository(app.db)
    app.events = EventRepository(app.db)
    app.requests_repo = RequestRepository(app.db)
    app.reviews = ReviewRepository(app.db)

    @app.before_request
    def load_user():
        user_id = session.get("user_id")
        g.user = app.users.by_id(user_id) if user_id else None

    init_security(app)

    from . import auth, main, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    messages = {
        400: "Форма устарела или отправлена неверно. Обновите страницу и повторите.",
        403: "У вас нет прав для просмотра этой страницы.",
        404: "Такой страницы нет.",
        405: "Так открывать эту страницу нельзя.",
    }

    def show_error(err):
        return render_template("error.html", code=err.code, text=messages.get(err.code, err.name)), err.code

    for code in messages:
        app.register_error_handler(code, show_error)
    return app
