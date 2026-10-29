from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .security import login_required
from .validators import RegisterForm, clean

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    app = current_app
    form = RegisterForm(request.form, app.users)
    if request.method == "POST" and form.ok:
        phone = clean(request.form["phone"]).replace(" ", "").replace("-", "")
        app.users.create(
            clean(request.form["login"]),
            clean(request.form["full_name"], 100),
            request.form["password"],
            clean(request.form["email"], 100),
            phone,
        )
        flash("Регистрация прошла успешно, теперь войдите")
        return redirect(url_for("auth.login"))
    errors = form.errors if request.method == "POST" else {}
    return render_template("register.html", errors=errors, values=request.form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        name = request.form.get("login", "").strip()[:20]
        limiter = current_app.limiter
        if limiter.locked(name):
            return render_template("login.html", error="Слишком много попыток входа, повторите через 10 минут"), 429
        user = current_app.users.authenticate(name, request.form.get("password", ""))
        if user:
            limiter.reset(name)
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            return redirect(url_for("admin.index") if user["role"] == "admin" else url_for("main.my_requests"))
        limiter.fail(name)
        error = "Неверный логин или пароль"
    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.index"))
