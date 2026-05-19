# AtmosAware

A live weather dashboard with real-time Doppler radar, forecasts, severe weather alerts, and browser push notifications. Built with Flask and Leaflet.js.

> **Note:** This project is actively under development. See [Future Plans](#future-plans) below.

## Features

- **Live Doppler Radar** — Animated radar overlay with playback controls (past + nowcast)
- **Current Conditions** — Temperature, feels like, humidity, wind, precipitation
- **7-Day Forecast** — Daily high/low bar chart
- **Hourly Forecast** — Multi-metric chart (temperature, feels like, wind, precip chance, humidity, UV index)
- **Historical Weather** — Look up past weather data with configurable date ranges
- **NWS Weather Alerts** — Real-time severe weather alerts with severity color coding
- **Browser Push Notifications** — Native OS notifications for new weather alerts
- **Draggable & Resizable Dashboard** — Rearrange and resize panels, layout persists per user
- **Location Search** — Find your location by zip code, city name, or browser geolocation
- **Multiple Saved Locations** — Save and switch between locations on the dashboard
- **Unit Preferences** — Toggle between °F/°C, mph/km/h/m/s/knots, inches/mm
- **User Accounts** — Registration, login, and per-user settings stored in SQLite
- **PWA Support** — Installable as a standalone app on mobile and desktop

## API Sources

| API | Purpose | Auth Required |
|-----|---------|---------------|
| [Open-Meteo](https://open-meteo.com/) | Forecast, hourly, and historical weather data | No |
| [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) | Location search (zip code, city name) | No |
| [NWS api.weather.gov](https://www.weather.gov/documentation/services-web-api) | Official US weather alerts (CAP format) | No |
| [RainViewer](https://www.rainviewer.com/api.html) | Doppler radar tile imagery (global) | No |
| [OpenStreetMap](https://www.openstreetmap.org/) | Base map tiles | No |

All APIs are free and require no API keys.

## Tech Stack

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF
- **Database:** SQLite
- **Frontend:** HTML/CSS/JS, Leaflet.js (maps), Chart.js (charts)
- **Notifications:** Service Worker + Web Notifications API
- **PWA:** Web App Manifest + Service Worker caching

## Setup

```bash
# Clone the repo
git clone <repo-url>
cd AtmosAware

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

Open http://localhost:5000, register an account, set your location in Settings, and the dashboard will populate with live data.

## Project Structure

```
AtmosAware/
├── run.py                    # Entry point
├── config.py                 # App configuration
├── requirements.txt          # Python dependencies
├── .env                      # Secret key (change before production)
└── app/
    ├── __init__.py           # Flask app factory
    ├── models.py             # User + SavedLocation models
    ├── forms.py              # Login & registration forms
    ├── routes/
    │   ├── auth.py           # Login/register/logout
    │   ├── main.py           # Dashboard, settings, layout API
    │   ├── weather.py        # Forecast, alerts, radar, history, geocode
    │   └── locations.py      # Saved locations CRUD API
    ├── static/
    │   ├── manifest.json     # PWA manifest
    │   ├── sw.js             # Service worker
    │   ├── js/notifications.js
    │   └── icons/
    └── templates/
        ├── base.html         # Layout with navbar
        ├── dashboard.html    # Main weather dashboard
        ├── settings.html     # Location, units, notifications
        └── auth/
            ├── login.html
            └── register.html
```
## Screen Shots
<img width="1759" height="891" alt="image" src="https://github.com/user-attachments/assets/7f86cc2d-82ce-4196-bd72-6690661f9bbe" />
<img width="1127" height="789" alt="image" src="https://github.com/user-attachments/assets/22036ab1-53a0-412c-8e05-d8fca8f10290" />
<img width="622" height="852" alt="image" src="https://github.com/user-attachments/assets/9fb8d804-1a01-4557-9ad5-dc6212657709" />



## Future Plans

This project is still being actively developed. Planned features include:

- **Enhanced Alerting System** — Custom alerts/alarms where users can define conditions (e.g. "notify me if wind exceeds 40mph" or "alert when temperature drops below freezing")
- **Alert Delivery Options** — Notifications not only in-browser but also via email and SMS
- **My Alerts Dashboard** — Dedicated area to manage, create, and review custom alert rules and their history
- **Mobile-Responsive UI** — Improved layout and touch interactions for phones and tablets
- **Expanded Multi-Location Support** — Track multiple areas simultaneously with side-by-side comparison views
- **Additional Weather Layers** — Satellite imagery, wind maps, temperature heatmaps

## License

This project is licensed under the [MIT License](LICENSE). Weather data is provided by third-party APIs, each governed by their own terms of service — see the LICENSE file for details.
