// AtmosAware Service Worker
const CACHE_NAME = 'atmosaware-v1';
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// Install - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS).catch(() => {
                // Some assets may not exist yet, that's ok
            });
        })
    );
    self.skipWaiting();
});

// Activate - clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// Push notification received
self.addEventListener('push', event => {
    let data = { title: 'Weather Alert', body: 'New weather alert in your area.' };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-192.png',
        vibrate: [200, 100, 200],
        tag: data.tag || 'weather-alert',
        renotify: true,
        data: {
            url: data.url || '/dashboard'
        },
        actions: [
            { action: 'view', title: 'View Details' },
            { action: 'dismiss', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'dismiss') return;

    const url = event.notification.data.url || '/dashboard';
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            for (const client of windowClients) {
                if (client.url.includes(url) && 'focus' in client) {
                    return client.focus();
                }
            }
            return clients.openWindow(url);
        })
    );
});

// Fetch - network first, fallback to cache
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
