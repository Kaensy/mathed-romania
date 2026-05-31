/**
 * CanvasCard — minimal-chrome frame around a placed ciornă component.
 *
 * Phase 3b refactor: the persistent title bar is gone. The card's only
 * resting chrome is its 2-px amber outline, which doubles as the drag
 * handle:
 *
 *   - The card root has 8 px of padding so the outline + the invisible
 *     ring inside it form an ~10 px hit zone for the drag. Hovering this
 *     zone shows the move cursor; pointerdown starts the drag.
 *   - Children fill the inner content area; their own pointer events go
 *     through untouched (cells stay clickable, inputs stay editable). The
 *     `target === currentTarget` guard on the root pointerdown ensures
 *     only clicks that land on the padding/border start the drag.
 *
 * The X close button sits at the top-right corner, invisible at rest and
 * fading in on hover or when the card holds focus (group-hover +
 * group-focus-within). It stops pointerdown propagation so clicking it
 * never starts a drag.
 *
 * Keyboard:
 *  - tabIndex=0 on the root. Delete + arrow nudges fire only when the
 *    event target IS the root, so internal cell editing keeps its keys.
 */
import { useCallback, type ReactNode } from "react";
import { X } from "lucide-react";

const NUDGE_STEP = 8;
const NUDGE_STEP_LARGE = 32;
const HIT_ZONE_PX = 8;

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

      const move = (ev: PointerEvent) => {
        const dx = (ev.clientX - startClientX) / scale;
        const dy = (ev.clientY - startClientY) / scale;
        onMove(id, startX + dx, startY + dy);
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
      };
      target.addEventListener("pointermove", move);
      target.addEventListener("pointerup", end);
      target.addEventListener("pointercancel", end);
    },
    [id, x, y, scale, onMove],
  );

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    // Only the outline / padding ring starts a drag — descendants (inputs,
    // close button, cells) keep their own pointer behavior.
    if (e.target !== e.currentTarget) return;
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
      className="group absolute cursor-move rounded-xl border-2 border-amber-300
        transition-[border-color,box-shadow]
        hover:border-amber-400
        focus-within:border-amber-500 focus-within:shadow-[0_2px_10px_-2px_rgba(180,83,9,0.25)]
        focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-1"
      style={{
        left: x,
        top: y,
        padding: HIT_ZONE_PX,
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
