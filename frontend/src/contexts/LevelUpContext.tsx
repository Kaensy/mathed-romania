import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

const AUTO_DISMISS_MS = 3500;

interface LevelUpContextType {
  /** Currently-celebrating level, or null when no overlay is visible. */
  newLevel: number | null;
  /**
   * Trigger the level-up celebration. Mirrors XPNotificationContext's
   * notify shape — fire-and-forget; the provider handles auto-dismiss.
   */
  notifyLevelUp: (newLevel: number) => void;
  dismiss: () => void;
}

const LevelUpContext = createContext<LevelUpContextType | null>(null);

export function LevelUpProvider({ children }: { children: ReactNode }) {
  const [newLevel, setNewLevel] = useState<number | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dismiss = useCallback(() => {
    setNewLevel(null);
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const notifyLevelUp = useCallback(
    (level: number) => {
      if (typeof level !== "number" || level <= 0) return;
      // If a previous celebration is still on screen, replace it: the
      // most recent transition wins (e.g., multi-level jumps coalesce
      // when PetPanel passes the highest level).
      setNewLevel(level);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        setNewLevel(null);
        timerRef.current = null;
      }, AUTO_DISMISS_MS);
    },
    [],
  );

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const value = useMemo(
    () => ({ newLevel, notifyLevelUp, dismiss }),
    [newLevel, notifyLevelUp, dismiss],
  );

  return (
    <LevelUpContext.Provider value={value}>{children}</LevelUpContext.Provider>
  );
}

export function useLevelUp(): LevelUpContextType {
  const ctx = useContext(LevelUpContext);
  if (!ctx) {
    throw new Error("useLevelUp must be used within a LevelUpProvider");
  }
  return ctx;
}
