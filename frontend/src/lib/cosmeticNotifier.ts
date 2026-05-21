// Mirrors the badgeNotifier singleton-handler pattern: the axios
// interceptor calls `notifyCosmeticsUnlocked` with each request's
// `newly_unlocked_cosmetics`; the React provider registers itself via
// `setCosmeticHandler` on mount.
//
// Phase 5 sets up the pipeline only — the toast component lands in
// Phase 6. The hook still consumes this signal so the wardrobe state
// refreshes when new cosmetics arrive via any payload.
import type { CosmeticUnlock } from "@/types/cosmetics";

type Handler = (cosmetics: CosmeticUnlock[]) => void;

let currentHandler: Handler | null = null;

export function setCosmeticHandler(handler: Handler | null): void {
  currentHandler = handler;
}

export function notifyCosmeticsUnlocked(cosmetics: CosmeticUnlock[]): void {
  if (
    !currentHandler ||
    !Array.isArray(cosmetics) ||
    cosmetics.length === 0
  ) {
    return;
  }
  currentHandler(cosmetics);
}
