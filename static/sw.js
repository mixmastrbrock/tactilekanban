/*
 * Service worker for the Task Printer PWA.
 *
 * This script caches the core application shell so that the app can load even
 * when the device is offline.  It uses an offline‑first strategy for static
 * resources and falls back to the network for API requests.
 */

const CACHE_NAME = 'task-printer-v1';
const OFFLINE_URLS = [
  '/',
  '/static/manifest.json',
  '/static/sw.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  // Do not cache POST requests
  if (request.method !== 'GET') {
    return;
  }
  event.respondWith(
    caches.match(request).then(cachedResponse => {
      return cachedResponse || fetch(request).then(networkResponse => {
        // Cache the new resource for next time
        return caches.open(CACHE_NAME).then(cache => {
          cache.put(request, networkResponse.clone());
          return networkResponse;
        });
      }).catch(() => {
        // Fallback: if offline and resource not cached, respond with the root page
        return caches.match('/');
      });
    })
  );
});