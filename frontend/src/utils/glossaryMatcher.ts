import type { GlossaryTerm } from "@/types/glossary";

export interface Match {
  start: number;
  end: number;
  termId: number;
}

export interface Matcher {
  findMatches: (text: string) => Match[];
}

const HAS_LETTER = /\p{L}/u;
const DIACRITIC = /\p{Diacritic}/gu;
const REGEX_SPECIALS = /[.*+?^${}()|[\]\\]/g;

// NFD + strip combining marks + lowercase. For Romanian (and other
// scripts whose letters decompose to base + 1 combining mark) this
// preserves character positions 1:1 with the original input — so a
// match index in the normalized string maps directly to the original.
function normalize(s: string): string {
  return s.normalize("NFD").replace(DIACRITIC, "").toLowerCase();
}

function escapeRegex(s: string): string {
  return s.replace(REGEX_SPECIALS, "\\$&");
}

export function buildMatcher(terms: GlossaryTerm[]): Matcher {
  const pairs: { normalized: string; termId: number }[] = [];
  for (const t of terms) {
    const phrases = [t.term, ...t.aliases];
    for (const phrase of phrases) {
      // Skip phrases with no Unicode letters (pure-symbol terms like
      // "<", "≥", "≈" — still browsable in /glossary, just not auto-linked).
      if (!HAS_LETTER.test(phrase)) continue;
      const n = normalize(phrase);
      if (!n) continue;
      pairs.push({ normalized: n, termId: t.id });
    }
  }

  // Longest-first: regex alternation prefers longer alternatives, and
  // map collisions resolve in favor of the first (longest) inserted.
  pairs.sort((a, b) => b.normalized.length - a.normalized.length);

  const phraseToTermId = new Map<string, number>();
  for (const { normalized, termId } of pairs) {
    if (!phraseToTermId.has(normalized)) {
      phraseToTermId.set(normalized, termId);
    }
  }

  if (phraseToTermId.size === 0) {
    return { findMatches: () => [] };
  }

  const alternatives = [...phraseToTermId.keys()].map(escapeRegex).join("|");
  const pattern = new RegExp(
    `(?<![\\p{L}\\p{N}])(?:${alternatives})(?![\\p{L}\\p{N}])`,
    "giu",
  );

  return {
    findMatches(text: string): Match[] {
      if (!text) return [];
      const normalized = normalize(text);
      pattern.lastIndex = 0;
      const matches: Match[] = [];
      let m: RegExpExecArray | null;
      while ((m = pattern.exec(normalized)) !== null) {
        const termId = phraseToTermId.get(m[0]);
        if (termId != null) {
          matches.push({
            start: m.index,
            end: m.index + m[0].length,
            termId,
          });
        }
        // Defensive: never let a zero-length match spin the loop.
        if (m[0].length === 0) pattern.lastIndex++;
      }
      return matches;
    },
  };
}
