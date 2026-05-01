import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

interface GlossaryDrawerContextType {
  isOpen: boolean;
  focusedTermId: number | null;
  openDrawer: (termId?: number) => void;
  closeDrawer: () => void;
}

const GlossaryDrawerContext = createContext<GlossaryDrawerContextType | null>(null);

export function GlossaryDrawerProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedTermId, setFocusedTermId] = useState<number | null>(null);

  const openDrawer = useCallback((termId?: number) => {
    setFocusedTermId(typeof termId === "number" ? termId : null);
    setIsOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsOpen(false);
    setFocusedTermId(null);
  }, []);

  // Dev convenience: openDrawer(N) from the browser console.
  useEffect(() => {
    const w = window as unknown as {
      openDrawer?: (id?: number) => void;
      closeDrawer?: () => void;
    };
    w.openDrawer = openDrawer;
    w.closeDrawer = closeDrawer;
    return () => {
      delete w.openDrawer;
      delete w.closeDrawer;
    };
  }, [openDrawer, closeDrawer]);

  const value = useMemo(
    () => ({ isOpen, focusedTermId, openDrawer, closeDrawer }),
    [isOpen, focusedTermId, openDrawer, closeDrawer],
  );

  return (
    <GlossaryDrawerContext.Provider value={value}>
      {children}
    </GlossaryDrawerContext.Provider>
  );
}

export function useGlossaryDrawer(): GlossaryDrawerContextType {
  const ctx = useContext(GlossaryDrawerContext);
  if (!ctx) {
    throw new Error(
      "useGlossaryDrawer must be used within a GlossaryDrawerProvider",
    );
  }
  return ctx;
}
