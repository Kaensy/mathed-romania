import { useLocation } from "react-router-dom";
import { useGlossaryDrawer } from "@/contexts/GlossaryDrawerContext";

// Routes that represent an ACTIVE test/daily-test attempt — hide the FAB there
// so students can't open the glossary mid-attempt.
const HIDDEN_PATTERNS: RegExp[] = [
  /^\/test\/[^/]+/, // /test/:testId
  /^\/daily(\/|$)/, // /daily and any sub-path
];

export default function GlossaryFab() {
  const { pathname } = useLocation();
  const { openDrawer } = useGlossaryDrawer();

  if (HIDDEN_PATTERNS.some((re) => re.test(pathname))) return null;

  return (
    <button
      type="button"
      onClick={() => openDrawer()}
      className="fixed bottom-4 right-4 z-30 rounded-full bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
    >
      Glosar
    </button>
  );
}
