/**
 * CanvasToolbar — floating corner controls for the ciornă canvas.
 *
 * Holds the "+" add button (opens the picker palette), zoom +/−, fit, and
 * reset. The palette popover sits above the toolbar and closes on outside
 * click or Esc; the picker inside fires onSelect → add a card → palette
 * closes.
 *
 * All buttons are pointerdown-stoppropagation so a touch on a toolbar
 * control doesn't accidentally start a canvas pan.
 */
import { useEffect, useRef, useState } from "react";
import { Maximize2, Plus, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";

import CiornaPicker from "./CiornaPicker";

interface Props {
  scale: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
  onAddComponent: (componentId: string) => void;
}

const BTN_CLS =
  "flex h-9 w-9 items-center justify-center rounded-md border border-amber-200 " +
  "bg-white text-amber-900 shadow-sm transition-colors " +
  "hover:border-amber-300 hover:bg-amber-50 " +
  "focus:outline-none focus:ring-2 focus:ring-amber-300 " +
  "disabled:cursor-not-allowed disabled:opacity-50";

export default function CanvasToolbar({
  scale,
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
  onAddComponent,
}: Props) {
  const [paletteOpen, setPaletteOpen] = useState(false);
  const paletteRef = useRef<HTMLDivElement>(null);
  const addButtonRef = useRef<HTMLButtonElement>(null);

  // Outside click + Esc close the palette.
  useEffect(() => {
    if (!paletteOpen) return;
    const onPointerDown = (e: MouseEvent | TouchEvent) => {
      const t = e.target as Node;
      if (paletteRef.current?.contains(t)) return;
      if (addButtonRef.current?.contains(t)) return;
      setPaletteOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        setPaletteOpen(false);
        addButtonRef.current?.focus();
      }
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("touchstart", onPointerDown);
    document.addEventListener("keydown", onKey, true);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("touchstart", onPointerDown);
      document.removeEventListener("keydown", onKey, true);
    };
  }, [paletteOpen]);

  const pct = Math.round(scale * 100);

  // Prevent canvas pan when interacting with toolbar.
  const stop = (e: React.PointerEvent) => e.stopPropagation();

  return (
    <>
      <div
        className="absolute bottom-3 right-3 z-10 flex flex-col items-end gap-2"
        onPointerDown={stop}
      >
        <button
          ref={addButtonRef}
          type="button"
          onClick={() => setPaletteOpen((o) => !o)}
          aria-label="Adaugă componentă"
          aria-expanded={paletteOpen}
          aria-haspopup="dialog"
          className={BTN_CLS + " h-11 w-11 bg-amber-600 text-white hover:bg-amber-700 border-amber-700"}
        >
          <Plus className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="flex flex-col gap-1 rounded-md border border-amber-200 bg-white p-1 shadow-sm">
          <button
            type="button"
            onClick={onZoomIn}
            aria-label="Mărește"
            disabled={scale >= 2}
            className={BTN_CLS + " border-transparent shadow-none"}
          >
            <ZoomIn className="h-4 w-4" aria-hidden="true" />
          </button>
          <div className="text-center text-[10px] font-medium tabular-nums text-amber-900/70">
            {pct}%
          </div>
          <button
            type="button"
            onClick={onZoomOut}
            aria-label="Micșorează"
            disabled={scale <= 0.25}
            className={BTN_CLS + " border-transparent shadow-none"}
          >
            <ZoomOut className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={onFit}
            aria-label="Încadrează în vizor"
            className={BTN_CLS + " border-transparent shadow-none"}
          >
            <Maximize2 className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={onReset}
            aria-label="Resetează vizorul"
            className={BTN_CLS + " border-transparent shadow-none"}
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      {paletteOpen && (
        <div
          ref={paletteRef}
          role="dialog"
          aria-label="Adaugă componentă"
          className="absolute bottom-3 right-16 z-20 w-[280px] max-w-[calc(100%-5rem)]
            max-h-[80%] overflow-y-auto rounded-xl border border-amber-200
            bg-white p-3 shadow-xl"
          onPointerDown={stop}
        >
          <CiornaPicker
            onSelect={(id) => {
              onAddComponent(id);
              setPaletteOpen(false);
            }}
          />
        </div>
      )}
    </>
  );
}
