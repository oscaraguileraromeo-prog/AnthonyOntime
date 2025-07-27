self.addEventListener('install', e => {
  e.waitUntil(caches.open('pwa-cache').then(cache => cache.addAll([
    '/',
    '/static/style.css',
    '/static/app.js'
  ])));
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(response => response || fetch(e.request))
  );
});
