/*jslint browser: true */
/*global console */

// Register the service worker that powers offline support and
// installability. Served from the site root so its scope covers every page.

(function () {
    "use strict";

    if (navigator.serviceWorker === undefined) {
        return;
    }

    window.addEventListener("load", function () {
        navigator.serviceWorker.register(
            "/service-worker.js"
        ).catch(function (error) {
            console.error("Service worker registration failed:", error);
        });
    });
}());
