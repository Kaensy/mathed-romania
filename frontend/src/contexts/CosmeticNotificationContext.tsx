import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { setCosmeticHandler } from "@/lib/cosmeticNotifier";
import type { CosmeticUnlock } from "@/types/cosmetics";

/**
 * Cosmetic-unlock notification context.
 *
 * Phase 5 sets up the pipeline only — the toast component lands in
 * Phase 6. The reason the context exists already is that `useCosmetics`
 * watches `unlockVersion` to refetch when new cosmetics arrive via any
 * progress payload (exercise attempt, test finish, quest claim), so the
 * wardrobe modal reflects fresh ownership without a manual reload.
 *
 * Mirrors BadgeNotificationContext / XPNotificationContext exactly so
 * the three subsystems behave the same way at the call site.
 */
interface CosmeticNotificationContextType {
  /** Cosmetics surfaced by recent responses, in arrival order. */
  pendingCosmetics: CosmeticUnlock[];
  /**
   * Increments every time the axios interceptor forwards a non-empty
   * `newly_unlocked_cosmetics`. Subscribers (e.g. `useCosmetics`) watch
   * this counter in a useEffect to refetch derived state.
   */
  unlockVersion: number;
  pushCosmetics: (cosmetics: CosmeticUnlock[]) => void;
  clearAll: () => void;
}

const CosmeticNotificationContext =
  createContext<CosmeticNotificationContextType | null>(null);

export function CosmeticNotificationProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [pendingCosmetics, setPendingCosmetics] = useState<CosmeticUnlock[]>(
    [],
  );
  const [unlockVersion, setUnlockVersion] = useState(0);

  const pushCosmetics = useCallback((cosmetics: CosmeticUnlock[]) => {
    if (!Array.isArray(cosmetics) || cosmetics.length === 0) return;
    setPendingCosmetics((prev) => {
      const seen = new Set(prev.map((c) => c.slug));
      const additions = cosmetics.filter((c) => c && !seen.has(c.slug));
      return additions.length === 0 ? prev : [...prev, ...additions];
    });
    setUnlockVersion((v) => v + 1);
  }, []);

  const clearAll = useCallback(() => setPendingCosmetics([]), []);

  useEffect(() => {
    setCosmeticHandler(pushCosmetics);
    return () => setCosmeticHandler(null);
  }, [pushCosmetics]);

  const value = useMemo(
    () => ({ pendingCosmetics, unlockVersion, pushCosmetics, clearAll }),
    [pendingCosmetics, unlockVersion, pushCosmetics, clearAll],
  );

  return (
    <CosmeticNotificationContext.Provider value={value}>
      {children}
    </CosmeticNotificationContext.Provider>
  );
}

export function useCosmeticNotifications(): CosmeticNotificationContextType {
  const ctx = useContext(CosmeticNotificationContext);
  if (!ctx) {
    throw new Error(
      "useCosmeticNotifications must be used within a CosmeticNotificationProvider",
    );
  }
  return ctx;
}
