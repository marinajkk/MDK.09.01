from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from .security import login_required
from .validators import RequestForm, clean

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", events=current_app.events.all())


@bp.route("/events/<int:event_id>")
def event(event_id):
    item = current_app.events.get(event_id)
    if not item:
        abort(404)
    return render_template("event.html", event=item)


@bp.route("/requests")
@login_required
def my_requests():
    items = current_app.requests_repo.by_user(g.user["id"])
    return render_template("my_requests.html", items=items)


@bp.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    app = current_app
    form = RequestForm(request.form, app.events)
    if request.method == "POST" and form.ok:
        app.requests_repo.create(
            g.user["id"],
            int(request.form["event_id"]),
            clean(request.form["room"], 50),
            clean(request.form["payment"], 30),
            int(request.form["seats"]),
        )
        flash("Заявка отправлена")
        return redirect(url_for("main.my_requests"))
    errors = form.errors if request.method == "POST" else {}
    selected = request.values.get("event_id", "")
    return render_template("new_request.html", events=app.events.all(), errors=errors, values=request.form, selected=selected)
