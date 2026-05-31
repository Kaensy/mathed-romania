/**
 * ColumnArithmetic — traditional vertical column arithmetic on squared-notebook paper.
 *
 * Romanian convention: operation sign sits to the RIGHT of the first (top) operand,
 * a single sign on that row only. Addition is n-ary; subtraction and multiplication
 * are strictly binary.
 *
 * The step model is operation-agnostic. Addition walks carries (above the next
 * column up). Subtraction walks borrows: a "−1" annotation appears in the same
 * band over each lending column, with cascading borrows through zeros producing
 * one "−1" per column in the chain. Multiplication walks one partial product
 * per multiplier digit (within-row carries are transient — they fade between
 * partials), then — if the multiplier has more than one digit — runs an
 * addition-style sum walk over the partial-product stack with its own
 * persistent carry band.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { RotateCcw, Cpu } from "lucide-react";
import type {
  ColumnArithmeticConfig,
  ColumnArithmeticMode,
  ColumnArithmeticOperation,
} from "@/types/lesson";
import DigitCell from "./DigitCell";

const OP_SYMBOL: Record<ColumnArithmeticOperation, string> = {
  addition: "+",
  subtraction: "−",
  multiplication: "×",
};

// Single tuning point for the carry walk. 1.0 = base pacing; 1.3 ≈ 30% slower.
// Every per-step delay and the pre/post-roll below scale by this — bump to taste.
const SPEED_MULTIPLIER = 1.3;

// Auto-play kicks in when this fraction of the component is in view.
const VIEW_THRESHOLD = 0.4;

// Per-operation cap on operand size (in digits) when the block is editable.
// Subtraction goes up to 6 to fit lesson 1.5's worked example (262 786 − 93 898);
// multiplication goes up to 4 to fit lesson 1.6's worked example (3249 × 102).
const MAX_OPERAND_DIGITS: Record<ColumnArithmeticOperation, number> = {
  addition: 5,
  subtraction: 6,
  multiplication: 4,
};

// ─── Step model (operation-agnostic) ──────────────────────────────────────────

export type ColumnArithmeticStepKind =
  | "activate"        // highlight a digit column
  | "result"          // reveal a digit in the final result row
  | "carry"           // reveal a carry digit (addition's top band OR multiplication's final-sum band)
  | "borrow"          // reveal a "−1" in the carry band (subtraction)
  | "partial_start"   // begin partial i — clear prev within-row carries, mark multiplier b_i active
  | "partial_digit"   // reveal a digit in a partial product row at (row, column)
  | "partial_carry"   // reveal a within-row carry above multiplicand column (transient)
  | "partial_end";    // end partial walks — clear within-row carries before sum walk

export interface ColumnArithmeticStep {
  kind: ColumnArithmeticStepKind;
  /** LSB-indexed column (0 = units, 1 = tens, …). */
  column: number;
  /** Partial-row index for `partial_*` steps. */
  row?: number;
}

// Delay AFTER each step before the next fires. Calm pacing for grade 5.
const STEP_DELAY_AFTER: Record<ColumnArithmeticStepKind, number> = {
  activate: Math.round(200 * SPEED_MULTIPLIER),
  result: Math.round(300 * SPEED_MULTIPLIER),
  carry: Math.round(250 * SPEED_MULTIPLIER),
  borrow: Math.round(300 * SPEED_MULTIPLIER),
  partial_start: Math.round(350 * SPEED_MULTIPLIER), // brief pause to settle on the new multiplier digit
  partial_digit: Math.round(300 * SPEED_MULTIPLIER),
  partial_carry: Math.round(250 * SPEED_MULTIPLIER),
  partial_end: Math.round(500 * SPEED_MULTIPLIER),   // longer pause so the carry-fade is visible before the sum walk
};
const PRE_ROLL_MS = Math.round(400 * SPEED_MULTIPLIER);
const POST_ROLL_MS = Math.round(250 * SPEED_MULTIPLIER);

// ─── Layout (pure arithmetic) ─────────────────────────────────────────────────

interface AdditionLayout {
  operation: "addition";
  totalColumns: number;
  // All arrays LSB-first (index 0 = units).
  resultDigits: number[];
  carryDigits: (number | null)[];      // carryDigits[0] is always null.
  operandDigits: (number | null)[][];  // [operandIdx][lsbCol]
}

interface SubtractionLayout {
  operation: "subtraction";
  totalColumns: number;
  // LSB-first. When `negative` is true, resultDigits and borrowFlags are empty.
  resultDigits: number[];
  // borrowFlags[k] === true means a "−1" annotation appears over column k
  // (column k lent 1 to column k−1). Length = totalColumns; the entry at
  // column 0 is always false (units can't be lent into from below).
  borrowFlags: boolean[];
  operandDigits: (number | null)[][];
  /** Highest non-zero result column + 1, used to suppress leading zeros. */
  effectiveResultLen: number;
  /** True when minuend < subtrahend — invalid, the operand editor surfaces a note. */
  negative: boolean;
}

interface MultiplicationLayout {
  operation: "multiplication";
  totalColumns: number;
  /** One entry per multiplier digit (LSB-first). */
  partials: {
    /** Sparse map: grid column → partial digit. Includes a leftover-carry digit beyond the multiplicand if there was one. */
    digits: Record<number, number>;
    /** Sparse map: grid column → within-row carry value (the carry INTO this multiplicand column from the previous one). */
    carries: Record<number, number>;
  }[];
  /** When the multiplier has 1 digit, partials[0] IS the result — no separate sum walk. */
  isSingleDigit: boolean;
  /** Column-sum carries from the final addition over the partial stack (multi-digit only). */
  finalCarries: (number | null)[];
  /** LSB-first digits of the actual product. */
  finalResultDigits: number[];
  effectiveResultLen: number;
  operandDigits: (number | null)[][];
}

type ColumnArithmeticLayout = AdditionLayout | SubtractionLayout | MultiplicationLayout;

function digitAt(n: number, pos: number): number | null {
  if (n < 0) return digitAt(-n, pos);
  if (n === 0) return pos === 0 ? 0 : null;
  const m = Math.floor(n / Math.pow(10, pos));
  if (m === 0) return null;
  return m % 10;
}

function lenOf(n: number): number {
  return n === 0 ? 1 : Math.floor(Math.log10(Math.abs(n))) + 1;
}

function computeAddition(operands: number[]): AdditionLayout {
  const sum = operands.reduce((a, b) => a + b, 0);
  const totalColumns = Math.max(lenOf(sum), ...operands.map(lenOf));

  const resultDigits: number[] = [];
  const carryDigits: (number | null)[] = [];
  let carry = 0;
  for (let p = 0; p < totalColumns; p++) {
    carryDigits.push(carry > 0 ? carry : null);
    const colSum = operands.reduce((acc, n) => acc + (digitAt(n, p) ?? 0), 0) + carry;
    resultDigits.push(colSum % 10);
    carry = Math.floor(colSum / 10);
  }

  const operandDigits = operands.map((n) => {
    const row: (number | null)[] = [];
    for (let p = 0; p < totalColumns; p++) row.push(digitAt(n, p));
    return row;
  });

  return { operation: "addition", totalColumns, resultDigits, carryDigits, operandDigits };
}

function buildAdditionSteps(layout: AdditionLayout): ColumnArithmeticStep[] {
  const { totalColumns, carryDigits } = layout;
  const steps: ColumnArithmeticStep[] = [];
  for (let p = 0; p < totalColumns; p++) {
    steps.push({ kind: "activate", column: p });
    steps.push({ kind: "result", column: p });
    if (p + 1 < totalColumns && carryDigits[p + 1] !== null) {
      steps.push({ kind: "carry", column: p + 1 });
    }
  }
  return steps;
}

function effectiveLenOf(digits: number[]): number {
  for (let i = digits.length - 1; i >= 0; i--) {
    if (digits[i] !== 0) return i + 1;
  }
  return 1; // all zeros → display a single "0"
}

function computeSubtraction(operands: number[]): SubtractionLayout {
  const minuend = operands[0] ?? 0;
  const subtrahend = operands[1] ?? 0;
  const totalColumns = Math.max(lenOf(minuend), lenOf(subtrahend));
  const operandDigits = operands.map((n) => {
    const row: (number | null)[] = [];
    for (let p = 0; p < totalColumns; p++) row.push(digitAt(n, p));
    return row;
  });

  if (minuend < subtrahend) {
    return {
      operation: "subtraction",
      totalColumns,
      resultDigits: [],
      borrowFlags: new Array(totalColumns).fill(false),
      operandDigits,
      effectiveResultLen: 0,
      negative: true,
    };
  }

  // Standard column-by-column borrow walk. borrow_in tracks the 1 borrowed
  // from this column by the previous (lower) column.
  const resultDigits: number[] = [];
  const borrowFlags: boolean[] = new Array(totalColumns).fill(false);
  let borrowIn = 0;
  for (let p = 0; p < totalColumns; p++) {
    const dM = digitAt(minuend, p) ?? 0;
    const dS = digitAt(subtrahend, p) ?? 0;
    const top = dM - borrowIn;
    if (top >= dS) {
      resultDigits.push(top - dS);
      borrowIn = 0;
    } else {
      resultDigits.push(top + 10 - dS);
      // Column p+1 lent 1 to p — mark "−1" above p+1.
      if (p + 1 < totalColumns) borrowFlags[p + 1] = true;
      borrowIn = 1;
    }
  }

  return {
    operation: "subtraction",
    totalColumns,
    resultDigits,
    borrowFlags,
    operandDigits,
    effectiveResultLen: effectiveLenOf(resultDigits),
    negative: false,
  };
}

function buildSubtractionSteps(layout: SubtractionLayout): ColumnArithmeticStep[] {
  if (layout.negative) return [];
  const { effectiveResultLen, borrowFlags, totalColumns } = layout;
  const steps: ColumnArithmeticStep[] = [];
  // Only walk through the columns the result actually occupies — the leading-
  // zero columns get their "−1" annotation revealed during their predecessor's
  // borrow step, so a trailing activate without a visible result would feel empty.
  for (let p = 0; p < effectiveResultLen; p++) {
    steps.push({ kind: "activate", column: p });
    if (p + 1 < totalColumns && borrowFlags[p + 1]) {
      steps.push({ kind: "borrow", column: p + 1 });
    }
    steps.push({ kind: "result", column: p });
  }
  return steps;
}

function computeMultiplication(operands: number[]): MultiplicationLayout {
  const multiplicand = operands[0] ?? 0;
  const multiplier = operands[1] ?? 0;
  const product = multiplicand * multiplier;
  const kM = lenOf(multiplicand);
  const kS = lenOf(multiplier);
  const totalColumns = Math.max(lenOf(product), kM, kS);

  // Walk each multiplier digit b_i, computing partial_i = multiplicand × b_i
  // digit-by-digit. The partial digits sit shifted LEFT by i in the grid.
  const partials: MultiplicationLayout["partials"] = [];
  for (let i = 0; i < kS; i++) {
    const bi = digitAt(multiplier, i) ?? 0;
    const digits: Record<number, number> = {};
    const carries: Record<number, number> = {};
    let carry = 0;
    for (let p = 0; p < kM; p++) {
      const dM = digitAt(multiplicand, p) ?? 0;
      const prod = dM * bi + carry;
      digits[i + p] = prod % 10;
      const newCarry = Math.floor(prod / 10);
      // The carry goes above the NEXT multiplicand digit — only annotated if
      // there is one. A leftover carry past the last multiplicand digit just
      // becomes the next partial digit (no annotation, no empty placeholder).
      if (newCarry > 0 && p + 1 < kM) carries[p + 1] = newCarry;
      carry = newCarry;
    }
    if (carry > 0) digits[i + kM] = carry;
    partials.push({ digits, carries });
  }

  const isSingleDigit = kS === 1;

  let finalCarries: (number | null)[] = [];
  const finalResultDigits: number[] = [];
  if (isSingleDigit) {
    // The single partial IS the result. Pad with 0s to totalColumns for the
    // animation player to walk uniformly.
    const only = partials[0]!;
    for (let p = 0; p < totalColumns; p++) {
      finalResultDigits.push(only.digits[p] ?? 0);
    }
  } else {
    finalCarries = new Array(totalColumns).fill(null);
    let carry = 0;
    for (let p = 0; p < totalColumns; p++) {
      finalCarries[p] = carry > 0 ? carry : null;
      let colSum = carry;
      for (const partial of partials) colSum += partial.digits[p] ?? 0;
      finalResultDigits.push(colSum % 10);
      carry = Math.floor(colSum / 10);
    }
  }

  const operandDigits = operands.map((n) => {
    const row: (number | null)[] = [];
    for (let p = 0; p < totalColumns; p++) row.push(digitAt(n, p));
    return row;
  });

  return {
    operation: "multiplication",
    totalColumns,
    partials,
    isSingleDigit,
    finalCarries,
    finalResultDigits,
    effectiveResultLen: effectiveLenOf(finalResultDigits),
    operandDigits,
  };
}

function buildMultiplicationSteps(layout: MultiplicationLayout): ColumnArithmeticStep[] {
  const steps: ColumnArithmeticStep[] = [];
  const { partials, isSingleDigit, finalCarries, effectiveResultLen, operandDigits } = layout;
  const multiplicandRow = operandDigits[0] ?? [];
  const kM = multiplicandRow.filter((d) => d !== null).length || 1;

  for (let i = 0; i < partials.length; i++) {
    const partial = partials[i]!;
    steps.push({ kind: "partial_start", column: i, row: i });
    for (let p = 0; p < kM; p++) {
      steps.push({ kind: "activate", column: p });
      // partial_carry reveals the carry INTO column p (produced by p−1's step).
      if (partial.carries[p] !== undefined) {
        steps.push({ kind: "partial_carry", column: p, row: i });
      }
      if (partial.digits[i + p] !== undefined) {
        steps.push({ kind: "partial_digit", column: i + p, row: i });
      }
    }
    // Leftover carry past the multiplicand — drop it directly as the next partial digit.
    if (partial.digits[i + kM] !== undefined) {
      steps.push({ kind: "activate", column: kM });
      steps.push({ kind: "partial_digit", column: i + kM, row: i });
    }
  }

  // Fade within-row carries before the sum walk (or before the final pause for single-digit).
  steps.push({ kind: "partial_end", column: 0 });

  if (!isSingleDigit) {
    // Final sum walk — addition over the partial-product stack.
    for (let p = 0; p < effectiveResultLen; p++) {
      steps.push({ kind: "activate", column: p });
      if (p + 1 < finalCarries.length && finalCarries[p + 1] !== null) {
        steps.push({ kind: "carry", column: p + 1 });
      }
      steps.push({ kind: "result", column: p });
    }
  }
  return steps;
}

// ─── Reduced motion ───────────────────────────────────────────────────────────

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  });
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handler = () => setReduced(mq.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);
  return reduced;
}

// ─── Unsupported placeholder ──────────────────────────────────────────────────

function Unsupported({ message }: { message: string }) {
  return (
    <div className="my-5 border-2 border-dashed border-gray-300 rounded-xl p-6 text-center bg-gray-50">
      <Cpu className="w-8 h-8 text-gray-400 mx-auto mb-2" />
      <p className="text-gray-500 text-sm">{message}</p>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface Props {
  config: Record<string, unknown>;
  /** mode="input" only — fired whenever the assembled result string changes. */
  onResultChange?: (resultStr: string) => void;
  /**
   * mode="scratch" only — when provided, the operator sign becomes a
   * cycling button (Adunare → Scădere → Înmulțire → Adunare). Lessons and
   * exercises pass a fixed operation and omit this prop, so the sign stays
   * a non-interactive span there.
   */
  onOperationChange?: (next: ColumnArithmeticOperation) => void;
}

export default function ColumnArithmetic({
  config,
  onResultChange,
  onOperationChange,
}: Props) {
  const operation = (config.operation ?? "addition") as ColumnArithmeticOperation;
  const mode = (config.mode ?? "display") as ColumnArithmeticMode;
  const editable = Boolean(config.editable);
  const maxDigits = MAX_OPERAND_DIGITS[operation];
  const rawOperands = Array.isArray(config.operands) ? (config.operands as unknown[]) : [];
  const initialOperands = rawOperands
    .map((n) => (typeof n === "number" ? n : Number(n)))
    .filter((n) => Number.isFinite(n) && n >= 0);

  // Operands held in state so editing (Phase 3) and a future input mode just flip
  // flags without restructuring.
  const [operands, setOperands] = useState<number[]>(initialOperands);

  // Scratch mode (ciornă) — empty draft surface. Operands aren't required up-front
  // since the student types them on the spot, so this branch runs BEFORE the
  // arity check that gates display / input. When operands ARE supplied (e.g.,
  // from a smart-scan match like "123 + 456"), they seed the initial state.
  if (mode === "scratch") {
    return (
      <ArithmeticScratchView
        operation={operation}
        initialOperands={initialOperands}
        onOperationChange={onOperationChange}
      />
    );
  }

  // Addition is n-ary; subtraction and multiplication are strictly binary.
  const arityOk =
    operation === "addition" ? operands.length >= 2 : operands.length === 2;
  if (!arityOk) {
    const msg =
      operation === "addition"
        ? "Adunarea în coloană are nevoie de cel puțin doi termeni."
        : "Această operație acceptă exact doi operanzi.";
    return <Unsupported message={msg} />;
  }

  if (mode === "input") {
    return (
      <ArithmeticInputView
        operands={operands}
        operation={operation}
        onResultChange={onResultChange ?? (() => {})}
      />
    );
  }

  return (
    <ArithmeticView
      operands={operands}
      setOperands={setOperands}
      operation={operation}
      editable={editable}
      maxDigits={maxDigits}
    />
  );
}

// ─── Arithmetic view (addition + subtraction) ────────────────────────────────

function ArithmeticView({
  operands,
  setOperands,
  operation,
  editable,
  maxDigits,
}: {
  operands: number[];
  setOperands: React.Dispatch<React.SetStateAction<number[]>>;
  operation: ColumnArithmeticOperation;
  editable: boolean;
  maxDigits: number;
}) {
  const reducedMotion = usePrefersReducedMotion();
  const layout: ColumnArithmeticLayout = useMemo(() => {
    if (operation === "subtraction") return computeSubtraction(operands);
    if (operation === "multiplication") return computeMultiplication(operands);
    return computeAddition(operands);
  }, [operands, operation]);
  const steps = useMemo(() => {
    if (layout.operation === "subtraction") return buildSubtractionSteps(layout);
    if (layout.operation === "multiplication") return buildMultiplicationSteps(layout);
    return buildAdditionSteps(layout);
  }, [layout]);

  const [playCount, setPlayCount] = useState(0);
  const [activeColumn, setActiveColumn] = useState<number | null>(null);
  const [revealedResults, setRevealedResults] = useState<Set<number>>(new Set());
  // Holds revealed carry digits (addition's top band, multiplication's final-sum
  // band) or borrow markers (subtraction). The render dispatches on operation.
  const [revealedAnnotations, setRevealedAnnotations] = useState<Set<number>>(new Set());
  // Multiplication-only: which partial is currently being walked (drives the
  // multiplier-digit highlight), revealed partial digits keyed "row-col",
  // and transient within-row carries (cleared between partials).
  const [activePartialRow, setActivePartialRow] = useState<number | null>(null);
  const [revealedPartialDigits, setRevealedPartialDigits] = useState<Set<string>>(new Set());
  const [revealedPartialCarries, setRevealedPartialCarries] = useState<Set<number>>(new Set());
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Refs to each editable cell, keyed by `${rowIdx}-${msbIdx}`. Used by the
  // chain-typing focus effect below to advance focus on grow and trim.
  const cellRefs = useRef<Map<string, HTMLInputElement>>(new Map());
  // `cell` targets a digit cell by LSB position so the lookup survives gridWidth
  // changes (sum overflow etc.) and still works after a delete-and-close-up.
  // `grow` is the slim end-cursor past units; `prepend` is the editable slot
  // adjacent to the MSB. The effect below resolves each kind to a refKey.
  const [focusIntent, setFocusIntent] = useState<
    | { row: number; kind: "cell"; lsbPos: number }
    | { row: number; kind: "grow" }
    | { row: number; kind: "prepend" }
    | null
  >(null);

  // Operand edits don't need an explicit playCount bump: the animation effect
  // below already lists `steps` / `layout` in its deps, so a useMemo recompute
  // (driven by operands change) re-runs the walk exactly once per edit. Bumping
  // playCount here would queue a second replay on top of that.

  // Direct, position-based entry. Four mutators:
  //   - overtypeOperand: digit typed on a filled cell. Replaces just that digit
  //     at its LSB position (magnitude unchanged); the cursor advances ONE cell
  //     right ALWAYS — even when the same digit was typed (4 over 4 still moves
  //     focus rightward). Value commit is skipped when oldD === newD so the carry
  //     walk doesn't replay for a no-op keystroke; the cursor still moves.
  //   - appendDigit: digit typed at the grow end-cursor. `cur * 10 + d` — new
  //     digit becomes units, existing digits slide one cell left, capped per
  //     operation. Cursor stays at the grow position so further digits chain.
  //   - prependDigit: digit typed at the left prepend slot. `d * 10^k + cur` —
  //     new digit becomes a leading MSB, grid extends leftward, capped per
  //     operation. Leading zero is ignored. Cursor stays at "prepend" so the
  //     slot shifts one further left for the next keystroke.
  //   - deleteDigitAt: Backspace removes the digit at the given LSB position;
  //     digits above slide right to close up. Cursor lands on the next-lower
  //     place (lsbPos - 1) — or the grow position if the deleted digit was the
  //     units. K ≥ 1; grow / prepend Backspace passes lsbPos=0 (trim units).
  // Each value-change mutator commits via setOperands; the carry walk re-runs
  // because the animation effect's deps include `steps` / `layout`. Non-mutations
  // early-out so the walk doesn't replay for a keystroke that produced no actual
  // change.
  const overtypeOperand = (idx: number, lsbPos: number, newD: number) => {
    const cur = operands[idx] ?? 0;
    const oldD = digitAt(cur, lsbPos) ?? 0;
    if (oldD !== newD) {
      const next = cur + (newD - oldD) * Math.pow(10, lsbPos);
      if (next >= 0) {
        setOperands((prev) => prev.map((o, i) => (i === idx ? next : o)));
      }
    }
    // Advance the cursor one cell to the right regardless of whether the value
    // changed; past LSB hands off to the grow cursor.
    if (lsbPos > 0) {
      setFocusIntent({ row: idx, kind: "cell", lsbPos: lsbPos - 1 });
    } else {
      setFocusIntent({ row: idx, kind: "grow" });
    }
  };
  const appendDigit = (idx: number, d: number) => {
    const cur = operands[idx] ?? 0;
    const k = lenOf(cur);
    if (k >= maxDigits) return; // cap reached — grow cursor stops accepting
    const next = cur * 10 + d;
    if (next === cur) return;   // typing 0 onto operand=0 is a no-op
    setOperands((prev) => prev.map((o, i) => (i === idx ? next : o)));
    setFocusIntent({ row: idx, kind: "grow" });
  };
  const prependDigit = (idx: number, d: number) => {
    const cur = operands[idx] ?? 0;
    const k = lenOf(cur);
    if (k >= maxDigits) return; // cap reached — prepend slot stops accepting
    if (d === 0) return;        // leading zero would be a no-op
    const next = d * Math.pow(10, k) + cur;
    setOperands((prev) => prev.map((o, i) => (i === idx ? next : o)));
    setFocusIntent({ row: idx, kind: "prepend" });
  };
  const deleteDigitAt = (idx: number, lsbPos: number) => {
    const cur = operands[idx] ?? 0;
    if (lenOf(cur) <= 1) return; // keep at least one digit
    const pow = Math.pow(10, lsbPos);
    const highPart = Math.floor(cur / (pow * 10));
    const lowPart = cur % pow;
    const next = highPart * pow + lowPart;
    setOperands((prev) => prev.map((o, i) => (i === idx ? next : o)));
    if (lsbPos === 0) {
      setFocusIntent({ row: idx, kind: "grow" });
    } else {
      setFocusIntent({ row: idx, kind: "cell", lsbPos: lsbPos - 1 });
    }
  };

  // One-shot view trigger: fire the first play when the grid is ~40% in view.
  // If already on screen at mount, IntersectionObserver delivers the entry immediately.
  // Reduced-motion path skips this entirely — solved state is shown synchronously below.
  useEffect(() => {
    if (reducedMotion) return;
    const node = containerRef.current;
    if (!node || typeof IntersectionObserver === "undefined") {
      // No observer support → fall back to immediate auto-play so the walk still runs.
      setPlayCount((c) => (c === 0 ? 1 : c));
      return;
    }
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting && entry.intersectionRatio >= VIEW_THRESHOLD) {
            setPlayCount((c) => (c === 0 ? 1 : c));
            obs.disconnect();
            return;
          }
        }
      },
      { threshold: VIEW_THRESHOLD },
    );
    obs.observe(node);
    return () => obs.disconnect();
  }, [reducedMotion]);

  useEffect(() => {
    if (reducedMotion) {
      // Solved state instantly; no motion; replay is inert (re-applies the same state).
      setActiveColumn(null);
      setActivePartialRow(null);
      setRevealedPartialCarries(new Set());
      if (layout.operation === "addition") {
        setRevealedResults(new Set(Array.from({ length: layout.totalColumns }, (_, i) => i)));
        setRevealedAnnotations(
          new Set(
            layout.carryDigits
              .map((c, i) => (c !== null ? i : -1))
              .filter((i) => i >= 0),
          ),
        );
        setRevealedPartialDigits(new Set());
      } else if (layout.operation === "subtraction") {
        setRevealedResults(
          new Set(Array.from({ length: layout.effectiveResultLen }, (_, i) => i)),
        );
        setRevealedAnnotations(
          layout.negative
            ? new Set()
            : new Set(
                layout.borrowFlags
                  .map((b, i) => (b ? i : -1))
                  .filter((i) => i >= 0),
              ),
        );
        setRevealedPartialDigits(new Set());
      } else {
        // Multiplication: all partial digits revealed; final result + final-sum
        // carries revealed only in the multi-digit case. Within-row carries are
        // transient — they're not part of the solved state.
        const partials = new Set<string>();
        layout.partials.forEach((partial, i) => {
          for (const colStr of Object.keys(partial.digits)) {
            partials.add(`${i}-${colStr}`);
          }
        });
        setRevealedPartialDigits(partials);
        if (layout.isSingleDigit) {
          setRevealedResults(new Set());
          setRevealedAnnotations(new Set());
        } else {
          setRevealedResults(
            new Set(Array.from({ length: layout.effectiveResultLen }, (_, i) => i)),
          );
          setRevealedAnnotations(
            new Set(
              layout.finalCarries
                .map((c, i) => (c !== null ? i : -1))
                .filter((i) => i >= 0),
            ),
          );
        }
      }
      return;
    }

    // Hold the initial hidden state until the view trigger (or manual replay) fires.
    if (playCount === 0) return;

    setActiveColumn(null);
    setActivePartialRow(null);
    setRevealedResults(new Set());
    setRevealedAnnotations(new Set());
    setRevealedPartialDigits(new Set());
    setRevealedPartialCarries(new Set());

    let cancelled = false;
    const timers: number[] = [];
    let acc = PRE_ROLL_MS;

    const schedule = (delay: number, fn: () => void) => {
      timers.push(
        window.setTimeout(() => {
          if (!cancelled) fn();
        }, delay),
      );
    };

    for (const step of steps) {
      const captured = step;
      schedule(acc, () => {
        switch (captured.kind) {
          case "activate":
            setActiveColumn(captured.column);
            break;
          case "result":
            setRevealedResults((s) => {
              const n = new Set(s);
              n.add(captured.column);
              return n;
            });
            break;
          case "carry":
          case "borrow":
            setRevealedAnnotations((s) => {
              const n = new Set(s);
              n.add(captured.column);
              return n;
            });
            break;
          case "partial_start":
            setActivePartialRow(captured.row ?? captured.column);
            setRevealedPartialCarries(new Set());
            break;
          case "partial_digit": {
            const key = `${captured.row}-${captured.column}`;
            setRevealedPartialDigits((s) => {
              const n = new Set(s);
              n.add(key);
              return n;
            });
            break;
          }
          case "partial_carry":
            setRevealedPartialCarries((s) => {
              const n = new Set(s);
              n.add(captured.column);
              return n;
            });
            break;
          case "partial_end":
            setActivePartialRow(null);
            setRevealedPartialCarries(new Set());
            break;
        }
      });
      acc += STEP_DELAY_AFTER[step.kind];
    }

    schedule(acc + POST_ROLL_MS, () => setActiveColumn(null));

    return () => {
      cancelled = true;
      timers.forEach((t) => window.clearTimeout(t));
    };
  }, [playCount, reducedMotion, steps, layout]);

  const { totalColumns } = layout;
  // Editable mode reserves room for the per-operation cap so the sign + other operand
  // stay anchored: growing one operand never shifts the other. Non-editable mode
  // collapses to layout.totalColumns. If the sum overflows maxDigits (e.g., 99999+1)
  // the grid still widens to fit it.
  const gridWidth = editable ? Math.max(totalColumns, maxDigits) : totalColumns;
  const lsbAt = (i: number) => gridWidth - 1 - i; // i is MSB-first render index
  const cols = Array.from({ length: gridWidth }, (_, i) => i);
  const sign = OP_SYMBOL[operation];

  // Apply focusIntent after each render. The cell-kind target is resolved against
  // the NEW operand state so deletions / overtype-shrinks land on a real cell.
  // Fallbacks: cell out-of-range → grow; prepend at the cap → grow.
  useEffect(() => {
    if (!focusIntent) return;
    const opVal = operands[focusIntent.row];
    if (opVal === undefined) {
      setFocusIntent(null);
      return;
    }
    let refKey: string;
    if (focusIntent.kind === "cell") {
      const k = lenOf(opVal);
      if (focusIntent.lsbPos >= k) {
        refKey = `${focusIntent.row}-grow`;
      } else {
        const msbIdx = gridWidth - 1 - focusIntent.lsbPos;
        refKey = `${focusIntent.row}-${msbIdx}`;
      }
    } else if (focusIntent.kind === "prepend") {
      refKey = `${focusIntent.row}-prepend`;
      if (!cellRefs.current.has(refKey)) refKey = `${focusIntent.row}-grow`;
    } else {
      refKey = `${focusIntent.row}-grow`;
    }
    const el = cellRefs.current.get(refKey);
    if (el) {
      el.focus();
      el.select();
    }
    setFocusIntent(null);
  }, [focusIntent, operands, gridWidth]);

  return (
    <div className="my-6" ref={containerRef}>
      <div className="overflow-x-auto">
        <div className="inline-block rounded-md border border-blue-200 bg-blue-50/40 shadow-sm font-mono select-none">
          {/* Annotation row — addition: small carry digits; subtraction: small "−1"
              lender marks; multiplication: within-row carries of the ACTIVE partial
              only (transient — they clear between partials). */}
          <div className="flex">
            {cols.map((i) => {
              const p = lsbAt(i);
              const isActive = activeColumn === p;
              if (layout.operation === "addition") {
                return (
                  <DigitCell
                    key={i}
                    size="sm"
                    tone="rose"
                    digit={layout.carryDigits[p]}
                    revealed={revealedAnnotations.has(p)}
                    active={isActive}
                    borderLeft={i !== 0}
                  />
                );
              }
              if (layout.operation === "multiplication") {
                const partial = activePartialRow !== null ? layout.partials[activePartialRow] : null;
                const carryVal = partial ? partial.carries[p] : undefined;
                const revealed =
                  carryVal !== undefined && revealedPartialCarries.has(p);
                return (
                  <DigitCell
                    key={i}
                    size="sm"
                    tone="rose"
                    digit={carryVal ?? null}
                    revealed={revealed}
                    active={isActive}
                    borderLeft={i !== 0}
                  />
                );
              }
              // Subtraction: "−1" is two characters, so render inline in the same band
              // instead of as a single-digit cell.
              const hasBorrow = p < layout.borrowFlags.length && layout.borrowFlags[p];
              const revealed = hasBorrow && revealedAnnotations.has(p);
              return (
                <div
                  key={i}
                  className={
                    "w-8 h-5 flex items-center justify-center text-[0.7rem] text-rose-500 transition-colors duration-200 " +
                    (i === 0 ? "" : "border-l border-blue-200 ") +
                    (isActive ? "bg-blue-200/60" : "")
                  }
                >
                  <span
                    className={
                      "transition-opacity duration-200 " +
                      (revealed ? "opacity-100" : "opacity-0")
                    }
                  >
                    {hasBorrow ? "−1" : ""}
                  </span>
                </div>
              );
            })}
            {editable && <div className="w-3 h-5" aria-hidden />}
            {/* Operator column placeholder in annotation row */}
            <div className="w-8 h-5" aria-hidden />
          </div>

          {/* Operand rows */}
          {operands.map((opVal, rowIdx) => {
            const k = lenOf(opVal);
            const filledFromMsb = gridWidth - k; // MSB-first idx of leftmost filled cell
            // Prepend slot sits at the cell immediately left of MSB when the
            // operand still has room to grow. Only this one empty cell becomes
            // focusable; the rest stay inert (gap-free invariant).
            const prependMsbIdx = editable && k < maxDigits ? filledFromMsb - 1 : -1;
            // In multiplication, the multiplier row's b_i stays highlighted for
            // the duration of partial i — overrides the moving activeColumn.
            const isMultiplierRow = layout.operation === "multiplication" && rowIdx === 1;
            return (
              <div key={rowIdx} className="flex border-t border-blue-200">
                {cols.map((i) => {
                  const p = lsbAt(i);
                  const isActive = isMultiplierRow
                    ? activePartialRow === p
                    : activeColumn === p;
                  const refKey = `${rowIdx}-${i}`;
                  const registerRef = (el: HTMLInputElement | null) => {
                    if (el) cellRefs.current.set(refKey, el);
                    else cellRefs.current.delete(refKey);
                  };
                  if (i >= filledFromMsb) {
                    const d = digitAt(opVal, p);
                    if (editable) {
                      return (
                        <DigitCell
                          key={i}
                          variant="editable"
                          digit={d}
                          borderLeft={i !== 0}
                          active={isActive}
                          onDigit={(newD) => overtypeOperand(rowIdx, p, newD)}
                          onBackspace={() => deleteDigitAt(rowIdx, p)}
                          ariaLabel={`Termen ${rowIdx + 1}, cifra ${k - p}`}
                          inputRef={registerRef}
                        />
                      );
                    }
                    return (
                      <DigitCell
                        key={i}
                        digit={d}
                        active={isActive}
                        borderLeft={i !== 0}
                      />
                    );
                  }
                  if (i === prependMsbIdx) {
                    // Left prepend slot. Indigo accent + "+" placeholder so it
                    // reads as "add a digit here", distinct from the slim grow
                    // caret at the right end of the row.
                    return (
                      <input
                        key={i}
                        ref={(el) => {
                          const key = `${rowIdx}-prepend`;
                          if (el) cellRefs.current.set(key, el);
                          else cellRefs.current.delete(key);
                        }}
                        type="text"
                        inputMode="numeric"
                        autoComplete="off"
                        value=""
                        placeholder="+"
                        aria-label={`Termen ${rowIdx + 1}, adaugă cifră în față`}
                        onFocus={(e) => e.currentTarget.select()}
                        onChange={(e) => {
                          const v = e.target.value;
                          if (v === "") return;
                          const last = v.charAt(v.length - 1);
                          if (last >= "0" && last <= "9") prependDigit(rowIdx, Number(last));
                        }}
                        onKeyDown={(e) => {
                          if (e.key === "Backspace") {
                            e.preventDefault();
                            deleteDigitAt(rowIdx, 0);
                          }
                        }}
                        className={
                          "w-8 h-9 p-0 m-0 text-center font-mono text-lg leading-9 " +
                          "bg-indigo-50/50 text-indigo-700 placeholder:text-indigo-300 " +
                          "transition-colors focus:bg-indigo-100/70 focus:outline-none " +
                          "focus:ring-1 focus:ring-indigo-400 focus:ring-inset caret-indigo-500 " +
                          (i !== 0 ? "border-l border-blue-200" : "")
                        }
                      />
                    );
                  }
                  // Empty inert cell (left padding — not focusable)
                  return (
                    <div
                      key={i}
                      className={"w-8 h-9 " + (i !== 0 ? "border-l border-blue-200" : "")}
                    />
                  );
                })}
                {/* Right-end grow cursor: slim, sits between units and the sign.
                    Typing here calls appendDigit; the value is always rendered empty
                    so the grow position stays a cursor, not a digit slot. */}
                {editable && (
                  <input
                    ref={(el) => {
                      const key = `${rowIdx}-grow`;
                      if (el) cellRefs.current.set(key, el);
                      else cellRefs.current.delete(key);
                    }}
                    type="text"
                    inputMode="numeric"
                    autoComplete="off"
                    value=""
                    aria-label={`Termen ${rowIdx + 1}, adaugă cifră la final`}
                    onFocus={(e) => e.currentTarget.select()}
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === "") return;
                      const last = v.charAt(v.length - 1);
                      if (last >= "0" && last <= "9") appendDigit(rowIdx, Number(last));
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Backspace") {
                        e.preventDefault();
                        deleteDigitAt(rowIdx, 0);
                      }
                    }}
                    className="w-3 h-9 p-0 m-0 bg-transparent text-center font-mono text-lg leading-9 text-gray-900 border-l border-blue-200 transition-colors focus:bg-blue-100/70 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:ring-inset caret-blue-500"
                  />
                )}
                {/* Operator column — sign on the FIRST (top) operand row only */}
                <div className="w-8 h-9 flex items-center justify-center text-lg text-gray-900 border-l border-blue-200">
                  {rowIdx === 0 ? sign : ""}
                </div>
              </div>
            );
          })}

          {/* Top sum line — between operands and result/partials */}
          <div className="border-t-2 border-gray-800" />

          {(layout.operation === "addition" || layout.operation === "subtraction") && (
            /* Result row (addition / subtraction). Subtraction suppresses leading zeros. */
            <div className="flex">
              {cols.map((i) => {
                const p = lsbAt(i);
                const showDigit =
                  layout.operation === "addition" || p < layout.effectiveResultLen;
                return (
                  <DigitCell
                    key={i}
                    emphasis="bold"
                    digit={showDigit ? layout.resultDigits[p] : undefined}
                    revealed={revealedResults.has(p)}
                    active={activeColumn === p}
                    borderLeft={i !== 0}
                  />
                );
              })}
              {editable && <div className="w-3 h-9 border-l border-blue-200" aria-hidden />}
              <div className="w-8 h-9 border-l border-blue-200" />
            </div>
          )}

          {layout.operation === "multiplication" && (
            <>
              {/* Final-sum carry band — only for multi-digit multipliers; rendered
                  here (between top line and partial stack) so the carries sit
                  visually above the addends being summed. */}
              {!layout.isSingleDigit && (
                <div className="flex">
                  {cols.map((i) => {
                    const p = lsbAt(i);
                    return (
                      <DigitCell
                        key={i}
                        size="sm"
                        tone="rose"
                        digit={layout.finalCarries[p]}
                        revealed={revealedAnnotations.has(p)}
                        active={activeColumn === p}
                        borderLeft={i !== 0}
                      />
                    );
                  })}
                  {editable && <div className="w-3 h-5" aria-hidden />}
                  <div className="w-8 h-5" aria-hidden />
                </div>
              )}

              {/* Partial product rows. For single-digit, this single row IS the
                  result — gets bold emphasis so it reads as the answer. */}
              {layout.partials.map((partial, partialIdx) => (
                <div key={partialIdx} className="flex">
                  {cols.map((i) => {
                    const p = lsbAt(i);
                    const d = partial.digits[p];
                    const revealKey = `${partialIdx}-${p}`;
                    return (
                      <DigitCell
                        key={i}
                        digit={d ?? null}
                        revealed={revealedPartialDigits.has(revealKey)}
                        active={activeColumn === p}
                        borderLeft={i !== 0}
                        emphasis={layout.isSingleDigit ? "bold" : "normal"}
                      />
                    );
                  })}
                  {editable && <div className="w-3 h-9 border-l border-blue-200" aria-hidden />}
                  <div className="w-8 h-9 border-l border-blue-200" />
                </div>
              ))}

              {/* Bottom line + final result row — only for multi-digit multipliers. */}
              {!layout.isSingleDigit && (
                <>
                  <div className="border-t-2 border-gray-800" />
                  <div className="flex">
                    {cols.map((i) => {
                      const p = lsbAt(i);
                      const showDigit = p < layout.effectiveResultLen;
                      return (
                        <DigitCell
                          key={i}
                          emphasis="bold"
                          digit={showDigit ? layout.finalResultDigits[p] : undefined}
                          revealed={revealedResults.has(p)}
                          active={activeColumn === p}
                          borderLeft={i !== 0}
                        />
                      );
                    })}
                    {editable && <div className="w-3 h-9 border-l border-blue-200" aria-hidden />}
                    <div className="w-8 h-9 border-l border-blue-200" />
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>

      {layout.operation === "subtraction" && layout.negative && (
        <p className="mt-2 text-sm text-amber-700 italic">
          Numărul de sus trebuie să fie cel puțin egal cu cel de jos.
        </p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
        <button
          type="button"
          onClick={() => setPlayCount((c) => c + 1)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-md transition-colors"
          aria-label="Reia animația"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reia
        </button>

        {editable && (
          <span className="text-xs italic text-gray-400">încearcă alte numere</span>
        )}
      </div>
    </div>
  );
}

// ─── Input view (mode="input") — solving-mode entry ──────────────────────────
//
// Used by column_arithmetic exercise blocks. Operands are display-only; the
// student fills the result row right-to-left, the way column arithmetic
// actually computes (units → tens → hundreds → ...).
//
// Model: the result row is a fixed-width digit array (LSB-first), each cell
// independent. Default cursor on render is the units cell (rightmost).
// Typing a digit fills the focused cell and moves the cursor LEFT (higher
// place value); Backspace clears the focused cell and moves the cursor RIGHT;
// clicking a cell focuses it (out-of-order entry / corrections). No grow
// cursor, no prepend slot — the lesson editor's left-to-right model is the
// wrong fit for solving a known column problem.
//
// Assembled answer: read MSB-first with empty cells worth 0 in place value,
// then drop leading zeros.

function maxResultWidth(
  operation: ColumnArithmeticOperation,
  operands: number[],
): number {
  const lens = operands.map(lenOf);
  if (operation === "addition") {
    // Use actual sum length — covers carry-out without over-allocating.
    return Math.max(1, lenOf(operands.reduce((a, b) => a + b, 0)));
  }
  if (operation === "subtraction") {
    return Math.max(1, lens[0] ?? 1);
  }
  // multiplication
  return Math.max(1, (lens[0] ?? 0) + (lens[1] ?? 0));
}

function assembleResult(digits: (number | null)[]): string {
  if (digits.every((d) => d === null)) return "";
  // Empty cells count as 0 in place value; String(number) drops leading zeros.
  const value = digits.reduce<number>(
    (acc, d, lsbPos) => acc + (d ?? 0) * Math.pow(10, lsbPos),
    0,
  );
  return String(value);
}

function ArithmeticInputView({
  operands,
  operation,
  onResultChange,
}: {
  operands: number[];
  operation: ColumnArithmeticOperation;
  onResultChange: (resultStr: string) => void;
}) {
  const resultWidth = useMemo(
    () => maxResultWidth(operation, operands),
    [operation, operands],
  );

  // Result row digits, LSB-first. null = empty cell.
  const [resultDigits, setResultDigits] = useState<(number | null)[]>(() =>
    new Array(resultWidth).fill(null),
  );
  // LSB-indexed cursor position. 0 = units (rightmost cell). On mount the
  // useEffect below focuses this cell so the student can type immediately.
  const [focusedLsbPos, setFocusedLsbPos] = useState(0);
  const cellRefs = useRef<Map<number, HTMLInputElement>>(new Map());

  // Typing a digit: fill the cell, move cursor LEFT. At the leftmost cell, stay.
  const setDigit = (lsbPos: number, d: number) => {
    setResultDigits((prev) => {
      if (prev[lsbPos] === d) return prev;
      const next = prev.slice();
      next[lsbPos] = d;
      return next;
    });
    setFocusedLsbPos(Math.min(lsbPos + 1, resultWidth - 1));
  };
  // Backspace: clear the cell, move cursor RIGHT. At units, stay.
  const clearDigit = (lsbPos: number) => {
    setResultDigits((prev) => {
      if (prev[lsbPos] === null) return prev;
      const next = prev.slice();
      next[lsbPos] = null;
      return next;
    });
    setFocusedLsbPos(Math.max(lsbPos - 1, 0));
  };

  // Focus follows focusedLsbPos. Runs on mount (default units cell) and on
  // every cursor move triggered by setDigit / clearDigit.
  useEffect(() => {
    const el = cellRefs.current.get(focusedLsbPos);
    if (el) {
      el.focus();
      el.select();
    }
  }, [focusedLsbPos]);

  // Emit assembled answer on every change.
  useEffect(() => {
    onResultChange(assembleResult(resultDigits));
  }, [resultDigits, onResultChange]);

  const gridWidth = resultWidth;
  const lsbAt = (i: number) => gridWidth - 1 - i;
  const cols = Array.from({ length: gridWidth }, (_, i) => i);
  const sign = OP_SYMBOL[operation];

  const registerRef = (lsbPos: number) => (el: HTMLInputElement | null) => {
    if (el) cellRefs.current.set(lsbPos, el);
    else cellRefs.current.delete(lsbPos);
  };

  const placeLabels = ["unități", "zeci", "sute", "mii", "zeci de mii", "sute de mii"];

  return (
    <div className="my-4">
      <div className="overflow-x-auto">
        <div className="inline-block rounded-md border border-blue-200 bg-blue-50/40 shadow-sm font-mono select-none">
          {/* Operand rows — display-only, right-anchored within the result-row width. */}
          {operands.map((opVal, rowIdx) => {
            const opK = lenOf(opVal);
            const opFilledFromMsb = gridWidth - opK;
            return (
              <div
                key={rowIdx}
                className={"flex" + (rowIdx > 0 ? " border-t border-blue-200" : "")}
              >
                {cols.map((i) => {
                  const p = lsbAt(i);
                  if (i >= opFilledFromMsb) {
                    return (
                      <DigitCell key={i} digit={digitAt(opVal, p)} borderLeft={i !== 0} />
                    );
                  }
                  return (
                    <div
                      key={i}
                      className={"w-8 h-9 " + (i !== 0 ? "border-l border-blue-200" : "")}
                    />
                  );
                })}
                {/* Operator column — sign on the FIRST operand row only. */}
                <div className="w-8 h-9 flex items-center justify-center text-lg text-gray-900 border-l border-blue-200">
                  {rowIdx === 0 ? sign : ""}
                </div>
              </div>
            );
          })}

          {/* Sum / diff / product line. */}
          <div className="border-t-2 border-gray-800" />

          {/* Editable result row — fixed-width digit array, each cell independent. */}
          <div className="flex">
            {cols.map((i) => {
              const lsbPos = lsbAt(i);
              return (
                <DigitCell
                  key={i}
                  variant="editable"
                  emphasis="bold"
                  digit={resultDigits[lsbPos] ?? null}
                  borderLeft={i !== 0}
                  onDigit={(d) => setDigit(lsbPos, d)}
                  onBackspace={() => clearDigit(lsbPos)}
                  inputRef={registerRef(lsbPos)}
                  ariaLabel={`Rezultat, ${placeLabels[lsbPos] ?? `poziția ${lsbPos + 1}`}`}
                />
              );
            })}
            {/* Operator column placeholder in result row. */}
            <div className="w-8 h-9 border-l border-blue-200" />
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Scratch view (mode="scratch") — ciornă draft surface ────────────────────
//
// Empty column, all cells waiting. The student types operands, partial
// products (multiplication), and the result with no auto-computation, no
// animation, no carry/borrow rendering. Editable rows (operand + partial) use
// the free-entry keystroke model (display + editable in spirit, but without
// the digit cap — scratch has no upper bound): grow caret at the right end,
// prepend slot adjacent to the MSB once a digit exists, per-cell overtype
// with cursor-advance-right, Backspace trims. Result row uses the
// solving-mode keystroke model (input): each cell independent, cursor starts
// at units, typing moves cursor LEFT, Backspace moves cursor RIGHT.
//
// gridWidth is dynamic — it grows as any row's content reaches the right
// edge, with overflow-x-auto for the wide cases. Partials sit between the
// top sum line and a second sum line that's specific to multiplication;
// addition + subtraction skip both the partial stack and the second line.

interface FreeEntryHandlers {
  /** Overtype the digit at gridLsbPos (the global column index, LSB = 0). */
  overtype: (idx: number, gridLsbPos: number, newD: number) => void;
  /** Append d to LSB; grows the row leftward. */
  append: (idx: number, d: number) => void;
  /** Insert d as the new MSB. */
  prepend: (idx: number, d: number) => void;
  /** Delete the digit at gridLsbPos (or trim units when called from grow / prepend). */
  deleteAt: (idx: number, gridLsbPos: number) => void;
}

type ScratchRowType = "op" | "partial";

interface ScratchFocusIntent {
  rowType: ScratchRowType;
  rowIdx: number;
  kind: "cell" | "grow" | "prepend";
  /** Grid LSB position for `kind === "cell"`. Ignored otherwise. */
  lsbPos?: number;
}

function scratchInitialGridWidth(op: ColumnArithmeticOperation): number {
  if (op === "addition") return MAX_OPERAND_DIGITS.addition + 1;
  if (op === "subtraction") return MAX_OPERAND_DIGITS.subtraction;
  return MAX_OPERAND_DIGITS.multiplication * 2;
}

/** Cycle order for the scratch operator-sign button: + → − → × → + */
function nextOperation(
  op: ColumnArithmeticOperation,
): ColumnArithmeticOperation {
  if (op === "addition") return "subtraction";
  if (op === "subtraction") return "multiplication";
  return "addition";
}

const SCRATCH_PLACE_LABELS = [
  "unități",
  "zeci",
  "sute",
  "mii",
  "zeci de mii",
  "sute de mii",
  "milioane",
  "zeci de milioane",
];

function ArithmeticScratchView({
  operation,
  initialOperands,
  onOperationChange,
}: {
  operation: ColumnArithmeticOperation;
  /**
   * Optional seed for the two operand rows. Empty / shorter arrays leave the
   * remaining slots as null (empty). Used by smart-scan placement so a card
   * arrives with "123 + 456" already filled in.
   */
  initialOperands?: number[];
  /**
   * When provided, the operator sign on operand row 1 becomes a cycling
   * button. Omitted from lesson/exercise call sites so the sign stays static
   * there.
   */
  onOperationChange?: (next: ColumnArithmeticOperation) => void;
}) {
  const initialGridWidth = scratchInitialGridWidth(operation);
  const sign = OP_SYMBOL[operation];

  // Binary for all three operations in scratch (simplest UX; addition's
  // n-ary form belongs to lessons, not the draft surface). null = empty.
  const [operands, setOperands] = useState<(number | null)[]>(() => {
    const a = initialOperands?.[0];
    const b = initialOperands?.[1];
    return [
      typeof a === "number" && Number.isFinite(a) && a >= 0 ? a : null,
      typeof b === "number" && Number.isFinite(b) && b >= 0 ? b : null,
    ];
  });
  // One partial per multiplier digit (LSB-first). Empty for non-mul or empty multiplier.
  const [partials, setPartials] = useState<(number | null)[]>([]);
  const [resultDigits, setResultDigits] = useState<(number | null)[]>(() =>
    new Array(initialGridWidth).fill(null),
  );

  // ── Dynamic gridWidth ─────────────────────────────────────────────────────
  // Grows to fit the widest content + one cell of breathing room (so the
  // prepend slot for the longest row stays reachable). Never shrinks below
  // the initial guess.
  const contentMaxLsb = useMemo(() => {
    let max = -1;
    for (const op of operands) {
      if (op != null) max = Math.max(max, lenOf(op) - 1);
    }
    partials.forEach((p, i) => {
      if (p != null) max = Math.max(max, i + lenOf(p) - 1);
    });
    for (let i = resultDigits.length - 1; i >= 0; i--) {
      if (resultDigits[i] != null) {
        max = Math.max(max, i);
        break;
      }
    }
    return max;
  }, [operands, partials, resultDigits]);
  const gridWidth = Math.max(initialGridWidth, contentMaxLsb + 2);

  // Grow resultDigits to gridWidth (never shrink — would lose typed cells).
  useEffect(() => {
    setResultDigits((prev) => {
      if (prev.length >= gridWidth) return prev;
      const next = prev.slice();
      while (next.length < gridWidth) next.push(null);
      return next;
    });
  }, [gridWidth]);

  // Sync partial row count. For multiplication, the count matches the
  // multiplier's digit count; for other operations partials are always empty
  // (so a cycle from mul → add/sub clears any leftover partial values).
  useEffect(() => {
    if (operation !== "multiplication") {
      setPartials((prev) => (prev.length === 0 ? prev : []));
      return;
    }
    const multiplier = operands[1];
    const count = multiplier == null ? 0 : lenOf(multiplier);
    setPartials((prev) => {
      if (prev.length === count) return prev;
      if (prev.length < count) {
        const next = prev.slice();
        while (next.length < count) next.push(null);
        return next;
      }
      return prev.slice(0, count);
    });
  }, [operands, operation]);

  // Reset answer state when operation changes — operands preserve, but the
  // result row clears (and the partials sync above clears partials). On the
  // initial mount this is effectively a no-op since resultDigits starts as
  // all-nulls.
  const prevOperationRef = useRef(operation);
  useEffect(() => {
    if (prevOperationRef.current === operation) return;
    prevOperationRef.current = operation;
    setResultDigits(new Array(scratchInitialGridWidth(operation)).fill(null));
  }, [operation]);

  // ── Refs + focus ──────────────────────────────────────────────────────────
  const operandRefs = useRef<Map<string, HTMLInputElement>>(new Map());
  const partialRefs = useRef<Map<string, HTMLInputElement>>(new Map());
  const resultRefs = useRef<Map<number, HTMLInputElement>>(new Map());
  const [focusIntent, setFocusIntent] = useState<ScratchFocusIntent | null>(null);

  // ── Free-entry handler factory (no caps in scratch) ───────────────────────
  // Shared by operands (shift = 0) and partial-product rows (shift = row idx).
  // gridLsbPos is the GRID column; the value's own LSB pos is gridLsbPos - shift.
  const makeHandlers = (
    values: (number | null)[],
    setValues: React.Dispatch<React.SetStateAction<(number | null)[]>>,
    rowType: ScratchRowType,
    shiftOf: (idx: number) => number,
  ): FreeEntryHandlers => ({
    overtype: (idx, gridLsbPos, newD) => {
      const cur = values[idx];
      if (cur == null) return;
      const shift = shiftOf(idx);
      const valLsbPos = gridLsbPos - shift;
      if (valLsbPos < 0) return;
      const oldD = digitAt(cur, valLsbPos) ?? 0;
      if (oldD !== newD) {
        const next = cur + (newD - oldD) * Math.pow(10, valLsbPos);
        if (next >= 0) {
          setValues((prev) => prev.map((v, i) => (i === idx ? next : v)));
        }
      }
      if (gridLsbPos > shift) {
        setFocusIntent({ rowType, rowIdx: idx, kind: "cell", lsbPos: gridLsbPos - 1 });
      } else {
        setFocusIntent({ rowType, rowIdx: idx, kind: "grow" });
      }
    },
    append: (idx, d) => {
      const cur = values[idx];
      if (cur === undefined) return;
      if (cur === null) {
        setValues((prev) => prev.map((v, i) => (i === idx ? d : v)));
        setFocusIntent({ rowType, rowIdx: idx, kind: "grow" });
        return;
      }
      const next = cur * 10 + d;
      if (next === cur) return;
      setValues((prev) => prev.map((v, i) => (i === idx ? next : v)));
      setFocusIntent({ rowType, rowIdx: idx, kind: "grow" });
    },
    prepend: (idx, d) => {
      const cur = values[idx];
      if (cur == null) return;
      if (d === 0) return;
      const k = lenOf(cur);
      const next = d * Math.pow(10, k) + cur;
      setValues((prev) => prev.map((v, i) => (i === idx ? next : v)));
      setFocusIntent({ rowType, rowIdx: idx, kind: "prepend" });
    },
    deleteAt: (idx, gridLsbPos) => {
      const cur = values[idx];
      if (cur == null) return;
      const shift = shiftOf(idx);
      const valLsbPos = gridLsbPos - shift;
      if (valLsbPos < 0) return;
      if (lenOf(cur) <= 1) {
        setValues((prev) => prev.map((v, i) => (i === idx ? null : v)));
        setFocusIntent({ rowType, rowIdx: idx, kind: "grow" });
        return;
      }
      const pow = Math.pow(10, valLsbPos);
      const highPart = Math.floor(cur / (pow * 10));
      const lowPart = cur % pow;
      const next = highPart * pow + lowPart;
      setValues((prev) => prev.map((v, i) => (i === idx ? next : v)));
      if (gridLsbPos === shift) {
        setFocusIntent({ rowType, rowIdx: idx, kind: "grow" });
      } else {
        setFocusIntent({ rowType, rowIdx: idx, kind: "cell", lsbPos: gridLsbPos - 1 });
      }
    },
  });

  const operandHandlers = makeHandlers(operands, setOperands, "op", () => 0);
  const partialHandlers = makeHandlers(partials, setPartials, "partial", (idx) => idx);

  // ── Result mutators (solving-mode) ─────────────────────────────────────────
  // Imperative focus (no state-driven effect) so the initial mount focus on
  // op-0-grow isn't fought over by an effect that runs at mount with lsbPos=0.
  const focusResultAt = (lsbPos: number) => {
    requestAnimationFrame(() => {
      const el = resultRefs.current.get(lsbPos);
      if (el) {
        el.focus();
        el.select();
      }
    });
  };
  const setResultDigit = (lsbPos: number, d: number) => {
    setResultDigits((prev) => {
      if (prev[lsbPos] === d) return prev;
      const next = prev.slice();
      next[lsbPos] = d;
      return next;
    });
    focusResultAt(Math.min(lsbPos + 1, gridWidth - 1));
  };
  const clearResultDigit = (lsbPos: number) => {
    setResultDigits((prev) => {
      if (prev[lsbPos] === null) return prev;
      const next = prev.slice();
      next[lsbPos] = null;
      return next;
    });
    focusResultAt(Math.max(lsbPos - 1, 0));
  };

  // ── Initial focus + focusIntent resolver ──────────────────────────────────
  useEffect(() => {
    operandRefs.current.get("op-0-grow")?.focus();
  }, []);

  useEffect(() => {
    if (!focusIntent) return;
    const refMap =
      focusIntent.rowType === "op" ? operandRefs.current : partialRefs.current;
    const prefix = focusIntent.rowType;
    const values = focusIntent.rowType === "op" ? operands : partials;
    const value = values[focusIntent.rowIdx];
    if (value === undefined) {
      setFocusIntent(null);
      return;
    }
    let refKey: string;
    if (focusIntent.kind === "cell") {
      const shift = focusIntent.rowType === "partial" ? focusIntent.rowIdx : 0;
      const k = value == null ? 0 : lenOf(value);
      const filledMin = shift;
      const filledMax = shift + k - 1;
      const lsb = focusIntent.lsbPos ?? -1;
      if (lsb < filledMin || lsb > filledMax) {
        refKey = `${prefix}-${focusIntent.rowIdx}-grow`;
      } else {
        const msbIdx = gridWidth - 1 - lsb;
        refKey = `${prefix}-${focusIntent.rowIdx}-${msbIdx}`;
      }
    } else if (focusIntent.kind === "prepend") {
      refKey = `${prefix}-${focusIntent.rowIdx}-prepend`;
      if (!refMap.has(refKey)) refKey = `${prefix}-${focusIntent.rowIdx}-grow`;
    } else {
      refKey = `${prefix}-${focusIntent.rowIdx}-grow`;
    }
    const el = refMap.get(refKey);
    if (el) {
      el.focus();
      el.select();
    }
    setFocusIntent(null);
  }, [focusIntent, operands, partials, gridWidth]);

  const resultAllNull = useMemo(
    () => resultDigits.every((d) => d == null),
    [resultDigits],
  );

  const cols = useMemo(
    () => Array.from({ length: gridWidth }, (_, i) => i),
    [gridWidth],
  );
  const lsbAt = (i: number) => gridWidth - 1 - i;

  return (
    <div className="my-2">
      <div className="overflow-x-auto">
        <div className="inline-block rounded-md border border-blue-200 bg-blue-50/40 shadow-sm font-mono select-none">
          {operands.map((opVal, rowIdx) => (
            <EditableDigitRow
              key={`op-${rowIdx}`}
              rowType="op"
              rowIdx={rowIdx}
              value={opVal}
              shift={0}
              refs={operandRefs}
              handlers={operandHandlers}
              showSign={rowIdx === 0}
              hasTopBorder={rowIdx > 0}
              cols={cols}
              lsbAt={lsbAt}
              gridWidth={gridWidth}
              sign={sign}
              ariaRowLabel={`Termen ${rowIdx + 1}`}
              clickToFocusWhenEmpty
              onSignClick={
                rowIdx === 0 && onOperationChange
                  ? () => onOperationChange(nextOperation(operation))
                  : undefined
              }
            />
          ))}

          <div className="border-t-2 border-gray-800" />

          {operation === "multiplication" && partials.length > 0 && (
            <>
              {partials.map((pVal, idx) => (
                <EditableDigitRow
                  key={`partial-${idx}`}
                  rowType="partial"
                  rowIdx={idx}
                  value={pVal}
                  shift={idx}
                  refs={partialRefs}
                  handlers={partialHandlers}
                  showSign={false}
                  hasTopBorder={idx > 0}
                  cols={cols}
                  lsbAt={lsbAt}
                  gridWidth={gridWidth}
                  sign={sign}
                  ariaRowLabel={`Produs parțial ${idx + 1}`}
                />
              ))}
              <div className="border-t-2 border-gray-800" />
            </>
          )}

          {/* Result row — solving-mode. When empty, mousedown-anywhere routes
              focus to units (the default starting cell), matching the
              click-to-focus rule for the empty operand area. */}
          <div
            className="flex"
            onMouseDown={
              resultAllNull
                ? (e) => {
                    e.preventDefault();
                    const el = resultRefs.current.get(0);
                    if (el) {
                      el.focus();
                      el.select();
                    }
                  }
                : undefined
            }
          >
            {cols.map((i) => {
              const lsbPos = lsbAt(i);
              return (
                <DigitCell
                  key={i}
                  variant="editable"
                  emphasis="bold"
                  digit={resultDigits[lsbPos] ?? null}
                  borderLeft={i !== 0}
                  onDigit={(d) => setResultDigit(lsbPos, d)}
                  onBackspace={() => clearResultDigit(lsbPos)}
                  inputRef={(el) => {
                    if (el) resultRefs.current.set(lsbPos, el);
                    else resultRefs.current.delete(lsbPos);
                  }}
                  ariaLabel={`Rezultat, ${SCRATCH_PLACE_LABELS[lsbPos] ?? `poziția ${lsbPos + 1}`}`}
                />
              );
            })}
            <div className="w-3 h-9 border-l border-blue-200" aria-hidden />
            <div className="w-8 h-9 border-l border-blue-200" />
          </div>
        </div>
      </div>

      {operation === "subtraction" &&
        operands[0] != null &&
        operands[1] != null &&
        operands[0] < operands[1] && (
          <p className="mt-2 text-sm text-amber-700 italic">
            Numărul de sus trebuie să fie cel puțin egal cu cel de jos.
          </p>
        )}
    </div>
  );
}

// ─── Editable digit row (scratch operands + partials) ────────────────────────
//
// One row of the scratch grid that holds a single numeric value, optionally
// shifted left by N grid columns. Renders inert spacers, filled DigitCells,
// an optional prepend slot to the left of the MSB, and a slim grow caret on
// the right. The operator sign column sits in a sibling div so the
// click-to-focus wrapper (applied when value === null) doesn't capture
// clicks on the sign.

interface EditableDigitRowProps {
  rowType: ScratchRowType;
  rowIdx: number;
  value: number | null;
  /** Grid LSB column where this value's units sit. 0 = right edge. */
  shift: number;
  refs: React.MutableRefObject<Map<string, HTMLInputElement>>;
  handlers: FreeEntryHandlers;
  showSign: boolean;
  hasTopBorder: boolean;
  cols: number[];
  lsbAt: (i: number) => number;
  gridWidth: number;
  sign: string;
  ariaRowLabel: string;
  /** When true and value === null, mousedown-anywhere focuses the grow caret. */
  clickToFocusWhenEmpty?: boolean;
  /**
   * Scratch-only: when provided AND showSign, the operator sign cell renders
   * as a button that cycles the operation. Omitting it (lesson / exercise
   * paths) keeps the sign cell a non-interactive span.
   */
  onSignClick?: () => void;
}

function EditableDigitRow({
  rowType,
  rowIdx,
  value,
  shift,
  refs,
  handlers,
  showSign,
  hasTopBorder,
  cols,
  lsbAt,
  gridWidth,
  sign,
  ariaRowLabel,
  clickToFocusWhenEmpty = false,
  onSignClick,
}: EditableDigitRowProps) {
  const k = value == null ? 0 : lenOf(value);
  const filledMinGridLsb = shift;
  const filledMaxGridLsb = shift + k - 1;
  // Prepend slot sits one grid column LEFT of the current MSB, only when the
  // row already has at least one digit (the empty state uses the grow caret
  // for first-digit entry; a prepend slot in that state would be redundant).
  const prependGridLsb = k > 0 && shift + k < gridWidth ? shift + k : -1;
  const growKey = `${rowType}-${rowIdx}-grow`;
  const isEmpty = value == null;

  return (
    <div className={"flex" + (hasTopBorder ? " border-t border-blue-200" : "")}>
      <div
        className="flex flex-1"
        onMouseDown={
          isEmpty && clickToFocusWhenEmpty
            ? (e) => {
                e.preventDefault();
                const el = refs.current.get(growKey);
                if (el) {
                  el.focus();
                  el.select();
                }
              }
            : undefined
        }
      >
        {cols.map((i) => {
          const p = lsbAt(i);
          const refKey = `${rowType}-${rowIdx}-${i}`;

          if (value != null && p >= filledMinGridLsb && p <= filledMaxGridLsb) {
            const valLsbPos = p - shift;
            const d = digitAt(value, valLsbPos);
            return (
              <DigitCell
                key={i}
                variant="editable"
                digit={d}
                borderLeft={i !== 0}
                onDigit={(newD) => handlers.overtype(rowIdx, p, newD)}
                onBackspace={() => handlers.deleteAt(rowIdx, p)}
                ariaLabel={`${ariaRowLabel}, cifra ${k - valLsbPos}`}
                inputRef={(el) => {
                  if (el) refs.current.set(refKey, el);
                  else refs.current.delete(refKey);
                }}
              />
            );
          }

          if (p === prependGridLsb) {
            const prependKey = `${rowType}-${rowIdx}-prepend`;
            return (
              <input
                key={i}
                ref={(el) => {
                  if (el) refs.current.set(prependKey, el);
                  else refs.current.delete(prependKey);
                }}
                type="text"
                inputMode="numeric"
                autoComplete="off"
                value=""
                placeholder="+"
                aria-label={`${ariaRowLabel}, adaugă cifră în față`}
                onFocus={(e) => e.currentTarget.select()}
                onChange={(e) => {
                  const v = e.target.value;
                  if (v === "") return;
                  const last = v.charAt(v.length - 1);
                  if (last >= "0" && last <= "9") handlers.prepend(rowIdx, Number(last));
                }}
                onKeyDown={(e) => {
                  if (e.key === "Backspace") {
                    e.preventDefault();
                    handlers.deleteAt(rowIdx, shift);
                  }
                }}
                className={
                  "w-8 h-9 p-0 m-0 text-center font-mono text-lg leading-9 " +
                  "bg-indigo-50/50 text-indigo-700 placeholder:text-indigo-300 " +
                  "transition-colors focus:bg-indigo-100/70 focus:outline-none " +
                  "focus:ring-1 focus:ring-indigo-400 focus:ring-inset caret-indigo-500 " +
                  (i !== 0 ? "border-l border-blue-200" : "")
                }
              />
            );
          }

          return (
            <div
              key={i}
              className={"w-8 h-9 " + (i !== 0 ? "border-l border-blue-200" : "")}
            />
          );
        })}

        <input
          ref={(el) => {
            if (el) refs.current.set(growKey, el);
            else refs.current.delete(growKey);
          }}
          type="text"
          inputMode="numeric"
          autoComplete="off"
          value=""
          aria-label={`${ariaRowLabel}, scrie cifre`}
          onFocus={(e) => e.currentTarget.select()}
          onChange={(e) => {
            const v = e.target.value;
            if (v === "") return;
            const last = v.charAt(v.length - 1);
            if (last >= "0" && last <= "9") handlers.append(rowIdx, Number(last));
          }}
          onKeyDown={(e) => {
            if (e.key === "Backspace") {
              e.preventDefault();
              handlers.deleteAt(rowIdx, shift);
            }
          }}
          className="w-3 h-9 p-0 m-0 bg-transparent text-center font-mono text-lg leading-9 text-gray-900 border-l border-blue-200 transition-colors focus:bg-blue-100/70 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:ring-inset caret-blue-500"
        />
      </div>

      {showSign && onSignClick ? (
        <button
          type="button"
          onPointerDown={(e) => e.stopPropagation()}
          onClick={onSignClick}
          aria-label="Schimbă operația"
          title="Schimbă operația"
          className="w-8 h-9 flex items-center justify-center text-lg text-gray-900
            border-l border-blue-200 cursor-pointer transition-colors
            hover:bg-amber-100
            focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-inset"
        >
          {sign}
        </button>
      ) : (
        <div className="w-8 h-9 flex items-center justify-center text-lg text-gray-900 border-l border-blue-200">
          {showSign ? sign : ""}
        </div>
      )}
    </div>
  );
}

// Re-export for callers that want to narrow.
export type { ColumnArithmeticConfig };
