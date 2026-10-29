from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from .security import admin_required
from .validators import clean, to_int

bp = Blueprint("admin", __name__, url_prefix="/admin")

STATUSES = ["новая", "назначено", "завершено"]


@bp.route("/")
@admin_required
def index():
    app = current_app
    status = request.args.get("status", "")
    event_id = request.args.get("event_id", "")
    search = clean(request.args.get("q", ""), 50)
    items = app.requests_repo.all(
        status if status in STATUSES else None,
        to_int(event_id),
        search or None,
    )
    return render_template("admin.html", items=items, events=app.events.all(), statuses=STATUSES,
                           status=status, event_id=event_id, search=search)


@bp.route("/requests/<int:request_id>/next", methods=["POST"])
@admin_required
def next_status(request_id):
    repo = current_app.requests_repo
    item = repo.get(request_id)
    if not item:
        abort(404)
    new = repo.FLOW.get(item["status"])
    if not new:
        abort(400)
    repo.set_status(request_id, new)
    flash("Заявка № %d: статус «%s»" % (request_id, new))
    return redirect(url_for("admin.index"))


@bp.route("/requests/<int:request_id>/delete", methods=["POST"])
@admin_required
def delete(request_id):
    if not current_app.requests_repo.get(request_id):
        abort(404)
    current_app.requests_repo.delete(request_id)
    flash("Заявка № %d удалена" % request_id)
    return redirect(url_for("admin.index"))
