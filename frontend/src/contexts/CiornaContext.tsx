/**
 * Ciornă (draft paper) — global open/close state.
 *
 * Ephemeral by design: state is reset whenever the route changes, so the
 * draft surface always opens empty. No localStorage, no backend.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useLocation } from "react-router-dom";

interface CiornaContextType {
  isOpen: boolean;
  openCiorna: () => void;
  closeCiorna: () => void;
  toggleCiorna: () => void;
}

const CiornaContext = createContext<CiornaContextType | null>(null);

export function CiornaProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const { pathname } = useLocation();

  const openCiorna = useCallback(() => setIsOpen(true), []);
  const closeCiorna = useCallback(() => setIsOpen(false), []);
  const toggleCiorna = useCallback(() => setIsOpen((v) => !v), []);

  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  useEffect(() => {
    const w = window as unknown as {
      openCiorna?: () => void;
      closeCiorna?: () => void;
    };
    w.openCiorna = openCiorna;
    w.closeCiorna = closeCiorna;
    return () => {
      delete w.openCiorna;
      delete w.closeCiorna;
    };
  }, [openCiorna, closeCiorna]);

  const value = useMemo(
    () => ({ isOpen, openCiorna, closeCiorna, toggleCiorna }),
    [isOpen, openCiorna, closeCiorna, toggleCiorna],
  );

  return (
    <CiornaContext.Provider value={value}>{children}</CiornaContext.Provider>
  );
}

export function useCiorna(): CiornaContextType {
  const ctx = useContext(CiornaContext);
  if (!ctx) {
    throw new Error("useCiorna must be used within a CiornaProvider");
  }
  return ctx;
}
