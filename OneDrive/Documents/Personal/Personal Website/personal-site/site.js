// Small progressive enhancements. The site works without this file.

// Plausible analytics setup (kept here instead of inline so the CSP needs no 'unsafe-inline').
window.plausible = window.plausible || function () { (plausible.q = plausible.q || []).push(arguments); };
plausible.init = plausible.init || function (i) { plausible.o = i || {}; };
plausible.init();

document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    };
    toggle.addEventListener("click", function () { setOpen(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setOpen(false); toggle.focus(); }
    });
  }

  // Print every collapsed list (e.g. presentations) in full
  window.addEventListener("beforeprint", function () {
    document.querySelectorAll("details").forEach(function (d) { d.open = true; });
  });

  // Publication filter
  var filter = document.querySelector(".filter");
  if (!filter) return;
  var groups = document.querySelectorAll(".pub-group");
  var status = document.querySelector(".filter-status");
  var total = document.querySelectorAll(".pub").length;
  filter.hidden = false;
  filter.addEventListener("change", function (e) {
    var type = e.target.value;
    var shown = 0;
    groups.forEach(function (g) {
      var match = type === "all" || g.dataset.type === type;
      g.hidden = !match;
      if (match) {
        shown += g.querySelectorAll(".pub").length;
        if (type !== "all") g.querySelectorAll("details").forEach(function (d) { d.open = true; });
      }
    });
    status.textContent = "Showing " + shown + " of " + total;
  });
});
