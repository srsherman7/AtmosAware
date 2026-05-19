// Browser notification system for AtmosAware
class WeatherNotifications {
    constructor() {
        this.permission = Notification.permission;
        this.lastAlertIds = new Set();
        this.checkInterval = null;
    }

    async init() {
        if (!('Notification' in window)) {
            console.warn('Browser does not support notifications');
            return false;
        }

        if (!('serviceWorker' in navigator)) {
            console.warn('Service workers not supported');
            return false;
        }

        // Register service worker
        try {
            await navigator.serviceWorker.register('/static/sw.js');
        } catch (err) {
            console.error('SW registration failed:', err);
        }

        return true;
    }

    async requestPermission() {
        if (this.permission === 'granted') return true;
        if (this.permission === 'denied') return false;

        const result = await Notification.requestPermission();
        this.permission = result;
        return result === 'granted';
    }

    startMonitoring(lat, lon, intervalMs = 60000) {
        // Check immediately
        this.checkForNewAlerts(lat, lon);

        // Then check periodically
        this.checkInterval = setInterval(() => {
            this.checkForNewAlerts(lat, lon);
        }, intervalMs);
    }

    stopMonitoring() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    async checkForNewAlerts(lat, lon) {
        try {
            const resp = await fetch(`/api/weather/alerts?lat=${lat}&lon=${lon}`);
            const data = await resp.json();

            if (!data.alerts || data.alerts.length === 0) return;

            for (const alert of data.alerts) {
                const alertId = `${alert.event}-${alert.onset || alert.headline}`;

                if (!this.lastAlertIds.has(alertId)) {
                    this.lastAlertIds.add(alertId);
                    this.showNotification(alert);
                }
            }

            // Clean up old alert IDs (keep last 50)
            if (this.lastAlertIds.size > 50) {
                const arr = Array.from(this.lastAlertIds);
                this.lastAlertIds = new Set(arr.slice(-50));
            }
        } catch (err) {
            console.error('Alert check failed:', err);
        }
    }

    showNotification(alert) {
        if (this.permission !== 'granted') return;

        const severityEmoji = {
            'Extreme': '\u{1F6A8}',
            'Severe': '\u{26A0}\u{FE0F}',
            'Moderate': '\u{1F4A7}',
            'Minor': '\u{2139}\u{FE0F}'
        };

        const emoji = severityEmoji[alert.severity] || '\u{1F321}\u{FE0F}';
        const title = `${emoji} ${alert.event || 'Weather Alert'}`;
        const body = alert.headline || alert.description || 'New weather alert in your area.';

        if (navigator.serviceWorker && navigator.serviceWorker.controller) {
            navigator.serviceWorker.ready.then(registration => {
                registration.showNotification(title, {
                    body: body.substring(0, 200),
                    icon: '/static/icons/icon-192.png',
                    badge: '/static/icons/icon-192.png',
                    vibrate: [200, 100, 200],
                    tag: `alert-${alert.event}`,
                    renotify: true,
                    data: { url: '/dashboard' }
                });
            });
        } else {
            // Fallback to basic notification
            new Notification(title, {
                body: body.substring(0, 200),
                icon: '/static/icons/icon-192.png'
            });
        }
    }
}

// Export for use in dashboard
window.WeatherNotifications = WeatherNotifications;
