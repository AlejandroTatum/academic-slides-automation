// Deck animation layer. Load after the shell script: it wraps show() and reads
// slides, current and PRINT. Print (the PDF) skips it, so no element stays hidden.
"use strict";
(() => {
  if (PRINT) return;
  const ITEMS = ".fx, .kicker, .title, .lead, .compare-criterion, .compare-side, .compare-takeaway, .big-number, "
    + ".stat-cards > li, .icon-row > li, .flow-steps > li, .recap > li, .case-card, .code-note";
  slides.forEach((slide) => {
    [...slide.querySelectorAll(ITEMS)].filter((el) => !el.hasAttribute("data-step")).forEach((el, i) => {
      el.setAttribute("data-anim", "");
      el.style.setProperty("--i", i);
      el.querySelectorAll(".dot, .icon").forEach((child) => child.style.setProperty("--i", i));
    });
  });

  // Count numbers up from zero; keeps the original text (decimal comma) as the final state.
  function countUp(slide) {
    slide.querySelectorAll(".stat-cards .big, .count").forEach((el) => {
      const final = el.dataset.final || (el.dataset.final = el.textContent);
      const match = final.match(/[\d.,]+/);
      if (!match) return;
      const decimals = (match[0].split(",")[1] || "").length;
      const target = parseFloat(match[0].replace(/\./g, "").replace(",", "."));
      const t0 = performance.now(), duration = 1400;
      const step = (t) => {
        const p = Math.min(1, (t - t0) / duration), eased = 1 - Math.pow(1 - p, 3);
        el.textContent = final.replace(match[0], (target * eased).toFixed(decimals).replace(".", ","));
        if (p < 1 && slide.classList.contains("active")) requestAnimationFrame(step);
        else el.textContent = final;
      };
      requestAnimationFrame(step);
    });
  }

  const bar = document.createElement("div");
  bar.id = "progress";
  document.body.appendChild(bar);
  const paint = () => {
    slides.forEach((slide, index) => slide.classList.toggle("back", index < current));
    bar.style.width = ((current + 1) / slides.length * 100) + "%";
  };
  let last = current;
  const baseShow = show;
  show = function (...args) {
    baseShow(...args);
    if (current !== last) countUp(slides[current]);
    last = current;
    paint();
  };
  paint();
  countUp(slides[current]);
})();
