import katex from "katex";

/**
 * Renders a string containing inline $...$ math markers.
 * Returns an array of alternating text nodes and KaTeX spans.
 */
export function parseInlineMath(text: string): (string | { key: number; html: string })[] {
  const parts = text.split(/\$([^$]+)\$/);
  return parts.map((part, index) => {
    if (index % 2 === 0) {
      // Plain text segment
      return part;
    }
    // Math segment — render with KaTeX
    try {
      return {
        key: index,
        html: katex.renderToString(part, { throwOnError: false, displayMode: false, output: "html" }),
      };
    } catch {
      return `$${part}$`;
    }
  });
}

/**
 * Renders text with inline $...$ math support.
 * Use this wherever block `text` fields are rendered.
 */
export function InlineMath({ text, className }: { text: string; className?: string }) {
  const parts = parseInlineMath(text);

  return (
    <span className={className}>
      {parts.map((part, _i) => {
        if (typeof part === "string") {
          return part;
        }
        return (
          <span
            key={part.key}
            dangerouslySetInnerHTML={{ __html: part.html }}
            className="katex-inline"
          />
        );
      })}
    </span>
  );
}

/**
 * Renders a standalone block (display) equation using KaTeX.
 */
export function BlockMath({ latex, className }: { latex: string; className?: string }) {
  try {
      const html = katex.renderToString(latex, {
          throwOnError: false,
          displayMode: true,
          output: "html",
      });
    return (
      <div
        dangerouslySetInnerHTML={{ __html: html }}
        className={className}
      />
    );
  } catch {
    return (
      <div className="text-red-500 font-mono text-sm p-2 bg-red-50 rounded">
        Error rendering: {latex}
      </div>
    );
  }
}
