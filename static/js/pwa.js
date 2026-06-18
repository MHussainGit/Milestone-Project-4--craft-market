// Register the service worker that powers offline support and installability.
// Served from the site root so its scope covers every page.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/service-worker.js").catch(function (error) {
      console.error("Service worker registration failed:", error);
    });
  });
}
