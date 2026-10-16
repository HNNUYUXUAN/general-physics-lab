/* SPDX-License-Identifier: MIT */
/* Consume the animation interruption on this experiment's controls only. */
(() => {
  "use strict";
  const initialise = async () => {
    for (const plot of document.querySelectorAll(".js-plotly-plot")) {
      if (!plot.layout || !plot._transitionData?._frames?.length) continue;
      const patch = {};
      (plot.layout.updatemenus || []).forEach((menu, i) => {
        (menu.buttons || []).forEach((button, j) => {
          if (button.method === "animate") patch[`updatemenus[${i}].buttons[${j}].execute`] = false;
        });
      });
      (plot.layout.sliders || []).forEach((slider, i) => {
        (slider.steps || []).forEach((step, j) => {
          if (step.method === "animate") patch[`sliders[${i}].steps[${j}].execute`] = false;
        });
      });
      if (!Object.keys(patch).length) continue;
      const pending = new Set();
      plot.on("plotly_animationinterrupted", () => {
        for (const token of pending) token.interrupted = true;
      });
      const animate = args => {
        // animate emits interruption synchronously; add the new token afterwards.
        const promise = Plotly.animate(plot, ...args);
        const token = {interrupted: false};
        pending.add(token);
        Promise.resolve(promise).catch(error => {
          if (!(token.interrupted && error === undefined)) throw error;
        }).finally(() => pending.delete(token));
      };
      plot.on("plotly_buttonclicked", event => {
        if (event.button.method === "animate" && event.button.execute === false) animate(event.button.args);
      });
      plot.on("plotly_sliderchange", event => {
        if (event.interaction && event.step.method === "animate" && event.step.execute === false) animate(event.step.args);
      });
      await Plotly.relayout(plot, patch);
      plot.dataset.pagesAnimationControls = "ready";
    }
  };
  if (document.readyState === "complete") initialise();
  else window.addEventListener("load", initialise, {once: true});
})();
