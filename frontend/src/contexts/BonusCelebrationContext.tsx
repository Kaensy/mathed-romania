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

/**
 * Bonus-celebration context — the Block 10 LevelUpContext treatment,
 * reused for the daily 100-point milestone finale. Fire-and-forget;
 * the provider owns auto-dismiss. Only the 100 rung celebrates; the
 * smaller rungs keep just the subtle XP toast.
 */
const AUTO_DISMISS_MS = 3500;

interface BonusCelebrationContextType {
  /** True while the finale overlay is on screen. */
  celebrating: boolean;
  notifyBonus: () => void;
  dismiss: () => void;
}

const BonusCelebrationContext =
  createContext<BonusCelebrationContextType | null>(null);

export function BonusCelebrationProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [celebrating, setCelebrating] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dismiss = useCallback(() => {
    setCelebrating(false);
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const notifyBonus = useCallback(() => {
    setCelebrating(true);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      setCelebrating(false);
      timerRef.current = null;
    }, AUTO_DISMISS_MS);
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const value = useMemo(
    () => ({ celebrating, notifyBonus, dismiss }),
    [celebrating, notifyBonus, dismiss],
  );

  return (
    <BonusCelebrationContext.Provider value={value}>
      {children}
    </BonusCelebrationContext.Provider>
  );
}

export function useBonusCelebration(): BonusCelebrationContextType {
  const ctx = useContext(BonusCelebrationContext);
  if (!ctx) {
    throw new Error(
      "useBonusCelebration must be used within a BonusCelebrationProvider",
    );
  }
  return ctx;
}
