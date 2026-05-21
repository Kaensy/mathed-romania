/**
 * Cosmetic-unlock toast — fixed app-root overlay, mirrors BadgeToast.
 *
 * Visible whenever `CosmeticNotificationContext.pendingCosmetics` is
 * non-empty. Each cosmetic shows as a small card with its visual,
 * display name, and a Romanian type label. Click anywhere on the
 * stack to dismiss every pending cosmetic (no auto-dismiss).
 *
 * Sits above the badge toast at `bottom-24` so the two can coexist
 * vertically when a single action grants both — e.g. a unit-test pass
 * that earns the `unit_1_complete` badge AND unlocks the
 * `frame_laurel` cosmetic.
 */
import { useCosmeticNotifications } from "@/contexts/CosmeticNotificationContext";
import type { CosmeticType } from "@/types/cosmetics";

import CosmeticVisual from "./CosmeticVisual";

const TYPE_LABEL: Record<CosmeticType, string> = {
  frame: "Ramă",
  profile_theme: "Temă",
  avatar: "Avatar",
};

const TYPE_BORDER: Record<CosmeticType, string> = {
  frame: "border-amber-300 bg-amber-50",
  profile_theme: "border-purple-300 bg-purple-50",
  avatar: "border-indigo-300 bg-indigo-50",
};

export default function CosmeticToast() {
  const { pendingCosmetics, clearAll } = useCosmeticNotifications();

  if (pendingCosmetics.length === 0) return null;

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={clearAll}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          clearAll();
        }
      }}
      // bottom-24 keeps us clear of BadgeToast (bottom-6) so both can
      // stack vertically when a single action surfaces both kinds.
      className="fixed bottom-24 left-1/2 z-[1000] -translate-x-1/2 cursor-pointer animate-badge-toast-in"
      aria-label="Închide notificările pentru cosmetice"
    >
      <div className="flex max-w-[90vw] gap-3 overflow-x-auto rounded-2xl bg-white/95 p-3 shadow-2xl ring-1 ring-slate-200 backdrop-blur">
        {pendingCosmetics.map((cosmetic) => (
          <div
            key={cosmetic.slug}
            className={`flex min-w-[13rem] items-center gap-3 rounded-xl border-2 px-3 py-2 ${
              TYPE_BORDER[cosmetic.type] ?? "border-slate-300 bg-slate-50"
            }`}
          >
            <div className="shrink-0">
              <CosmeticVisual
                type={cosmetic.type}
                assetRef={cosmetic.asset_ref}
                size="sm"
              />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                {TYPE_LABEL[cosmetic.type]} nouă
              </span>
              <span className="text-sm font-semibold text-slate-900 truncate">
                {cosmetic.display_name}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
