from flask import Blueprint, current_app, render_template

from .security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def index():
    return render_template("admin.html", items=current_app.requests_repo.all())
