import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Search } from "lucide-react";
import api from "@/api/client";
import { InlineMath } from "@/lib/math";
import type {
  GlossaryCategory,
  GlossaryTerm,
  GlossaryUnit,
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

function unitChipLabel(unit: GlossaryUnit): string {
  return `${unit.grade_number}.${unit.order} ${unit.title}`;
}

export default function GlossaryPage() {
  const [searchParams] = useSearchParams();
  const isPopup = searchParams.get("popup") === "true";

  const [terms, setTerms] = useState<GlossaryTerm[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedUnits, setSelectedUnits] = useState<Set<number>>(new Set());
  const [selectedCategories, setSelectedCategories] = useState<Set<GlossaryCategory>>(
    new Set(),
  );

  // Fetch once on mount.
  useEffect(() => {
    api
      .get<GlossaryTerm[]>("/content/glossary/")
      .then((res) => setTerms(res.data))
      .catch(() => setError("Nu am putut încărca glosarul. Reîncearcă mai târziu."));
  }, []);

  // Fire glossary-opened ping (badge eval is server-side; idempotent).
  useEffect(() => {
    api.post("/content/glossary/opened/").catch(() => {});
  }, []);

  // Debounce search input ~150ms.
  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query), 150);
    return () => clearTimeout(id);
  }, [query]);

  const units = useMemo<GlossaryUnit[]>(() => {
    if (!terms) return [];
    const seen = new Map<number, GlossaryUnit>();
    for (const t of terms) {
      if (!seen.has(t.unit.id)) seen.set(t.unit.id, t.unit);
    }
    return [...seen.values()].sort(
      (a, b) => a.grade_number - b.grade_number || a.order - b.order,
    );
  }, [terms]);

  const filtered = useMemo<GlossaryTerm[]>(() => {
    if (!terms) return [];

    const passesChips = (t: GlossaryTerm) => {
      if (selectedUnits.size > 0 && !selectedUnits.has(t.unit.id)) return false;
      if (selectedCategories.size > 0 && !selectedCategories.has(t.category)) {
        return false;
      }
      return true;
    };

    const q = normalize(debouncedQuery.trim());

    if (!q) {
      return terms
        .filter(passesChips)
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
  }, [terms, debouncedQuery, selectedUnits, selectedCategories]);

  const toggleUnit = (id: number) => {
    setSelectedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleCategory = (cat: GlossaryCategory) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isPopup ? (
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-2">
            <h1 className="text-sm font-bold text-indigo-900">Glosar</h1>
            {terms && (
              <span className="text-xs text-gray-500">
                {filtered.length}{" "}
                {filtered.length === 1 ? "termen" : "termeni"}
              </span>
            )}
          </div>
        </header>
      ) : (
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
            <Link to="/dashboard" className="text-sm text-gray-500 hover:text-indigo-600">
              ← Dashboard
            </Link>
            <h1 className="text-lg font-bold text-indigo-900">Glosar</h1>
            <span className="w-20" aria-hidden />
          </div>
        </header>
      )}

      <div className="sticky top-0 z-10 border-b bg-white/95 backdrop-blur">
        <div className={`mx-auto max-w-4xl space-y-3 ${isPopup ? "px-3 py-3" : "px-6 py-4"}`}>
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

          {units.length > 1 && (
            <ChipRow label="Unitate">
              <Chip
                active={selectedUnits.size === 0}
                onClick={() => setSelectedUnits(new Set())}
              >
                Toate
              </Chip>
              {units.map((u) => (
                <Chip
                  key={u.id}
                  active={selectedUnits.has(u.id)}
                  onClick={() => toggleUnit(u.id)}
                >
                  {unitChipLabel(u)}
                </Chip>
              ))}
            </ChipRow>
          )}

          <ChipRow label="Categorie">
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
          </ChipRow>

          {!isPopup && terms && (
            <p className="text-xs text-gray-500">
              {filtered.length}{" "}
              {filtered.length === 1 ? "termen" : "termeni"}
            </p>
          )}
        </div>
      </div>

      <main className={`mx-auto max-w-4xl ${isPopup ? "px-3 py-4" : "px-6 py-6"}`}>
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!error && terms === null && <SkeletonList />}

        {!error && terms !== null && filtered.length === 0 && (
          <div className="rounded-lg border bg-white p-8 text-center text-sm text-gray-500">
            Nu am găsit niciun termen care să se potrivească căutării.
          </div>
        )}

        {!error && filtered.length > 0 && (
          <ul className="space-y-3">
            {filtered.map((t) => (
              <TermCard key={t.id} term={t} />
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}

function ChipRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
        {label}
      </span>
      {children}
    </div>
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

function TermCard({ term }: { term: GlossaryTerm }) {
  return (
    <li className="rounded-xl border bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <h3 className="text-lg font-bold text-gray-900">
          <InlineMath text={term.term} />
        </h3>
        <span
          className={
            "rounded-full px-2.5 py-0.5 text-xs font-medium " +
            CATEGORY_BADGE[term.category]
          }
        >
          {CATEGORY_LABEL[term.category]}
        </span>
      </div>

      <p className="mt-2 text-sm leading-relaxed text-gray-700">
        <InlineMath text={term.definition} />
      </p>

      {term.examples.length > 0 && (
        <div className="mt-3 ml-3 border-l-2 border-gray-200 pl-3 space-y-1">
          {term.examples.map((ex, i) => (
            <p key={i} className="text-sm text-gray-600">
              <InlineMath text={ex} />
            </p>
          ))}
        </div>
      )}
    </li>
  );
}

function SkeletonList() {
  return (
    <ul className="space-y-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <li key={i} className="rounded-xl border bg-white p-5 animate-pulse">
          <div className="flex items-center justify-between gap-3">
            <div className="h-5 w-40 rounded bg-gray-200" />
            <div className="h-5 w-20 rounded-full bg-gray-100" />
          </div>
          <div className="mt-3 h-4 w-full rounded bg-gray-100" />
          <div className="mt-2 h-4 w-3/4 rounded bg-gray-100" />
        </li>
      ))}
    </ul>
  );
}
