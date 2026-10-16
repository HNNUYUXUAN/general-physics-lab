/* SPDX-License-Identifier: MIT */
/* Render the declared plot axis labels with the site's MathJax 2 SVG output. */
(() => {
  "use strict";
  const labels = JSON.parse(document.currentScript.dataset.labels);
  const initialise = async () => {
    for (const label of labels) {
      const plot = document.getElementById(label.plot_id);
      if (!plot?._fullLayout) throw new Error("Mathematical plot is not ready: " + label.plot_id);
      const holder = document.createElement("div");
      holder.style.cssText = "position:absolute;visibility:hidden;font-family:'Times New Roman',SimSun,serif;font-size:" + label.font_size + "px";
      const input = document.createElement("script");
      input.type = "math/tex";
      input.textContent = label.tex;
      holder.appendChild(input);
      const hub = MathJax.Hub;
      const renderer = hub.config.menuSettings.renderer || "CommonHTML";
      let rendered;
      MathJax.Hub.Config({SVG: {useFontCache: false}});
      await new Promise(resolve => MathJax.Ajax.Require("[MathJax]/jax/output/SVG/config.js", resolve));
      await new Promise(resolve => MathJax.Ajax.Require("[MathJax]/jax/output/SVG/jax.js", resolve));
      await new Promise(resolve => hub.Queue(
        () => document.body.appendChild(holder),
        ["setRenderer", hub, "SVG"],
        ["Typeset", hub, holder],
        () => {
          const svg = holder.querySelector("svg");
          if (svg) {
            const box = svg.getBoundingClientRect();
            rendered = {svg: svg.cloneNode(true), width: box.width, height: box.height};
          }
          for (const jax of hub.getAllJax(holder)) jax.Remove();
          holder.remove();
        },
        ["setRenderer", hub, renderer],
        resolve
      ));
      if (!rendered) throw new Error("Plot axis TeX failed: " + label.tex);
      const install = () => {
        const title = plot.querySelector("." + label.axis_class);
        if (!title) throw new Error("Plot axis title is missing: " + label.axis_class);
        title.parentNode.querySelectorAll('[data-pages-tex-axis="' + label.axis_class + '"]').forEach(node => node.remove());
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.dataset.pagesTexAxis = label.axis_class;
        group.setAttribute("aria-label", label.accessible_text);
        group.setAttribute("role", "img");
        const x = Number(title.getAttribute("x"));
        const y = Number(title.getAttribute("y"));
        const svg = rendered.svg.cloneNode(true);
        svg.setAttribute("x", x - rendered.width / 2);
        svg.setAttribute("y", y - rendered.height / 2);
        svg.setAttribute("width", rendered.width);
        svg.setAttribute("height", rendered.height);
        svg.style.overflow = "visible";
        svg.querySelectorAll("text").forEach(node => node.style.fontFamily = '"Times New Roman",SimSun,serif');
        group.setAttribute("transform", title.getAttribute("transform") || "");
        group.appendChild(svg);
        title.style.visibility = "hidden";
        title.parentNode.appendChild(group);
      };
      install();
      plot.on("plotly_afterplot", install);
      plot.dataset.pagesPlotMath = "ready";
    }
  };
  if (document.readyState === "complete") initialise();
  else window.addEventListener("load", initialise, {once: true});
})();
