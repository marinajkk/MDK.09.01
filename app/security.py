import os
import secrets
import time
from datetime import timedelta
from functools import wraps

from flask import abort, g, redirect, request, session, url_for

MAX_FAILS = 5
LOCK_SECONDS = 600


def load_secret_key(instance_path):
    env = os.environ.get("PORTAL_SECRET_KEY")
    if env:
        return env
    os.makedirs(instance_path, exist_ok=True)
    path = os.path.join(instance_path, "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip()


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def check_csrf():
    if request.method != "POST":
        return
    sent = request.form.get("csrf_token", "")
    saved = session.get("csrf")
    if not saved or not secrets.compare_digest(sent.encode("utf-8"), saved.encode("utf-8")):
        abort(400, "Неверный токен формы")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.user:
            return redirect(url_for("auth.login"))
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapper


class LoginLimiter:
    def __init__(self):
        self.fails = {}

    def key(self, login):
        return (request.remote_addr, login.lower())

    def locked(self, login):
        count, since = self.fails.get(self.key(login), (0, 0))
        if count >= MAX_FAILS and time.time() - since < LOCK_SECONDS:
            return True
        if count >= MAX_FAILS:
            self.fails.pop(self.key(login), None)
        return False

    def fail(self, login):
        count, since = self.fails.get(self.key(login), (0, time.time()))
        self.fails[self.key(login)] = (count + 1, since)

    def reset(self, login):
        self.fails.pop(self.key(login), None)


def init_security(app):
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    )
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.limiter = LoginLimiter()

    @app.before_request
    def protect_forms():
        check_csrf()

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        resp.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'"
        return resp
