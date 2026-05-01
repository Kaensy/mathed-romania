import { useEffect, useMemo, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { useGlossary } from "@/contexts/GlossaryContext";
import { useGlossaryDrawer } from "@/contexts/GlossaryDrawerContext";
import { InlineMath } from "@/lib/math";
import type {
  GlossaryCategory,
  GlossaryTerm,
} from "@/types/glossary";

const CATEGORY_LABEL: Record<GlossaryCategory, string> = {
  definition: "Definiție",
  notation: "Notație",
  property: "Proprietate",
  other: "Altele",
};

const CATEGORY_BADGE: Record<GlossaryCategory, string> = {
  definition: "bg-blue-100 text-blue-700",
  notation: "bg-purple-100 text-purple-700",
  property: "bg-amber-100 text-amber-700",
  other: "bg-gray-100 text-gray-700",
};

const CATEGORY_ORDER: GlossaryCategory[] = [
  "definition",
  "notation",
  "property",
  "other",
];

function normalize(s: string): string {
  return s.toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");
}

function tokenize(text: string): string[] {
  return normalize(text)
    .split(/[^\p{L}\d]+/u)
    .filter(Boolean);
}

function fieldMatches(field: string, normalizedQuery: string): boolean {
  if (!normalizedQuery) return false;
  return tokenize(field).some((tok) => tok.startsWith(normalizedQuery));
}

export default function GlossaryDrawer() {
  const { isOpen, focusedTermId, closeDrawer } = useGlossaryDrawer();
  const { terms } = useGlossary();

  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<
    Set<GlossaryCategory>
  >(new Set());
  const [highlightedId, setHighlightedId] = useState<number | null>(null);

  const cardRefs = useRef<Map<number, HTMLLIElement>>(new Map());

  // Esc to close.
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeDrawer();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, closeDrawer]);

  // Debounce search ~150ms.
  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query), 150);
    return () => clearTimeout(id);
  }, [query]);

  // When opened with focusedTermId, clear filters so the card is visible,
  // then scroll to it and apply a brief highlight.
  useEffect(() => {
    if (!isOpen || focusedTermId == null) return;
    setQuery("");
    setDebouncedQuery("");
    setSelectedCategories(new Set());
    setHighlightedId(focusedTermId);

    const raf = requestAnimationFrame(() => {
      const el = cardRefs.current.get(focusedTermId);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    const t = setTimeout(() => setHighlightedId(null), 2000);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(t);
    };
  }, [isOpen, focusedTermId]);

  const filtered = useMemo<GlossaryTerm[]>(() => {
    const passesChips = (t: GlossaryTerm) => {
      if (
        selectedCategories.size > 0 &&
        !selectedCategories.has(t.category)
      ) {
        return false;
      }
      return true;
    };

    const q = normalize(debouncedQuery.trim());

    if (!q) {
      return terms
        .filter(passesChips)
        .slice()
        .sort((a, b) => a.term.localeCompare(b.term, "ro"));
    }

    const scored: { term: GlossaryTerm; score: number }[] = [];
    for (const t of terms) {
      if (!passesChips(t)) continue;
      let score = 0;
      if (fieldMatches(t.term, q)) score = 3;
      else if (t.aliases.some((a) => fieldMatches(a, q))) score = 2;
      else if (fieldMatches(t.definition, q)) score = 1;
      if (score > 0) scored.push({ term: t, score });
    }

    scored.sort(
      (a, b) =>
        b.score - a.score || a.term.term.localeCompare(b.term.term, "ro"),
    );

    return scored.map((x) => x.term);
  }, [terms, debouncedQuery, selectedCategories]);

  const toggleCategory = (cat: GlossaryCategory) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  if (!isOpen) return null;

  return (
    <aside
      role="dialog"
      aria-label="Glosar"
      className="fixed right-0 top-0 z-40 flex h-full w-full max-w-[440px] flex-col border-l border-gray-200 bg-white shadow-2xl"
    >
      <header className="flex items-center justify-between border-b px-4 py-3">
        <h2 className="text-base font-bold text-indigo-900">Glosar</h2>
        <button
          type="button"
          onClick={closeDrawer}
          className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-800"
          aria-label="Închide glosarul"
        >
          <X className="h-4 w-4" />
        </button>
      </header>

      <div className="space-y-3 border-b bg-white px-4 py-3">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Caută termen, alias sau cuvânt din definiție…"
            className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm
              focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
            Categorie
          </span>
          <Chip
            active={selectedCategories.size === 0}
            onClick={() => setSelectedCategories(new Set())}
          >
            Toate
          </Chip>
          {CATEGORY_ORDER.map((cat) => (
            <Chip
              key={cat}
              active={selectedCategories.has(cat)}
              onClick={() => toggleCategory(cat)}
            >
              {CATEGORY_LABEL[cat]}
            </Chip>
          ))}
        </div>

        <p className="text-xs text-gray-500">
          {filtered.length} {filtered.length === 1 ? "termen" : "termeni"}
        </p>
      </div>

      <main className="flex-1 overflow-y-auto px-4 py-3">
        {filtered.length === 0 ? (
          <div className="rounded-lg border bg-gray-50 p-6 text-center text-sm text-gray-500">
            Nu am găsit niciun termen.
          </div>
        ) : (
          <ul className="space-y-3">
            {filtered.map((t) => (
              <li
                key={t.id}
                ref={(el) => {
                  if (el) cardRefs.current.set(t.id, el);
                  else cardRefs.current.delete(t.id);
                }}
                className={
                  "rounded-xl border bg-white p-4 transition-colors duration-500 " +
                  (highlightedId === t.id
                    ? "border-amber-400 bg-amber-50"
                    : "")
                }
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h3 className="text-base font-bold text-gray-900">
                    <InlineMath text={t.term} />
                  </h3>
                  <span
                    className={
                      "rounded-full px-2 py-0.5 text-xs font-medium " +
                      CATEGORY_BADGE[t.category]
                    }
                  >
                    {CATEGORY_LABEL[t.category]}
                  </span>
                </div>

                <p className="mt-2 text-sm leading-relaxed text-gray-700">
                  <InlineMath text={t.definition} />
                </p>

                {t.examples.length > 0 && (
                  <div className="mt-3 ml-3 space-y-1 border-l-2 border-gray-200 pl-3">
                    {t.examples.map((ex, i) => (
                      <p key={i} className="text-sm text-gray-600">
                        <InlineMath text={ex} />
                      </p>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </main>
    </aside>
  );
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
        (active
          ? "border-indigo-500 bg-indigo-500 text-white"
          : "border-gray-300 bg-white text-gray-600 hover:border-indigo-300 hover:text-indigo-600")
      }
    >
      {children}
    </button>
  );
}
