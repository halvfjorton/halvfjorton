(function (global) {
  "use strict";

  function hydrateImg(img) {
    if (!img || img.dataset.deferHeroHydrated === "1") return;
    var src = img.getAttribute("data-defer-src");
    if (!src) return;
    var srcset = img.getAttribute("data-defer-srcset");
    img.src = src;
    if (srcset) img.srcset = srcset;
    img.removeAttribute("data-defer-src");
    img.removeAttribute("data-defer-srcset");
    img.dataset.deferHeroHydrated = "1";
  }

  function hydrateAll(root) {
    if (!root) return;
    root.querySelectorAll("img[data-defer-src]").forEach(hydrateImg);
  }

  /**
   * Stagger hydration before each slide rotation, and fill in any remainder on load/idle.
   */
  function scheduleCarousel(carousel, intervalMs, leadMs) {
    if (!carousel) return;
    var deferred = carousel.querySelectorAll("img[data-defer-src]");
    deferred.forEach(function (img, i) {
      var delay = Math.max(0, (i + 1) * intervalMs - leadMs);
      setTimeout(function () {
        hydrateImg(img);
      }, delay);
    });

    function idleHydrate() {
      if (typeof requestIdleCallback === "function") {
        requestIdleCallback(
          function () {
            hydrateAll(carousel);
          },
          { timeout: 5000 }
        );
      } else {
        setTimeout(function () {
          hydrateAll(carousel);
        }, 2000);
      }
    }

    if (document.readyState === "complete") {
      idleHydrate();
    } else {
      window.addEventListener("load", idleHydrate, { once: true });
    }
  }

  global.__deferHeroSlides = {
    hydrateImg: hydrateImg,
    hydrateAll: hydrateAll,
    scheduleCarousel: scheduleCarousel,
  };
})(window);
