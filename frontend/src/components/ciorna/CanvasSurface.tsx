/**
 * CanvasSurface — free-positioning paper hosting cards + per-cell handwriting.
 *
 * The notebook paper IS the editable surface: each 32 × 32 canvas grid cell
 * can hold one character. There's no TextBlock primitive — text lives in a
 * sparse Map keyed by "gx,gy" and renders as font-mono spans dropped onto
 * the gridded backdrop.
 *
 * State:
 *   - `cards: CanvasCardItem[]` — placed components; same shape as Phase 3a/b.
 *   - `cellText: Map<string, string>` — sparse "gx,gy" → single character.
 *   - `focusedCell: { gx, gy } | null` — current typing cursor.
 *   - pan / scale unchanged.
 *
 * Keyboard capture: a hidden <input> inside the transformed inner layer,
 * moved imperatively to the focused cell so iOS / Android show the on-screen
 * keyboard with the cursor in view. The input runs in a "sentinel" mode for
 * mobile soft-keyboard reliability: its value is held at a zero-width-space;
 * insertions push the typed char into the focused cell and reset the value,
 * and deletions (value shorter than the sentinel) fire backspace. Desktop
 * onKeyDown handles Enter / Esc / Arrows / Backspace / printable chars
 * directly so all those paths work whether or not `beforeinput` fires.
 *
 * Click-vs-pan: same 5 px movement threshold as Phase 3c. Click on canvas
 * background → focus the underlying cell (and synchronously focus the
 * hidden input so iOS opens its keyboard within the user gesture).
 * Click on a card → pan handler skips; hidden input blurs naturally and
 * the cursor disappears until the user clicks back on the paper.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { scratchScanLeadingCols } from "@/components/lesson/interactive/ColumnArithmetic";
import type { ColumnArithmeticOperation } from "@/types/lesson";

import CanvasCard from "./CanvasCard";
import CanvasToolbar from "./CanvasToolbar";
import { CIORNA_COMPONENTS, findComponent } from "./registry";

export interface CanvasCardItem {
  id: string;
  componentId: string;
  x: number;
  y: number;
  /**
   * Set when the card was placed by smart-scan ("123 + 456" → operands
   * [123, 456]); undefined when added from the picker. Passed through to the
   * registry's render() to seed the component's initial state.
   */
  operands?: number[];
  /**
   * Column-arithmetic only. Picker-added cards default to "addition";
   * smart-scan cards inherit the matched operator. Mutable via the cycling
   * operator-sign button inside the card (scratch mode only).
   */
  operation?: ColumnArithmeticOperation;
}

function nextOperation(
  op: ColumnArithmeticOperation,
): ColumnArithmeticOperation {
  if (op === "addition") return "subtraction";
  if (op === "subtraction") return "multiplication";
  return "addition";
}

interface FocusedCell {
  gx: number;
  gy: number;
}

const GRID_PX = 32;

const MIN_SCALE = 0.25;
const MAX_SCALE = 2;
const WHEEL_ZOOM_STEP = 0.0015;
const BUTTON_ZOOM_STEP = 0.25;
const FIT_PADDING_PX = 32;
const CLICK_THRESHOLD_PX = 5;
// Zero-width space — held in the hidden input so mobile keyboards have a
// character to delete on Backspace. Insertions land after it; deletions
// shrink the value below this length and we read that as backspace.
const SENTINEL = "​";

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}

/** Snap a canvas coordinate to the nearest whole cell origin. */
function snapToGrid(v: number): number {
  return Math.round(v / GRID_PX) * GRID_PX;
}

function makeId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function cellKey(gx: number, gy: number): string {
  return `${gx},${gy}`;
}

export default function CanvasSurface() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  const hiddenInputRef = useRef<HTMLInputElement>(null);

  const [cards, setCards] = useState<CanvasCardItem[]>([]);
  const [cellText, setCellText] = useState<Map<string, string>>(() => new Map());
  const [focusedCell, setFocusedCell] = useState<FocusedCell | null>(null);
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const placementCountRef = useRef(0);
  // Stable ref to the latest focused cell so the hidden-input event handlers
  // (attached once) always read the current cursor without re-binding.
  const focusedCellRef = useRef<FocusedCell | null>(null);
  focusedCellRef.current = focusedCell;

  // ── Cell mutators ─────────────────────────────────────────────────────────
  const writeCells = useCallback(
    (entries: { gx: number; gy: number; char: string }[]) => {
      if (entries.length === 0) return;
      setCellText((prev) => {
        const next = new Map(prev);
        for (const { gx, gy, char } of entries) {
          next.set(cellKey(gx, gy), char);
        }
        return next;
      });
    },
    [],
  );
  const clearCell = useCallback((gx: number, gy: number) => {
    setCellText((prev) => {
      const k = cellKey(gx, gy);
      if (!prev.has(k)) return prev;
      const next = new Map(prev);
      next.delete(k);
      return next;
    });
  }, []);

  // ── Hidden-input position + focus ─────────────────────────────────────────
  // Imperative positioning rather than React-state-driven style so the input
  // can be moved synchronously inside the pointerup handler before .focus(),
  // which is required for iOS to open the on-screen keyboard.
  const positionInputAt = (gx: number, gy: number) => {
    const input = hiddenInputRef.current;
    if (!input) return;
    input.style.left = `${gx * GRID_PX}px`;
    input.style.top = `${gy * GRID_PX}px`;
  };

  const focusCellAt = (canvasX: number, canvasY: number) => {
    const gx = Math.floor(canvasX / GRID_PX);
    const gy = Math.floor(canvasY / GRID_PX);
    setFocusedCell({ gx, gy });
    const input = hiddenInputRef.current;
    if (input) {
      positionInputAt(gx, gy);
      input.value = SENTINEL;
      input.focus();
    }
  };

  // ── Typing actions ────────────────────────────────────────────────────────
  const advanceCursor = (dx: number, dy: number) => {
    const cur = focusedCellRef.current;
    if (!cur) return;
    const next = { gx: cur.gx + dx, gy: cur.gy + dy };
    setFocusedCell(next);
    positionInputAt(next.gx, next.gy);
  };

  const handleChars = (chars: string) => {
    if (!chars) return;
    const cur = focusedCellRef.current;
    if (!cur) return;
    let gx = cur.gx;
    const gy = cur.gy;
    const writes: { gx: number; gy: number; char: string }[] = [];
    for (const ch of chars) {
      writes.push({ gx, gy, char: ch });
      gx += 1;
    }
    writeCells(writes);
    const next = { gx, gy };
    setFocusedCell(next);
    positionInputAt(next.gx, next.gy);
  };

  // Backspace: if the focused cell holds a character, clear it and leave the
  // cursor where it is; if the cell is already empty, step the cursor one cell
  // left and delete nothing. (Shared by the desktop keydown path and the
  // mobile sentinel-delete path — both route through here.)
  const handleBackspace = () => {
    const cur = focusedCellRef.current;
    if (!cur) return;
    const hasChar = cellText.get(cellKey(cur.gx, cur.gy)) !== undefined;
    if (hasChar) {
      clearCell(cur.gx, cur.gy);
    } else {
      const target = { gx: cur.gx - 1, gy: cur.gy };
      setFocusedCell(target);
      positionInputAt(target.gx, target.gy);
    }
  };

  // ── Smart scan: cells → component card ────────────────────────────────────
  // Builds the contiguous run of filled cells around the cursor's current
  // position (walking left to the first gap, then right to the first gap),
  // tries each registered pattern, and on the first match replaces the
  // matched cells with a placed card carrying the parsed operands.
  const scanRunAndMaybePlaceCard = () => {
    const cur = focusedCellRef.current;
    if (!cur) return;

    // Walk left from one cell before the cursor; collect chars until a gap.
    const leftChars: string[] = [];
    let g = cur.gx - 1;
    while (true) {
      const ch = cellText.get(cellKey(g, cur.gy));
      if (ch === undefined) break;
      leftChars.push(ch);
      g--;
    }
    leftChars.reverse(); // restore left-to-right order
    const leftmostGx = g + 1;

    // Walk right starting at the cursor's own cell (might be empty — then
    // rightChars stays empty and the run is just the left side).
    const rightChars: string[] = [];
    g = cur.gx;
    while (true) {
      const ch = cellText.get(cellKey(g, cur.gy));
      if (ch === undefined) break;
      rightChars.push(ch);
      g++;
    }

    const runLen = leftChars.length + rightChars.length;
    if (runLen === 0) return;
    const runText = [...leftChars, ...rightChars].join("");

    for (const comp of CIORNA_COMPONENTS) {
      if (!comp.patterns) continue;
      for (const pattern of comp.patterns) {
        const result = pattern.match(runText);
        if (!result) continue;
        // Match — clear the run's cells and append the card.
        setCellText((prev) => {
          const next = new Map(prev);
          for (let i = 0; i < runLen; i++) {
            next.delete(cellKey(leftmostGx + i, cur.gy));
          }
          return next;
        });
        // The scratch grid right-anchors operands to the units column, so
        // operand 1's leftmost digit sits `leadingCols` cells in from the card
        // origin. Slide the card left by that much so operand 1's leftmost
        // digit lands exactly on the run's leftmost typed cell.
        const leadingCols = scratchScanLeadingCols(
          result.operation,
          result.operands,
        );
        const newCard: CanvasCardItem = {
          id: makeId("card"),
          componentId: comp.id,
          x: (leftmostGx - leadingCols) * GRID_PX,
          y: cur.gy * GRID_PX,
          operands: result.operands,
          operation: result.operation,
        };
        setCards((prev) => [...prev, newCard]);
        return;
      }
    }
  };

  const onInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!focusedCellRef.current) return;
    const key = e.key;
    if (key === "Enter") {
      e.preventDefault();
      // Smart-scan: if the contiguous run of cells around the cursor matches
      // a registered pattern, replace those cells with a pre-populated card.
      // Either way, the cursor still moves down one row afterward.
      scanRunAndMaybePlaceCard();
      advanceCursor(0, 1);
      return;
    }
    if (key === "Escape") {
      e.preventDefault();
      e.currentTarget.blur(); // onBlur clears focusedCell
      return;
    }
    if (key === "Backspace") {
      e.preventDefault();
      handleBackspace();
      return;
    }
    if (key === "ArrowLeft") {
      e.preventDefault();
      advanceCursor(-1, 0);
      return;
    }
    if (key === "ArrowRight") {
      e.preventDefault();
      advanceCursor(1, 0);
      return;
    }
    if (key === "ArrowUp") {
      e.preventDefault();
      advanceCursor(0, -1);
      return;
    }
    if (key === "ArrowDown") {
      e.preventDefault();
      advanceCursor(0, 1);
      return;
    }
    if (key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      // Printable; intercept here so desktop typing doesn't depend on the
      // beforeinput / sentinel path.
      e.preventDefault();
      handleChars(key);
      e.currentTarget.value = SENTINEL;
      return;
    }
  };

  const onInputInput = (e: React.FormEvent<HTMLInputElement>) => {
    // Sentinel-based fallback for mobile soft keyboards where keydown isn't
    // reliable. Compare current value to SENTINEL: longer = insertion,
    // shorter = backspace.
    const v = e.currentTarget.value;
    if (v === SENTINEL) return;
    if (v.length > SENTINEL.length) {
      // Strip the leading sentinel; the rest is what the user typed
      // (mobile autocorrect can submit multiple chars in one shot).
      const typed = v.startsWith(SENTINEL) ? v.slice(SENTINEL.length) : v;
      handleChars(typed);
    } else {
      // Sentinel was deleted.
      handleBackspace();
    }
    e.currentTarget.value = SENTINEL;
  };

  const onInputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.currentTarget.value = SENTINEL;
  };

  const onInputBlur = () => {
    setFocusedCell(null);
  };

  // ── Pan + click detection (5 px threshold) ────────────────────────────────
  const panStateRef = useRef<{
    startClientX: number;
    startClientY: number;
    startPanX: number;
    startPanY: number;
    moved: boolean;
  } | null>(null);

  const onPanPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.target !== canvasRef.current && e.target !== innerRef.current) return;
    if (e.button !== 0 && e.pointerType !== "touch") return;
    // If the hidden input is already focused, prevent the browser-default
    // focus shift to body — otherwise the on-screen keyboard closes between
    // taps on mobile. The first tap (input not yet focused) falls through to
    // default, then focusCellAt programmatically focuses inside the gesture.
    if (document.activeElement === hiddenInputRef.current) {
      e.preventDefault();
    }
    canvasRef.current?.setPointerCapture(e.pointerId);
    panStateRef.current = {
      startClientX: e.clientX,
      startClientY: e.clientY,
      startPanX: pan.x,
      startPanY: pan.y,
      moved: false,
    };
  };
  const onPanPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const state = panStateRef.current;
    if (!state) return;
    const dx = e.clientX - state.startClientX;
    const dy = e.clientY - state.startClientY;
    if (!state.moved && Math.hypot(dx, dy) > CLICK_THRESHOLD_PX) {
      state.moved = true;
    }
    if (state.moved) {
      setPan({
        x: state.startPanX + dx,
        y: state.startPanY + dy,
      });
    }
  };
  const onPanPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    const state = panStateRef.current;
    if (!state) return;
    try {
      canvasRef.current?.releasePointerCapture(e.pointerId);
    } catch {
      // already released
    }
    panStateRef.current = null;
    if (state.moved) return;
    // Click without drag → focus the cell under the cursor and open the
    // on-screen keyboard. Pan didn't change, so use the start values.
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const canvasX = (e.clientX - rect.left - state.startPanX) / scale;
    const canvasY = (e.clientY - rect.top - state.startPanY) / scale;
    focusCellAt(canvasX, canvasY);
  };

  // ── Zoom ──────────────────────────────────────────────────────────────────
  const zoomAt = useCallback(
    (pivotClientX: number, pivotClientY: number, nextScaleRaw: number) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      const nextScale = clamp(nextScaleRaw, MIN_SCALE, MAX_SCALE);
      const pivotLocalX = pivotClientX - rect.left;
      const pivotLocalY = pivotClientY - rect.top;
      const canvasX = (pivotLocalX - pan.x) / scale;
      const canvasY = (pivotLocalY - pan.y) / scale;
      setPan({
        x: pivotLocalX - canvasX * nextScale,
        y: pivotLocalY - canvasY * nextScale,
      });
      setScale(nextScale);
    },
    [pan, scale],
  );

  // Wheel zoom — gated to canvas/inner so palette can scroll.
  useEffect(() => {
    const el = canvasRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      const target = e.target as Node | null;
      if (!target) return;
      const onCanvas =
        target === canvasRef.current ||
        (innerRef.current?.contains(target) ?? false);
      if (!onCanvas) return;
      e.preventDefault();
      const factor = Math.exp(-e.deltaY * WHEEL_ZOOM_STEP);
      zoomAt(e.clientX, e.clientY, scale * factor);
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [scale, zoomAt]);

  // Pinch zoom.
  useEffect(() => {
    const el = canvasRef.current;
    if (!el) return;

    let pinchStart: {
      dist: number;
      scale: number;
      pivotCanvasX: number;
      pivotCanvasY: number;
    } | null = null;

    const dist = (a: Touch, b: Touch) =>
      Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    const mid = (a: Touch, b: Touch) => ({
      x: (a.clientX + b.clientX) / 2,
      y: (a.clientY + b.clientY) / 2,
    });

    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length !== 2) return;
      const target = e.target as Node | null;
      if (!target) return;
      const onCanvas =
        target === el || (innerRef.current?.contains(target) ?? false);
      if (!onCanvas) return;
      e.preventDefault();
      const rect = el.getBoundingClientRect();
      const [t0, t1] = [e.touches[0]!, e.touches[1]!];
      const m = mid(t0, t1);
      const pivotLocalX = m.x - rect.left;
      const pivotLocalY = m.y - rect.top;
      pinchStart = {
        dist: dist(t0, t1),
        scale,
        pivotCanvasX: (pivotLocalX - pan.x) / scale,
        pivotCanvasY: (pivotLocalY - pan.y) / scale,
      };
      panStateRef.current = null;
    };
    const onTouchMove = (e: TouchEvent) => {
      if (!pinchStart || e.touches.length !== 2) return;
      e.preventDefault();
      const [t0, t1] = [e.touches[0]!, e.touches[1]!];
      const newDist = dist(t0, t1);
      if (newDist <= 0) return;
      const nextScale = clamp(
        (pinchStart.scale * newDist) / pinchStart.dist,
        MIN_SCALE,
        MAX_SCALE,
      );
      const m = mid(t0, t1);
      const rect = el.getBoundingClientRect();
      const pivotLocalX = m.x - rect.left;
      const pivotLocalY = m.y - rect.top;
      setPan({
        x: pivotLocalX - pinchStart.pivotCanvasX * nextScale,
        y: pivotLocalY - pinchStart.pivotCanvasY * nextScale,
      });
      setScale(nextScale);
    };
    const onTouchEnd = (e: TouchEvent) => {
      if (e.touches.length < 2) pinchStart = null;
    };

    el.addEventListener("touchstart", onTouchStart, { passive: false });
    el.addEventListener("touchmove", onTouchMove, { passive: false });
    el.addEventListener("touchend", onTouchEnd);
    el.addEventListener("touchcancel", onTouchEnd);
    return () => {
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchmove", onTouchMove);
      el.removeEventListener("touchend", onTouchEnd);
      el.removeEventListener("touchcancel", onTouchEnd);
    };
  }, [pan, scale]);

  // ── Zoom keyboard shortcuts (+/− zoom, 0 reset) ───────────────────────────
  // Only mounts while the ciornă panel is open (CanvasSurface is unmounted
  // otherwise). Skipped when the user is typing in any input/textarea/button
  // or contentEditable surface — including the hidden cell-text input, so
  // typing "+", "-", "0" into a cell never zooms.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const active = document.activeElement as HTMLElement | null;
      if (active) {
        const tag = active.tagName;
        if (
          tag === "INPUT" ||
          tag === "TEXTAREA" ||
          tag === "BUTTON" ||
          active.isContentEditable
        ) {
          return;
        }
      }
      if (e.key === "+" || e.key === "=") {
        e.preventDefault();
        const p = viewportCenterPivot();
        zoomAt(p.x, p.y, scale + BUTTON_ZOOM_STEP);
      } else if (e.key === "-") {
        e.preventDefault();
        const p = viewportCenterPivot();
        zoomAt(p.x, p.y, scale - BUTTON_ZOOM_STEP);
      } else if (e.key === "0") {
        e.preventDefault();
        setScale(1);
        setPan({ x: 0, y: 0 });
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [scale, zoomAt]);

  // ── Toolbar handlers ──────────────────────────────────────────────────────
  const viewportCenterPivot = () => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
  };

  const onZoomIn = () => {
    const p = viewportCenterPivot();
    zoomAt(p.x, p.y, scale + BUTTON_ZOOM_STEP);
  };
  const onZoomOut = () => {
    const p = viewportCenterPivot();
    zoomAt(p.x, p.y, scale - BUTTON_ZOOM_STEP);
  };
  const onReset = () => {
    setScale(1);
    setPan({ x: 0, y: 0 });
  };
  const onFit = () => {
    const rect = canvasRef.current?.getBoundingClientRect();
    const inner = innerRef.current;
    if (!rect || !inner) {
      onReset();
      return;
    }
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    // Cards.
    const cardEls = inner.querySelectorAll<HTMLElement>("[data-card-id]");
    cardEls.forEach((el) => {
      const id = el.dataset.cardId;
      const card = cards.find((c) => c.id === id);
      if (!card) return;
      const w = el.offsetWidth;
      const h = el.offsetHeight;
      if (card.x < minX) minX = card.x;
      if (card.y < minY) minY = card.y;
      if (card.x + w > maxX) maxX = card.x + w;
      if (card.y + h > maxY) maxY = card.y + h;
    });
    // Filled cells.
    for (const key of cellText.keys()) {
      const [gxStr, gyStr] = key.split(",");
      const gx = Number(gxStr);
      const gy = Number(gyStr);
      const cx = gx * GRID_PX;
      const cy = gy * GRID_PX;
      if (cx < minX) minX = cx;
      if (cy < minY) minY = cy;
      if (cx + GRID_PX > maxX) maxX = cx + GRID_PX;
      if (cy + GRID_PX > maxY) maxY = cy + GRID_PX;
    }
    if (!isFinite(minX)) {
      onReset();
      return;
    }
    const bboxW = maxX - minX;
    const bboxH = maxY - minY;
    const availW = rect.width - FIT_PADDING_PX * 2;
    const availH = rect.height - FIT_PADDING_PX * 2;
    if (availW <= 0 || availH <= 0) {
      onReset();
      return;
    }
    const fitScale = clamp(
      Math.min(availW / bboxW, availH / bboxH),
      MIN_SCALE,
      MAX_SCALE,
    );
    const bboxCenterX = (minX + maxX) / 2;
    const bboxCenterY = (minY + maxY) / 2;
    setScale(fitScale);
    setPan({
      x: rect.width / 2 - bboxCenterX * fitScale,
      y: rect.height / 2 - bboxCenterY * fitScale,
    });
  };

  // ── Card mutators ─────────────────────────────────────────────────────────
  const addComponent = (componentId: string) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const centerCanvasX = (rect.width / 2 - pan.x) / scale;
    const centerCanvasY = (rect.height / 2 - pan.y) / scale;
    // Snap the origin to a whole cell, then stagger successive placements by
    // whole cells so cards don't stack exactly while staying grid-aligned.
    const offsetCells = placementCountRef.current % 5;
    placementCountRef.current += 1;
    const newCard: CanvasCardItem = {
      id: makeId("card"),
      componentId,
      x: snapToGrid(centerCanvasX) + offsetCells * GRID_PX,
      y: snapToGrid(centerCanvasY) + offsetCells * GRID_PX,
      // Default the column-arithmetic operation; ignored by future
      // components that don't carry an operation.
      operation: "addition",
    };
    setCards((prev) => [...prev, newCard]);
  };

  const moveCard = useCallback((id: string, x: number, y: number) => {
    setCards((prev) => prev.map((c) => (c.id === id ? { ...c, x, y } : c)));
  }, []);
  const closeCard = useCallback((id: string) => {
    setCards((prev) => prev.filter((c) => c.id !== id));
  }, []);
  // Cycle the operation of a column-arithmetic card in place: + → − → × → +.
  // Operands preserve; the scratch view's own effects clear answer state.
  const cycleCardOperation = useCallback((id: string) => {
    setCards((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, operation: nextOperation(c.operation ?? "addition") }
          : c,
      ),
    );
  }, []);

  // ── Render helpers ────────────────────────────────────────────────────────
  const renderedCards = useMemo(
    () =>
      cards
        .map((card) => {
          const reg = findComponent(card.componentId);
          if (!reg) return null;
          return (
            <CanvasCard
              key={card.id}
              id={card.id}
              label={reg.label}
              x={card.x}
              y={card.y}
              scale={scale}
              onMove={moveCard}
              onClose={closeCard}
            >
              {reg.render({
                operands: card.operands,
                operation: card.operation,
                onOperationChange: () => cycleCardOperation(card.id),
              })}
            </CanvasCard>
          );
        }),
    [cards, scale, moveCard, closeCard, cycleCardOperation],
  );

  const renderedCells = useMemo(
    () =>
      Array.from(cellText.entries()).map(([key, char]) => {
        const [gxStr, gyStr] = key.split(",");
        const gx = Number(gxStr);
        const gy = Number(gyStr);
        return (
          <span
            key={key}
            aria-hidden="true"
            className="pointer-events-none absolute flex items-center justify-center
              font-mono text-[18px] leading-none text-amber-950 select-none"
            style={{
              left: gx * GRID_PX,
              top: gy * GRID_PX,
              width: GRID_PX,
              height: GRID_PX,
            }}
          >
            {char}
          </span>
        );
      }),
    [cellText],
  );

  return (
    <div
      ref={canvasRef}
      className="relative h-full w-full overflow-hidden"
      style={{ touchAction: "none", backgroundColor: "#fffdf5" }}
      onPointerDown={onPanPointerDown}
      onPointerMove={onPanPointerMove}
      onPointerUp={onPanPointerUp}
      onPointerCancel={onPanPointerUp}
    >
      <div
        ref={innerRef}
        className="absolute left-0 top-0"
        style={{
          width: 1,
          height: 1,
          transformOrigin: "0 0",
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
        }}
      >
        {/* Notebook-paper backdrop. Origin + extent are whole multiples of
            GRID_PX so the gridlines fall exactly on canvas multiples of 32 —
            i.e. on the same boundaries cells, the cursor outline, and placed
            cards are positioned against. (A non-multiple origin like -5000
            shifts every line ~8px off the cells.) */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute"
          style={{
            left: -5120,
            top: -5120,
            width: 10240,
            height: 10240,
            backgroundImage:
              "linear-gradient(to right, rgba(96, 165, 250, 0.22) 1px, transparent 1px), " +
              "linear-gradient(to bottom, rgba(96, 165, 250, 0.22) 1px, transparent 1px)",
            backgroundSize: `${GRID_PX}px ${GRID_PX}px`,
            backgroundPosition: "0 0",
          }}
        />

        {/* Filled cell text — below cards so a placed card visually covers
            the writing underneath (paper-physics). */}
        {renderedCells}

        {/* Cursor outline. box-border + no rounding so the 2px outline sits
            dead-center in the 32px cell with its edges coincident with the
            gridlines (a rounded corner would nudge it off the cell). */}
        {focusedCell && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute box-border border-2 border-amber-400"
            style={{
              left: focusedCell.gx * GRID_PX,
              top: focusedCell.gy * GRID_PX,
              width: GRID_PX,
              height: GRID_PX,
            }}
          />
        )}

        {/* Hidden keyboard-capture input. Positioned imperatively at the
            focused cell so iOS can show the on-screen keyboard at a real
            on-screen target without scrolling. font-size 16px prevents
            iOS auto-zoom on focus. */}
        <input
          ref={hiddenInputRef}
          type="text"
          inputMode="text"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
          aria-label="Editare celulă"
          tabIndex={-1}
          className="pointer-events-none absolute opacity-0"
          style={{
            left: -10000,
            top: -10000,
            width: GRID_PX,
            height: GRID_PX,
            fontSize: 16,
            caretColor: "transparent",
            border: 0,
            padding: 0,
            background: "transparent",
          }}
          onFocus={onInputFocus}
          onBlur={onInputBlur}
          onKeyDown={onInputKeyDown}
          onInput={onInputInput}
        />

        {/* Cards on top of cells (cards visually obscure underlying writing). */}
        {renderedCards}
      </div>

      <CanvasToolbar
        scale={scale}
        onZoomIn={onZoomIn}
        onZoomOut={onZoomOut}
        onFit={onFit}
        onReset={onReset}
        onAddComponent={addComponent}
      />
    </div>
  );
}
