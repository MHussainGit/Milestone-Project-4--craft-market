/*jslint browser: true */

document.addEventListener("DOMContentLoaded", function () {
    "use strict";
    var toggle = document.querySelector(".nav-toggle");
    var links = document.getElementById("primary-nav-links");
    if (!toggle || !links) {
        return;
    }
    toggle.addEventListener("click", function () {
        var isOpen = links.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", (
            isOpen
            ? "true"
            : "false"
        ));
    });
    links.addEventListener("click", function (event) {
        var isTargetLink = event.target.tagName === "A";
        var isMenuOpen = links.classList.contains("is-open");
        if (isTargetLink && isMenuOpen) {
            links.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
        }
    });
});

