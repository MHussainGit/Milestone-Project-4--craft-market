{% load static %}/*
 * CraftMarket service worker.
 *
 * Strategy:
 *   - Navigations  -> network-first, falling back to a cached offline page.
 *   - Static GETs  -> cache-first (stale-while-revalidate), so repeat
 *                     visits paint instantly and survive flaky networks.
 * Bump CACHE_VERSION to force clients onto a fresh cache after a deploy.
 */
const CACHE_VERSION = "v2";
const CACHE_NAME = "craftmarket-" + CACHE_VERSION;
const OFFLINE_URL = "{% url 'offline' %}";

const PRECACHE = [
  OFFLINE_URL,
  "{% static 'js/nav.js' %}",
  "{% static 'icons/icon-192.png' %}",
  "{% static 'icons/icon-512.png' %}",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith("craftmarket-") && key !== CACHE_NAME)
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;

  // Only handle same-origin GETs; let everything else hit the network.
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) {
    return;
  }

  // Page navigations: network-first with an offline fallback.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Static assets: serve from cache, refresh in the background.
  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && response.status === 200 && response.type === "basic") {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
