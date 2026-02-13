// Service Worker for CapeControl
// Version: bump this on every deploy for automatic updates
const SW_VERSION = "cc-v0.2.5-3";
const CACHE_NAME = `autorisen-cache-${SW_VERSION}`;

// Assets to cache (adjust based on your needs)
const STATIC_CACHE_URLS = [
  '/favicon.ico',
  '/icons/apple-touch-icon.png',
  '/config.json'  // Always cache the runtime config
];

self.addEventListener('install', (event) => {
  console.log('SW installing, version:', SW_VERSION);
  
  // Skip waiting to activate immediately
  self.skipWaiting();
  
  // Pre-cache essential static assets
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_CACHE_URLS);
    })
  );
});

self.addEventListener('activate', (event) => {
  console.log('SW activating, version:', SW_VERSION);
  
  // Take control of all pages immediately
  event.waitUntil(clients.claim());
  
  // Clean up old caches
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName.startsWith('autorisen-cache-') && cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Only handle GET requests from our origin
  if (request.method !== 'GET' || url.origin !== self.location.origin) {
    return;
  }
  
  // Bypass the service worker for auth, API, and onboarding routes (network-only)
  if (
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/auth/') ||
    url.pathname.startsWith('/onboarding/')
  ) {
    return;
  }

  // Handle different types of requests
  if (
    url.pathname.startsWith('/assets/') ||
    url.pathname.startsWith('/icons/') ||
    STATIC_CACHE_URLS.includes(url.pathname)
  ) {
    // Cache-first strategy for immutable/static assets only
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(request);
        if (cached) {
          return cached;
        }

        const response = await fetch(request);
        if (response.ok) {
          cache.put(request, response.clone());
        }
        return response;
      })
    );
    return;
  }

  // Network-only for all other requests (HTML routes, etc.)
  return;
});

// Listen for skip waiting messages
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});