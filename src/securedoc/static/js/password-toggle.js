/**
 * Toggle password visibility; swaps eye / eye-off icons (accessibility: aria-label, aria-pressed).
 */
(function () {
  function setIcons(btn, passwordConcealed) {
    var showIcon = btn.querySelector(".pw-toggle__icon--show");
    var hideIcon = btn.querySelector(".pw-toggle__icon--hide");
    if (!showIcon || !hideIcon) return;
    if (passwordConcealed) {
      showIcon.removeAttribute("hidden");
      hideIcon.setAttribute("hidden", "");
    } else {
      hideIcon.removeAttribute("hidden");
      showIcon.setAttribute("hidden", "");
    }
  }

  function init(btn) {
    var id = btn.getAttribute("data-target");
    var input = id ? document.getElementById(id) : null;
    if (!input) return;

    setIcons(btn, input.getAttribute("type") === "password");

    btn.addEventListener("click", function () {
      var concealed = input.getAttribute("type") === "password";
      var reveal = concealed;
      input.setAttribute("type", reveal ? "text" : "password");
      btn.setAttribute("aria-pressed", reveal ? "true" : "false");
      btn.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
      setIcons(btn, !reveal);
    });
  }

  document.querySelectorAll(".js-pw-toggle").forEach(init);
})();
