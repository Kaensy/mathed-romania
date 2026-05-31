/**
 * Ciornă adaptive container.
 *
 * Bottom sheet on narrow viewports (<md, Tailwind 768px breakpoint),
 * right-side panel on md+. The body is a CanvasSurface (Phase 3a) that
 * hosts free-positioned cards; the picker now lives inside the canvas's
 * "+" palette, so the container header stays minimal: title + close X.
 *
 * Dialog semantics: focus moves into the body content on open, Tab cycles
 * within the panel, Esc and backdrop click close. prefers-reduced-motion
 * users get a fade instead of the slide.
 *
 * Persistence: state is local to this component, so closing or navigating
 * unmounts the container and discards `cards` + canvas pan/zoom — matching
 * the ephemeral rule.
 */
import { useEffect, useRef } from "react";
import { X } from "lucide-react";

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

export default function CiornaContainer() {
  const { isOpen, closeCiorna } = useCiorna();
  const panelRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedRef = useRef<HTMLElement | null>(null);

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

  if (!isOpen) return null;

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
        className="absolute inset-x-0 bottom-0 flex h-[85vh] max-h-[85vh] flex-col
          rounded-t-2xl border-t border-amber-200 bg-white shadow-2xl
          animate-[ciornaSlideUp_220ms_ease-out] motion-reduce:animate-[ciornaFade_140ms_ease-out]
          md:inset-y-0 md:right-0 md:left-auto md:h-auto md:max-h-none md:w-[440px]
          md:rounded-none md:border-l md:border-t-0 md:border-amber-200
          md:animate-[ciornaSlideLeft_240ms_ease-out] md:motion-reduce:animate-[ciornaFade_140ms_ease-out]"
      >
        <header className="flex items-center gap-2 border-b border-amber-100 px-3 py-3">
          <h2
            id="ciorna-title"
            className="flex-1 px-1 text-base font-bold text-amber-900"
          >
            Ciornă
          </h2>
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
