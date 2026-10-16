(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var avatars = document.querySelectorAll(".om-oss-members-section .member-compact-card__avatar");
  if (!avatars.length) return;

  avatars.forEach(function (avatar) {
    avatar.setAttribute("role", "button");
    avatar.setAttribute("tabindex", "0");
    avatar.style.cursor = "pointer";

    function spin() {
      if (avatar.classList.contains("is-spinning")) return;
      avatar.classList.remove("is-spinning");
      void avatar.offsetWidth;
      avatar.classList.add("is-spinning");
    }

    avatar.addEventListener("animationend", function () {
      avatar.classList.remove("is-spinning");
    });

    avatar.addEventListener("click", spin);
    avatar.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        spin();
      }
    });
  });
})();
