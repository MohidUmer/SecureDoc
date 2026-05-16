/**
 * Light / dark theme toggle. Persists choice in localStorage.
 * On load: reads localStorage or prefers-color-scheme. Toggles data-theme on <html>.
 */
(function () {
  var KEY = "securedoc-theme";

  function getPreferred() {
    var stored = localStorage.getItem(KEY);
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(KEY, theme);
  }

  apply(getPreferred());

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".js-theme-toggle");
    if (!btn) return;
    var current = document.documentElement.getAttribute("data-theme") || "dark";
    apply(current === "dark" ? "light" : "dark");
  });
})();
