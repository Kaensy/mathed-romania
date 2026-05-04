import type { Badge } from "@/types/badges";

type Handler = (badges: Badge[]) => void;

let currentHandler: Handler | null = null;

export function setBadgeHandler(handler: Handler | null): void {
  currentHandler = handler;
}

export function notifyBadges(badges: Badge[]): void {
  if (!currentHandler || !Array.isArray(badges) || badges.length === 0) return;
  currentHandler(badges);
}
