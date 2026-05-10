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

import { setXpHandler } from "@/lib/xpNotifier";

const AUTO_DISMISS_MS = 2500;

interface XPToastItem {
  id: number;
  amount: number;
}

interface XPNotificationContextType {
  /** Active transient toasts. Each auto-dismisses after AUTO_DISMISS_MS. */
  toasts: XPToastItem[];
  pushXp: (amount: number) => void;
  dismiss: (id: number) => void;
  /**
   * Increments every time XP is awarded. Subscribers (e.g. PetPanel) can
   * watch this counter in a useEffect to refetch derived state without
   * needing a manual page reload.
   */
  awardVersion: number;
}

const XPNotificationContext = createContext<XPNotificationContextType | null>(null);

export function XPNotificationProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<XPToastItem[]>([]);
  const [awardVersion, setAwardVersion] = useState(0);
  const idRef = useRef(0);
  const timersRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
  }, []);

  const pushXp = useCallback(
    (amount: number) => {
      if (typeof amount !== "number" || amount <= 0) return;

      // Collapse multiple grants from the same request into a single
      // pill: if a toast is still pending, fold the new amount into it
      // and reset its dismiss timer.
      setToasts((prev) => {
        const last = prev[prev.length - 1];
        if (last === undefined) {
          const id = ++idRef.current;
          const timer = setTimeout(() => dismiss(id), AUTO_DISMISS_MS);
          timersRef.current.set(id, timer);
          return [{ id, amount }];
        }
        const merged: XPToastItem = { id: last.id, amount: last.amount + amount };
        const oldTimer = timersRef.current.get(last.id);
        if (oldTimer) clearTimeout(oldTimer);
        const timer = setTimeout(() => dismiss(last.id), AUTO_DISMISS_MS);
        timersRef.current.set(last.id, timer);
        return [...prev.slice(0, -1), merged];
      });

      setAwardVersion((v) => v + 1);
    },
    [dismiss],
  );

  useEffect(() => {
    setXpHandler(pushXp);
    return () => setXpHandler(null);
  }, [pushXp]);

  // Best-effort cleanup if the provider unmounts while toasts are live.
  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
    };
  }, []);

  const value = useMemo(
    () => ({ toasts, pushXp, dismiss, awardVersion }),
    [toasts, pushXp, dismiss, awardVersion],
  );

  return (
    <XPNotificationContext.Provider value={value}>
      {children}
    </XPNotificationContext.Provider>
  );
}

export function useXpNotifications(): XPNotificationContextType {
  const ctx = useContext(XPNotificationContext);
  if (!ctx) {
    throw new Error(
      "useXpNotifications must be used within an XPNotificationProvider",
    );
  }
  return ctx;
}
