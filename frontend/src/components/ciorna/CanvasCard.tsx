/**
 * CanvasCard — minimal-chrome frame around a placed ciornă component.
 *
 * The card has NO border and NO padding: its component cells sit directly on
 * the paper gridlines with zero inset. A "movable" frame is drawn only on
 * hover / focus via `outline` — a non-layout property rendered outside the
 * cells, so it never displaces the cell grid and never doubles up with a
 * border.
 *
 * Drag handle = any non-interactive region. A pointerdown that does NOT land
 * on an interactive descendant (input / button / link / contenteditable)
 * starts a drag: the separator bar, display digits, spacers, and the empty
 * area beneath the operator all move the card. Interactive elements
 * (result-input cells, the cycling sign button, the close button) keep their
 * own behavior and never initiate a drag.
 *
 *   - During the drag the card tracks the cursor 1:1 at any zoom (delta is
 *     divided by `scale` to convert screen px → canvas px). On drop the
 *     origin snaps to the nearest whole cell.
 *
 * The X close button sits at the top-right corner, invisible at rest and
 * fading in on hover or when the card holds focus. It stops pointerdown
 * propagation so clicking it never starts a drag.
 *
 * Keyboard:
 *  - tabIndex=0 on the root. Delete + arrow nudges fire only when the
 *    event target IS the root, so internal cell editing keeps its keys.
 *    Arrows step one whole cell (Shift = 5 cells); the origin stays
 *    grid-aligned because placement + drop both snap to the grid.
 */
import { useCallback, type ReactNode } from "react";
import { X } from "lucide-react";

// Paper cell size — must match GRID_PX in CanvasSurface so snapping lands on
// the same grid the cards are positioned against.
const GRID_PX = 32;
const NUDGE_STEP = GRID_PX;          // one cell
const NUDGE_STEP_LARGE = GRID_PX * 5; // power-user jump, still grid-aligned

const snapToGrid = (v: number) => Math.round(v / GRID_PX) * GRID_PX;

interface Props {
  id: string;
  label: string;
  x: number;
  y: number;
  scale: number;
  onMove: (id: string, x: number, y: number) => void;
  onClose: (id: string) => void;
  children: ReactNode;
}

export default function CanvasCard({
  id,
  label,
  x,
  y,
  scale,
  onMove,
  onClose,
  children,
}: Props) {
  const startDrag = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      if (e.button !== 0 && e.pointerType !== "touch") return;
      e.stopPropagation();
      const startClientX = e.clientX;
      const startClientY = e.clientY;
      const startX = x;
      const startY = y;
      const target = e.currentTarget;
      target.setPointerCapture(e.pointerId);

      // Track the latest free (un-snapped) position so the drag follows the
      // cursor 1:1; we snap to the nearest cell only on drop.
      let lastX = startX;
      let lastY = startY;
      const move = (ev: PointerEvent) => {
        const dx = (ev.clientX - startClientX) / scale;
        const dy = (ev.clientY - startClientY) / scale;
        lastX = startX + dx;
        lastY = startY + dy;
        onMove(id, lastX, lastY);
      };
      const end = (ev: PointerEvent) => {
        target.removeEventListener("pointermove", move);
        target.removeEventListener("pointerup", end);
        target.removeEventListener("pointercancel", end);
        try {
          target.releasePointerCapture(ev.pointerId);
        } catch {
          // already released; ignore
        }
        // Snap the origin to the nearest whole cell.
        onMove(id, snapToGrid(lastX), snapToGrid(lastY));
      };
      target.addEventListener("pointermove", move);
      target.addEventListener("pointerup", end);
      target.addEventListener("pointercancel", end);
    },
    [id, x, y, scale, onMove],
  );

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    // Drag from any NON-interactive region. Interactive descendants
    // (result-input cells, the cycling sign button, the close button, links,
    // contenteditable) keep their own pointer behavior and never drag.
    const t = e.target as HTMLElement;
    if (t.closest('input, textarea, select, button, a, [contenteditable="true"]')) {
      return;
    }
    startDrag(e);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.target !== e.currentTarget) return;
    if (e.key === "Delete" || e.key === "Backspace") {
      e.preventDefault();
      onClose(id);
      return;
    }
    const step = e.shiftKey ? NUDGE_STEP_LARGE : NUDGE_STEP;
    let nx = x;
    let ny = y;
    switch (e.key) {
      case "ArrowLeft":
        nx -= step;
        break;
      case "ArrowRight":
        nx += step;
        break;
      case "ArrowUp":
        ny -= step;
        break;
      case "ArrowDown":
        ny += step;
        break;
      default:
        return;
    }
    e.preventDefault();
    onMove(id, nx, ny);
  };

  return (
    <div
      role="group"
      aria-label={`Componentă ${label}`}
      tabIndex={0}
      data-card-id={id}
      onPointerDown={onPointerDown}
      onKeyDown={onKeyDown}
      className="group absolute cursor-move
        outline outline-2 outline-offset-0 outline-transparent
        transition-[outline-color]
        hover:outline-amber-400/70
        focus-within:outline-amber-500
        focus:outline-amber-500"
      style={{
        left: x,
        top: y,
        touchAction: "none",
      }}
    >
      {children}

      <button
        type="button"
        onPointerDown={(e) => e.stopPropagation()}
        onClick={(e) => {
          e.stopPropagation();
          onClose(id);
        }}
        aria-label={`Închide ${label}`}
        className="absolute -right-2 -top-2 rounded-full border border-amber-300
          bg-white p-0.5 text-amber-700 shadow-sm
          opacity-0 pointer-events-none transition-opacity duration-150
          group-hover:opacity-100 group-hover:pointer-events-auto
          group-focus-within:opacity-100 group-focus-within:pointer-events-auto
          focus:opacity-100 focus:pointer-events-auto focus:outline-none
          focus:ring-2 focus:ring-amber-300"
      >
        <X className="h-3 w-3" aria-hidden="true" />
      </button>
    </div>
  );
}
