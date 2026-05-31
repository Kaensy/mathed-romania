/**
 * Ciornă component registry.
 *
 * Adding a new draft-paper component (number line, place-value table, …) is a
 * single append to CIORNA_COMPONENTS — no edits inside the picker, container,
 * or canvas. Each entry owns its own render() so the registry stays
 * decoupled from any specific component's props shape.
 *
 * Phase 5 collapses the three operation variants (Adunare / Scădere /
 * Înmulțire) into a single "Operație coloană" entry whose operation is
 * mutable inside the placed card via the cycling operator-sign button. The
 * patterns array still holds three regexes; each match result carries the
 * operation so smart-scan can pre-set the placed card.
 */
import { Calculator, type LucideIcon } from "lucide-react";
import type { ReactElement } from "react";

import ColumnArithmetic from "@/components/lesson/interactive/ColumnArithmetic";
import type { ColumnArithmeticOperation } from "@/types/lesson";

/** A single scan pattern. Returns null when the text doesn't match. */
export interface CiornaScanPattern {
  match: (
    text: string,
  ) => { operands: number[]; operation: ColumnArithmeticOperation } | null;
}

/** Args passed to a registry entry's render() by the canvas. */
export interface CiornaRenderArgs {
  operands?: number[];
  operation?: ColumnArithmeticOperation;
  /** Cycle the card's operation (set by the canvas on column-arithmetic cards). */
  onOperationChange?: (next: ColumnArithmeticOperation) => void;
}

export interface CiornaComponent {
  /** Stable id — used as the placed card's componentId. */
  id: string;
  /** Romanian label shown on the picker card. */
  label: string;
  /** Lucide icon component rendered on the card. */
  icon: LucideIcon;
  /**
   * Renders the component into the ciornă card body. Args are pre-populated
   * for scan-placed cards, omitted for picker-placed cards (the component's
   * own defaults take over).
   */
  render: (args?: CiornaRenderArgs) => ReactElement;
  /** Patterns the scanner tries against contiguous cell-text runs. */
  patterns?: CiornaScanPattern[];
}

/**
 * Build a CiornaScanPattern from a regex whose capture groups are decimal
 * operands and a fixed operation that the match resolves to. Anchored,
 * whitespace-tolerant patterns are the caller's responsibility.
 */
function operationPattern(
  re: RegExp,
  operation: ColumnArithmeticOperation,
): CiornaScanPattern {
  return {
    match: (text) => {
      const m = text.match(re);
      if (!m) return null;
      const operands: number[] = [];
      for (let i = 1; i < m.length; i++) {
        const raw = m[i];
        if (raw === undefined) return null;
        const n = Number(raw);
        if (!Number.isFinite(n)) return null;
        operands.push(n);
      }
      return { operands, operation };
    },
  };
}

const ADDITION_PATTERN = /^\s*(\d+)\s*\+\s*(\d+)\s*$/;
// Accept ASCII hyphen-minus AND the U+2212 minus sign.
const SUBTRACTION_PATTERN = /^\s*(\d+)\s*[-−]\s*(\d+)\s*$/;
// Accept ASCII *, lowercase x, and the U+00D7 multiplication sign.
const MULTIPLICATION_PATTERN = /^\s*(\d+)\s*[*×x]\s*(\d+)\s*$/;

export const CIORNA_COMPONENTS: CiornaComponent[] = [
  {
    id: "column-arithmetic",
    label: "Operație coloană",
    icon: Calculator,
    render: (args) => (
      <ColumnArithmetic
        config={{
          operation: args?.operation ?? "addition",
          operands: args?.operands ?? [],
          mode: "scratch",
        }}
        onOperationChange={args?.onOperationChange}
      />
    ),
    patterns: [
      operationPattern(ADDITION_PATTERN, "addition"),
      operationPattern(SUBTRACTION_PATTERN, "subtraction"),
      operationPattern(MULTIPLICATION_PATTERN, "multiplication"),
    ],
  },
];

export function findComponent(id: string): CiornaComponent | undefined {
  return CIORNA_COMPONENTS.find((c) => c.id === id);
}
