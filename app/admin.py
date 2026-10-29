from flask import Blueprint, abort, current_app, g, render_template

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
def index():
    if not g.user or g.user["role"] != "admin":
        abort(403)
    return render_template("admin.html", items=current_app.requests_repo.all())
