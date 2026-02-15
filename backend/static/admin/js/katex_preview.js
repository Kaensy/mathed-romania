/**
 * KaTeX live preview for the Django admin.
 *
 * Convention for lesson content:
 *   Inline math:  $expression$
 *   Display math: $$expression$$
 *
 * This script watches the content textarea and renders a live preview
 * below it, converting $...$ and $$...$$ to rendered KaTeX.
 */
(function () {
  "use strict";

  // Load KaTeX CSS and JS from CDN
  function loadKaTeX(callback) {
    // CSS
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href =
      "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css";
    document.head.appendChild(link);

    // JS
    const script = document.createElement("script");
    script.src =
      "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js";
    script.onload = callback;
    document.head.appendChild(script);
  }

  function renderMathInText(text) {
    // Escape HTML first
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Convert newlines to <br> for basic formatting
    html = html.replace(/\n/g, "<br>");

    // Replace $$...$$ (display math) first
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, function (match, expr) {
      try {
        return katex.renderToString(expr.trim(), {
          displayMode: true,
          throwOnError: false,
        });
      } catch (e) {
        return '<span style="color:red;">[Math Error: ' + e.message + "]</span>";
      }
    });

    // Replace $...$ (inline math) — but not already-processed $$
    html = html.replace(/\$([^\$\n]+?)\$/g, function (match, expr) {
      try {
        return katex.renderToString(expr.trim(), {
          displayMode: false,
          throwOnError: false,
        });
      } catch (e) {
        return '<span style="color:red;">[Math Error: ' + e.message + "]</span>";
      }
    });

    return html;
  }

  function setupPreview() {
    // Find the content textarea
    const textarea = document.querySelector("#id_content");
    if (!textarea) return;

    // Create preview container
    const previewWrapper = document.createElement("div");
    previewWrapper.style.marginTop = "10px";

    const toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.textContent = "👁 Previzualizare KaTeX";
    toggleBtn.style.cssText =
      "padding: 6px 14px; background: #417690; color: white; border: none; " +
      "border-radius: 4px; cursor: pointer; font-size: 13px; margin-bottom: 8px;";

    const previewBox = document.createElement("div");
    previewBox.style.cssText =
      "padding: 20px; background: #fafafa; border: 1px solid #ddd; " +
      "border-radius: 4px; min-height: 100px; font-size: 15px; " +
      "line-height: 1.8; display: none; max-height: 500px; overflow-y: auto;";

    previewWrapper.appendChild(toggleBtn);
    previewWrapper.appendChild(previewBox);
    textarea.parentNode.appendChild(previewWrapper);

    let previewVisible = false;

    function updatePreview() {
      if (previewVisible) {
        previewBox.innerHTML = renderMathInText(textarea.value);
      }
    }

    toggleBtn.addEventListener("click", function () {
      previewVisible = !previewVisible;
      previewBox.style.display = previewVisible ? "block" : "none";
      toggleBtn.textContent = previewVisible
        ? "✕ Ascunde previzualizarea"
        : "👁 Previzualizare KaTeX";
      updatePreview();
    });

    // Update on input with debounce
    let timeout;
    textarea.addEventListener("input", function () {
      clearTimeout(timeout);
      timeout = setTimeout(updatePreview, 300);
    });

    // Also add a help text about math syntax
    const helpText = document.createElement("div");
    helpText.style.cssText =
      "margin-top: 6px; font-size: 12px; color: #666;";
    helpText.innerHTML =
      '<strong>Math syntax:</strong> Use <code>$x^2$</code> for inline math, ' +
      "<code>$$\\frac{a}{b}$$</code> for display math.";
    textarea.parentNode.insertBefore(helpText, previewWrapper);
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      loadKaTeX(setupPreview);
    });
  } else {
    loadKaTeX(setupPreview);
  }
})();
