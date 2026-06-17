/* CIT rotating hook — slot-machine word roll.
   The visible rotator is decorative (aria-hidden in the markup); the static
   <h1> phrase carries meaning for screen readers. Edit WORDS freely. */

(function () {
  "use strict";

  // The assignment: grow this to 8-12 absurd-but-straight-faced words.
  var WORDS = ["frogs", "Canadians", "pizza-making robots", "cobblers", "anglers", "fletchers", "Wainwrights", "Cartographers", "florists", "Girondins"];

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var rotator = document.querySelector("[data-rotator]");
  if (!rotator || !WORDS.length) return;

  // Build word spans.
  var nodes = WORDS.map(function (w) {
    var el = document.createElement("span");
    el.className = "rotator__word";
    el.textContent = w;
    rotator.appendChild(el);
    return el;
  });

  // Size the slot to the widest word so the box never jumps.
  function measure() {
    var max = 0;
    nodes.forEach(function (el) {
      var prev = el.style.position;
      el.style.position = "static";
      max = Math.max(max, el.offsetWidth);
      el.style.position = prev;
    });
    rotator.style.width = Math.ceil(max) + "px";
  }

  var i = 0;
  nodes[0].classList.add("is-current");

  function tick() {
    var current = nodes[i];
    var next = nodes[(i + 1) % nodes.length];

    // Place the incoming word below before it slides up (skipped under reduced motion via CSS).
    next.classList.remove("is-exit");

    current.classList.remove("is-current");
    current.classList.add("is-exit");

    next.classList.add("is-current");

    i = (i + 1) % nodes.length;
  }

  function start() {
    measure();
    var interval = reduce.matches ? 3500 : 2000;
    var timer = setInterval(tick, interval);
    // Re-measure on resize (font load / viewport change).
    var rm;
    window.addEventListener("resize", function () {
      clearTimeout(rm);
      rm = setTimeout(measure, 150);
    });
    // React if the user toggles the OS reduced-motion setting.
    reduce.addEventListener("change", function () {
      clearInterval(timer);
      timer = setInterval(tick, reduce.matches ? 3500 : 2000);
    });
  }

  // Wait for fonts so the width measurement is correct.
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(start);
  } else {
    window.addEventListener("load", start);
  }
})();
