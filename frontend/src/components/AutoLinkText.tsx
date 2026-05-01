import { useMemo, type ReactNode } from "react";
import { useGlossary } from "@/contexts/GlossaryContext";
import { useGlossaryDrawer } from "@/contexts/GlossaryDrawerContext";
import { buildMatcher } from "@/utils/glossaryMatcher";
import { parseInlineMath } from "@/lib/math";
import type { GlossaryTerm } from "@/types/glossary";

interface AutoLinkTextProps {
  text: string;
  className?: string;
}

export default function AutoLinkText({ text, className }: AutoLinkTextProps) {
  const { terms, isReady } = useGlossary();
  const { openDrawer } = useGlossaryDrawer();

  const matcher = useMemo(() => buildMatcher(terms), [terms]);
  const termById = useMemo(() => {
    const m = new Map<number, GlossaryTerm>();
    for (const t of terms) m.set(t.id, t);
    return m;
  }, [terms]);

  // Per-render dedup: each AutoLinkText invocation gets its own Set,
  // so StrictMode's double-render starts fresh each pass and siblings
  // don't share mutable state.
  const linked = new Set<number>();

  // Split off any inline `$…$` math first so the matcher only ever
  // sees plain prose. Math segments render via KaTeX HTML, identical
  // to what <InlineMath> does internally.
  const parts = parseInlineMath(text);
  const out: ReactNode[] = [];
  let key = 0;
  const enabled = isReady && terms.length > 0;

  for (const part of parts) {
    if (typeof part !== "string") {
      out.push(
        <span
          key={`m${key++}`}
          dangerouslySetInnerHTML={{ __html: part.html }}
          className="katex-inline"
        />,
      );
      continue;
    }

    if (!enabled || !part) {
      out.push(<span key={`p${key++}`}>{part}</span>);
      continue;
    }

    const matches = matcher.findMatches(part);
    if (matches.length === 0) {
      out.push(<span key={`p${key++}`}>{part}</span>);
      continue;
    }

    let cursor = 0;
    for (const m of matches) {
      if (m.start > cursor) {
        out.push(
          <span key={`t${key++}`}>{part.slice(cursor, m.start)}</span>,
        );
      }
      const span = part.slice(m.start, m.end);

      if (linked.has(m.termId)) {
        out.push(<span key={`l${key++}`}>{span}</span>);
      } else {
        const term = termById.get(m.termId);
        const tooltip = term ? term.definition.slice(0, 140) : undefined;
        const termId = m.termId;
        out.push(
          <button
            key={`b${key++}`}
            type="button"
            onClick={() => openDrawer(termId)}
            title={tooltip}
            className="text-blue-600 cursor-pointer hover:underline underline-offset-2"
          >
            {span}
          </button>,
        );
        linked.add(termId);
      }
      cursor = m.end;
    }
    if (cursor < part.length) {
      out.push(<span key={`t${key++}`}>{part.slice(cursor)}</span>);
    }
  }

  return <span className={className}>{out}</span>;
}
