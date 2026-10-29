from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .validators import RegisterForm

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    app = current_app
    form = RegisterForm(request.form, app.users)
    if request.method == "POST" and form.ok:
        phone = request.form["phone"].replace(" ", "").replace("-", "")
        app.users.create(
            request.form["login"].strip(),
            request.form["full_name"].strip(),
            request.form["password"],
            request.form["email"].strip(),
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
        user = current_app.users.authenticate(request.form.get("login", "").strip(), request.form.get("password", ""))
        if user:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("admin.index") if user["role"] == "admin" else url_for("main.my_requests"))
        error = "Неверный логин или пароль"
    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
