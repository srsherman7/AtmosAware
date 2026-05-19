import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required

weather_bp = Blueprint("weather", __name__, url_prefix="/api/weather")


@weather_bp.route("/forecast")
@login_required
def forecast():
    """Get forecast from Open-Meteo API."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    # Use user preferences for units
    from flask_login import current_user
    temp_unit = current_user.temp_unit or "fahrenheit"
    wind_unit = current_user.wind_unit or "mph"
    precip_unit = current_user.precip_unit or "inch"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,relative_humidity_2m,dew_point_2m,visibility,uv_index",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "precipitation_unit": precip_unit,
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        data["units"] = {
            "temperature": "\u00b0F" if temp_unit == "fahrenheit" else "\u00b0C",
            "wind": wind_unit,
            "precipitation": precip_unit,
        }
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502


@weather_bp.route("/alerts")
@login_required
def alerts():
    """Get active weather alerts from NWS API."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    # NWS alerts by point
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    headers = {
        "User-Agent": "AtmosAware App (contact@atmosaware.app)",
        "Accept": "application/geo+json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        alerts_list = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            alerts_list.append({
                "event": props.get("event"),
                "headline": props.get("headline"),
                "severity": props.get("severity"),
                "urgency": props.get("urgency"),
                "description": props.get("description"),
                "instruction": props.get("instruction"),
                "expires": props.get("expires"),
                "onset": props.get("onset"),
            })
        return jsonify({"alerts": alerts_list})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502


@weather_bp.route("/radar")
@login_required
def radar():
    """Get RainViewer radar tile timestamps."""
    url = "https://api.rainviewer.com/public/weather-maps.json"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return jsonify({
            "host": data.get("host", "https://tilecache.rainviewer.com"),
            "radar": data.get("radar", {}),
            "satellite": data.get("satellite", {}),
        })
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502


@weather_bp.route("/geocode")
@login_required
def geocode():
    """Geocode a location name or zip code using Open-Meteo Geocoding API."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter is required"}), 400

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": query,
        "count": 5,
        "language": "en",
        "format": "json",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", []):
            results.append({
                "name": r.get("name", ""),
                "admin1": r.get("admin1", ""),  # state/province
                "country": r.get("country", ""),
                "lat": r.get("latitude"),
                "lon": r.get("longitude"),
                "timezone": r.get("timezone", ""),
                "population": r.get("population", 0),
            })
        return jsonify({"results": results})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502


@weather_bp.route("/history")
@login_required
def history():
    """Get historical weather data from Open-Meteo Archive API."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    start_date = request.args.get("start_date")  # YYYY-MM-DD
    end_date = request.args.get("end_date")  # YYYY-MM-DD

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required (YYYY-MM-DD)"}), 400

    from flask_login import current_user
    temp_unit = current_user.temp_unit or "fahrenheit"
    wind_unit = current_user.wind_unit or "mph"
    precip_unit = current_user.precip_unit or "inch"

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "precipitation_unit": precip_unit,
        "timezone": "auto",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        data["units_display"] = {
            "temperature": "\u00b0F" if temp_unit == "fahrenheit" else "\u00b0C",
            "wind": wind_unit,
            "precipitation": precip_unit,
        }
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502
