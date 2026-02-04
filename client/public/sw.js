// Service Worker for CapeControl
// Version: bump this on every deploy for automatic updates
const SW_VERSION = "cc-v0.2.5-2";
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
  
  // Handle different types of requests
  if (url.pathname.startsWith('/assets/')) {
    // Cache-first strategy for hashed assets (they're immutable)
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
  } else if (url.pathname === '/' || url.pathname.endsWith('.html')) {
    // Network-first for HTML files (always check for updates)
    event.respondWith(
      fetch(request).catch(() => {
        // Fallback to cache if network fails (offline support)
        return caches.match(request);
      })
    );
  } else if (url.pathname.startsWith('/api/')) {
    // Network-only for API calls (no caching)
    return;
  } else {
    // Stale-while-revalidate for other static assets
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(request);
        const fetchPromise = fetch(request).then((response) => {
          if (response.ok) {
            cache.put(request, response.clone());
          }
          return response;
        });
        
        return cached || fetchPromise;
      })
    );
  }
});

// Listen for skip waiting messages
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});