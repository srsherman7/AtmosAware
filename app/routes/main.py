from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db, csrf

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        lat=current_user.default_lat,
        lon=current_user.default_lon,
        location_name=current_user.default_location_name,
        dashboard_layout=current_user.dashboard_layout or "",
    )


@main_bp.route("/api/layout", methods=["POST"])
@login_required
@csrf.exempt
def save_layout():
    """Save the user's dashboard panel order and sizes."""
    import json
    data = request.get_json()
    if not data or "order" not in data:
        return {"error": "order is required"}, 400

    # Validate it's a list
    order = data["order"]
    if not isinstance(order, list):
        return {"error": "order must be an array"}, 400

    current_user.dashboard_layout = json.dumps(order)
    db.session.commit()
    return {"success": True}


@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        lat = request.form.get("lat", type=float)
        lon = request.form.get("lon", type=float)
        location_name = request.form.get("location_name", "").strip()
        alerts_enabled = request.form.get("alerts_enabled") == "on"
        temp_unit = request.form.get("temp_unit", "fahrenheit")
        wind_unit = request.form.get("wind_unit", "mph")
        precip_unit = request.form.get("precip_unit", "inch")

        if lat is not None and lon is not None:
            current_user.default_lat = lat
            current_user.default_lon = lon
            current_user.default_location_name = location_name or "Custom Location"
            current_user.alerts_enabled = alerts_enabled
            current_user.temp_unit = temp_unit
            current_user.wind_unit = wind_unit
            current_user.precip_unit = precip_unit
            db.session.commit()
            flash("Settings saved.", "success")

        return redirect(url_for("main.settings"))

    return render_template("settings.html")
