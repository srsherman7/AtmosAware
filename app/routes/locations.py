from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db, csrf
from app.models import SavedLocation

locations_bp = Blueprint("locations", __name__, url_prefix="/api/locations")


@locations_bp.route("/", methods=["GET"])
@login_required
def get_locations():
    """Get all saved locations for the current user."""
    locations = SavedLocation.query.filter_by(user_id=current_user.id).all()
    return jsonify({"locations": [loc.to_dict() for loc in locations]})


@locations_bp.route("/", methods=["POST"])
@login_required
@csrf.exempt
def add_location():
    """Add a new saved location."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    name = data.get("name", "").strip()
    lat = data.get("lat")
    lon = data.get("lon")
    is_primary = data.get("is_primary", False)

    if not name or lat is None or lon is None:
        return jsonify({"error": "name, lat, and lon are required"}), 400

    # If setting as primary, unset other primaries
    if is_primary:
        SavedLocation.query.filter_by(
            user_id=current_user.id, is_primary=True
        ).update({"is_primary": False})

    location = SavedLocation(
        user_id=current_user.id,
        name=name,
        lat=lat,
        lon=lon,
        is_primary=is_primary,
    )
    db.session.add(location)

    # Also update user default if primary
    if is_primary:
        current_user.default_lat = lat
        current_user.default_lon = lon
        current_user.default_location_name = name

    db.session.commit()
    return jsonify({"location": location.to_dict()}), 201


@locations_bp.route("/<int:location_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_location(location_id):
    """Delete a saved location."""
    location = SavedLocation.query.filter_by(
        id=location_id, user_id=current_user.id
    ).first()

    if not location:
        return jsonify({"error": "Location not found"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"success": True})


@locations_bp.route("/<int:location_id>/primary", methods=["POST"])
@login_required
@csrf.exempt
def set_primary(location_id):
    """Set a location as the primary/default."""
    location = SavedLocation.query.filter_by(
        id=location_id, user_id=current_user.id
    ).first()

    if not location:
        return jsonify({"error": "Location not found"}), 404

    # Unset all other primaries
    SavedLocation.query.filter_by(
        user_id=current_user.id, is_primary=True
    ).update({"is_primary": False})

    location.is_primary = True
    current_user.default_lat = location.lat
    current_user.default_lon = location.lon
    current_user.default_location_name = location.name
    db.session.commit()

    return jsonify({"success": True, "location": location.to_dict()})
