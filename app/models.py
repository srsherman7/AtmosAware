from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # User preferences
    default_lat = db.Column(db.Float, default=39.8283)  # Default: center of US
    default_lon = db.Column(db.Float, default=-98.5795)
    default_location_name = db.Column(db.String(200), default="United States")
    alerts_enabled = db.Column(db.Boolean, default=True)
    temp_unit = db.Column(db.String(10), default="fahrenheit")  # fahrenheit or celsius
    wind_unit = db.Column(db.String(10), default="mph")  # mph or kmh
    precip_unit = db.Column(db.String(10), default="inch")  # inch or mm
    dashboard_layout = db.Column(db.Text, default=None)  # JSON string of panel order

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SavedLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("saved_locations", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "is_primary": self.is_primary,
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
