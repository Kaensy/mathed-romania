import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { setBadgeHandler } from "@/lib/badgeNotifier";
import type { Badge } from "@/types/badges";

interface BadgeNotificationContextType {
  pendingBadges: Badge[];
  pushBadges: (badges: Badge[]) => void;
  clearAll: () => void;
}

const BadgeNotificationContext = createContext<BadgeNotificationContextType | null>(null);

export function BadgeNotificationProvider({ children }: { children: ReactNode }) {
  const [pendingBadges, setPendingBadges] = useState<Badge[]>([]);

  const pushBadges = useCallback((badges: Badge[]) => {
    if (!Array.isArray(badges) || badges.length === 0) return;
    setPendingBadges((prev) => {
      const seen = new Set(prev.map((b) => b.key));
      const additions = badges.filter((b) => b && !seen.has(b.key));
      return additions.length === 0 ? prev : [...prev, ...additions];
    });
  }, []);

  const clearAll = useCallback(() => setPendingBadges([]), []);

  useEffect(() => {
    setBadgeHandler(pushBadges);
    return () => setBadgeHandler(null);
  }, [pushBadges]);

  const value = useMemo(
    () => ({ pendingBadges, pushBadges, clearAll }),
    [pendingBadges, pushBadges, clearAll],
  );

  return (
    <BadgeNotificationContext.Provider value={value}>
      {children}
    </BadgeNotificationContext.Provider>
  );
}

export function useBadgeNotifications(): BadgeNotificationContextType {
  const ctx = useContext(BadgeNotificationContext);
  if (!ctx) {
    throw new Error(
      "useBadgeNotifications must be used within a BadgeNotificationProvider",
    );
  }
  return ctx;
}
