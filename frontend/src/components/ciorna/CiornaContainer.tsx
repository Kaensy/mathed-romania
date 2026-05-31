/**
 * Ciornă adaptive container.
 *
 * Two desktop layouts, one mobile layout:
 *
 *   - Mobile (<md): bottom sheet. Always docked — no pop-out.
 *   - Desktop docked (default): right-side panel.
 *   - Desktop popped: a free-floating window detached from the edge —
 *     draggable by its header, resizable from the bottom-right corner, kept
 *     within sane min/max bounds. The header's pop-out toggle flips between
 *     docked and popped; toggling back re-docks.
 *
 * Dialog semantics are preserved in every state: focus moves into the body on
 * open, Tab cycles within the panel, Esc and backdrop click close.
 * prefers-reduced-motion users get a fade instead of the slide.
 *
 * Persistence: state is local to this component, so closing or navigating
 * unmounts the container and discards `cards` + canvas pan/zoom — matching
 * the ephemeral rule. The popped window's position/size are equally ephemeral.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { Maximize2, Minimize2, X } from "lucide-react";

import { useCiorna } from "@/contexts/CiornaContext";

import CanvasSurface from "./CanvasSurface";

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "textarea:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

const DESKTOP_QUERY = "(min-width: 768px)";

// Free-floating window bounds.
const MIN_W = 340;
const MIN_H = 320;
const MARGIN = 24; // keep at least this much viewport breathing room

interface WinRect {
  x: number;
  y: number;
  w: number;
  h: number;
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}

export default function CiornaContainer() {
  const { isOpen, closeCiorna } = useCiorna();
  const panelRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedRef = useRef<HTMLElement | null>(null);

  // Desktop vs mobile — pop-out only exists on desktop.
  const [isDesktop, setIsDesktop] = useState<boolean>(() =>
    typeof window !== "undefined"
      ? window.matchMedia(DESKTOP_QUERY).matches
      : true,
  );
  const [isPopped, setIsPopped] = useState(false);
  const [rect, setRect] = useState<WinRect>({ x: 0, y: 0, w: 520, h: 640 });

  // `popped` is derived: a mobile viewport always renders the docked sheet
  // regardless of the toggle's last state.
  const popped = isPopped && isDesktop;

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia(DESKTOP_QUERY);
    const handler = () => setIsDesktop(mq.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  // Reset to docked each time the panel opens, so it always opens in the
  // default layout.
  useEffect(() => {
    if (!isOpen) setIsPopped(false);
  }, [isOpen]);

  // ── Focus trap + Esc + (effective in both layouts) ──────────────────────
  useEffect(() => {
    if (!isOpen) return;

    previouslyFocusedRef.current =
      (document.activeElement as HTMLElement | null) ?? null;

    const panel = panelRef.current;
    const focusables = () =>
      panel
        ? Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
        : [];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        closeCiorna();
        return;
      }
      if (e.key !== "Tab") return;
      const items = focusables();
      if (items.length === 0) {
        e.preventDefault();
        panel?.focus();
        return;
      }
      const first = items[0]!;
      const last = items[items.length - 1]!;
      const active = document.activeElement as HTMLElement | null;
      if (e.shiftKey) {
        if (active === first || !panel?.contains(active)) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (active === last || !panel?.contains(active)) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      previouslyFocusedRef.current?.focus?.();
    };
  }, [isOpen, closeCiorna]);

  // ── Pop-out toggle ───────────────────────────────────────────────────────
  const popOut = useCallback(() => {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const w = clamp(520, MIN_W, vw - MARGIN * 2);
    const h = clamp(640, MIN_H, vh - MARGIN * 2);
    setRect({
      x: Math.round((vw - w) / 2),
      y: Math.round((vh - h) / 2),
      w,
      h,
    });
    setIsPopped(true);
  }, []);
  const dock = useCallback(() => setIsPopped(false), []);

  // ── Window drag (by header) ────────────────────────────────────────────
  const onHeaderPointerDown = (e: React.PointerEvent<HTMLElement>) => {
    if (!popped) return;
    // Buttons inside the header keep their own behavior.
    if ((e.target as HTMLElement).closest("button")) return;
    e.preventDefault();
    const startX = e.clientX;
    const startY = e.clientY;
    const { x: origX, y: origY, w, h } = rect;
    const el = e.currentTarget;
    el.setPointerCapture(e.pointerId);
    const move = (ev: PointerEvent) => {
      const maxX = Math.max(0, window.innerWidth - w);
      const maxY = Math.max(0, window.innerHeight - h);
      setRect((r) => ({
        ...r,
        x: clamp(origX + (ev.clientX - startX), 0, maxX),
        y: clamp(origY + (ev.clientY - startY), 0, maxY),
      }));
    };
    const end = (ev: PointerEvent) => {
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", end);
      el.removeEventListener("pointercancel", end);
      try {
        el.releasePointerCapture(ev.pointerId);
      } catch {
        // already released
      }
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", end);
    el.addEventListener("pointercancel", end);
  };

  // ── Window resize (bottom-right corner) ──────────────────────────────────
  const onResizePointerDown = (e: React.PointerEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const { w: origW, h: origH, x, y } = rect;
    const el = e.currentTarget;
    el.setPointerCapture(e.pointerId);
    const move = (ev: PointerEvent) => {
      const maxW = window.innerWidth - x - MARGIN;
      const maxH = window.innerHeight - y - MARGIN;
      setRect((r) => ({
        ...r,
        w: clamp(origW + (ev.clientX - startX), MIN_W, Math.max(MIN_W, maxW)),
        h: clamp(origH + (ev.clientY - startY), MIN_H, Math.max(MIN_H, maxH)),
      }));
    };
    const end = (ev: PointerEvent) => {
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", end);
      el.removeEventListener("pointercancel", end);
      try {
        el.releasePointerCapture(ev.pointerId);
      } catch {
        // already released
      }
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", end);
    el.addEventListener("pointercancel", end);
  };

  if (!isOpen) return null;

  const dockedPanelCls =
    "absolute inset-x-0 bottom-0 flex h-[85vh] max-h-[85vh] flex-col " +
    "rounded-t-2xl border-t border-amber-200 bg-white shadow-2xl " +
    "animate-[ciornaSlideUp_220ms_ease-out] motion-reduce:animate-[ciornaFade_140ms_ease-out] " +
    "md:inset-y-0 md:right-0 md:left-auto md:h-auto md:max-h-none md:w-[440px] " +
    "md:rounded-none md:border-l md:border-t-0 md:border-amber-200 " +
    "md:animate-[ciornaSlideLeft_240ms_ease-out] md:motion-reduce:animate-[ciornaFade_140ms_ease-out]";

  const poppedPanelCls =
    "fixed flex flex-col overflow-hidden rounded-2xl border border-amber-200 " +
    "bg-white shadow-2xl animate-[ciornaFade_140ms_ease-out]";

  return (
    <div className="fixed inset-0 z-40">
      <div
        className="absolute inset-0 bg-transparent transition-opacity md:bg-slate-900/30"
        onClick={closeCiorna}
        aria-hidden="true"
      />

      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="ciorna-title"
        tabIndex={-1}
        className={popped ? poppedPanelCls : dockedPanelCls}
        style={
          popped
            ? { left: rect.x, top: rect.y, width: rect.w, height: rect.h }
            : undefined
        }
      >
        <header
          onPointerDown={onHeaderPointerDown}
          className={
            "flex items-center gap-2 border-b border-amber-100 px-3 py-3" +
            (popped ? " cursor-move select-none" : "")
          }
        >
          <h2
            id="ciorna-title"
            className="flex-1 px-1 text-base font-bold text-amber-900"
          >
            Ciornă
          </h2>

          {/* Pop-out / dock toggle — desktop only. */}
          {isDesktop && (
            <button
              type="button"
              onClick={popped ? dock : popOut}
              className="rounded p-1 text-gray-500 transition-colors
                hover:bg-amber-50 hover:text-amber-900
                focus:outline-none focus:ring-2 focus:ring-amber-300"
              aria-label={popped ? "Andochează ciorna" : "Desprinde ciorna"}
              title={popped ? "Andochează" : "Desprinde"}
            >
              {popped ? (
                <Minimize2 className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Maximize2 className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          )}

          <button
            type="button"
            onClick={closeCiorna}
            className="rounded p-1 text-gray-500 transition-colors
              hover:bg-amber-50 hover:text-amber-900
              focus:outline-none focus:ring-2 focus:ring-amber-300"
            aria-label="Închide ciorna"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </header>

        <div className="flex-1 overflow-hidden">
          <CanvasSurface />
        </div>

        {/* Resize handle — popped only, bottom-right corner. */}
        {popped && (
          <div
            onPointerDown={onResizePointerDown}
            role="separator"
            aria-label="Redimensionează fereastra"
            className="absolute bottom-0 right-0 h-4 w-4 cursor-nwse-resize"
            style={{
              background:
                "linear-gradient(135deg, transparent 50%, rgba(180,83,9,0.45) 50%)",
            }}
          />
        )}
      </div>

      <style>{`
        @keyframes ciornaSlideUp {
          from { transform: translateY(100%); }
          to   { transform: translateY(0); }
        }
        @keyframes ciornaSlideLeft {
          from { transform: translateX(100%); }
          to   { transform: translateX(0); }
        }
        @keyframes ciornaFade {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
