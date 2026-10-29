from flask import Blueprint, current_app, render_template, request

from .security import admin_required
from .validators import clean

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
        int(event_id) if event_id.isdigit() else None,
        search or None,
    )
    return render_template("admin.html", items=items, events=app.events.all(), statuses=STATUSES,
                           status=status, event_id=event_id, search=search)
