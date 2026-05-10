// Mirrors the badgeNotifier singleton-handler pattern: the axios
// interceptor calls `notifyXpGained` with the request's xp_gained;
// the React provider registers itself via `setXpHandler` on mount.

type Handler = (amount: number) => void;

let currentHandler: Handler | null = null;

export function setXpHandler(handler: Handler | null): void {
  currentHandler = handler;
}

export function notifyXpGained(amount: number): void {
  if (!currentHandler || typeof amount !== "number" || amount <= 0) return;
  currentHandler(amount);
}
