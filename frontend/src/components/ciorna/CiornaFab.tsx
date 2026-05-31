/**
 * Ciornă launcher — global FAB.
 *
 * Pill button anchored bottom-right. Default position is `bottom-20`, one
 * row above the Glossary FAB so the two stack cleanly where both are
 * visible. On routes that hide the Glossary FAB (test attempts, daily
 * test), drop to `bottom-4` so Ciornă doesn't float awkwardly in the
 * empty corner.
 *
 * Gated on authentication — no point opening a draft surface on the
 * login/register screens.
 */
import { NotebookPen } from "lucide-react";
import { useLocation } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useCiorna } from "@/contexts/CiornaContext";

// Mirrors the patterns in GlossaryFab.tsx — keep in sync if those change.
const GLOSSARY_HIDDEN_PATTERNS: RegExp[] = [
  /^\/test\/[^/]+/,
  /^\/daily(\/|$)/,
];

export default function CiornaFab() {
  const { isAuthenticated } = useAuth();
  const { isOpen, toggleCiorna } = useCiorna();
  const { pathname } = useLocation();

  if (!isAuthenticated) return null;

  const glossaryHidden = GLOSSARY_HIDDEN_PATTERNS.some((re) => re.test(pathname));
  const bottomCls = glossaryHidden ? "bottom-4" : "bottom-20";

  return (
    <button
      type="button"
      onClick={toggleCiorna}
      aria-label="Deschide ciorna"
      aria-expanded={isOpen}
      aria-haspopup="dialog"
      className={`fixed ${bottomCls} right-4 z-30 inline-flex min-h-[44px] items-center gap-2
        rounded-full px-4 py-2 text-sm font-medium text-white shadow-lg transition-colors
        focus:outline-none focus:ring-2 focus:ring-amber-300 focus:ring-offset-2
        ${isOpen ? "bg-amber-700 hover:bg-amber-800" : "bg-amber-600 hover:bg-amber-700"}`}
    >
      <NotebookPen className="h-4 w-4" aria-hidden="true" />
      <span>Ciornă</span>
    </button>
  );
}
