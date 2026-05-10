import { Sparkles } from "lucide-react";

import { useXpNotifications } from "@/contexts/XPNotificationContext";

/**
 * Floating "+N XP" pill. Stacks alongside the badge toast; when both
 * fire on the same request the badge toast sits centered (bottom-6)
 * and this pill sits one row above it (bottom-24) so they don't
 * overlap. Multiple grants from the same request collapse into a
 * single pill via XPNotificationContext.
 */
export default function XPToast() {
  const { toasts, dismiss } = useXpNotifications();

  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed bottom-24 left-1/2 z-[1000] -translate-x-1/2 flex flex-col items-center gap-2">
      {toasts.map((toast) => (
        <button
          key={toast.id}
          type="button"
          onClick={() => dismiss(toast.id)}
          className="pointer-events-auto inline-flex items-center gap-2 rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-lg ring-1 ring-amber-600/30 animate-xp-toast-in hover:bg-amber-600 transition-colors"
          aria-label={`+${toast.amount} XP`}
        >
          <Sparkles className="h-4 w-4" aria-hidden />
          <span>+{toast.amount} XP</span>
        </button>
      ))}
    </div>
  );
}
