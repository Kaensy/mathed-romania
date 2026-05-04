import { useBadgeNotifications } from "@/contexts/BadgeNotificationContext";
import BadgeIcon from "./BadgeIcon";

const FAMILY_BORDER: Record<string, string> = {
  progress: "border-indigo-300 bg-indigo-50",
  mastery: "border-amber-300 bg-amber-50",
  consistency: "border-orange-300 bg-orange-50",
  discovery: "border-teal-300 bg-teal-50",
};

export default function BadgeToast() {
  const { pendingBadges, clearAll } = useBadgeNotifications();

  if (pendingBadges.length === 0) return null;

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
      className="fixed bottom-6 left-1/2 z-[1000] -translate-x-1/2 cursor-pointer animate-badge-toast-in"
      aria-label="Închide notificările pentru insigne"
    >
      <div className="flex max-w-[90vw] gap-3 overflow-x-auto rounded-2xl bg-white/95 p-3 shadow-2xl ring-1 ring-slate-200 backdrop-blur">
        {pendingBadges.map((badge) => (
          <div
            key={badge.key}
            className={`flex min-w-[12rem] items-center gap-3 rounded-xl border-2 px-3 py-2 ${
              FAMILY_BORDER[badge.family] ?? "border-slate-300 bg-slate-50"
            }`}
          >
            <BadgeIcon
              iconName={badge.icon_name}
              family={badge.family}
              size={36}
            />
            <div className="flex flex-col">
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Insignă nouă
              </span>
              <span className="text-sm font-semibold text-slate-900">
                {badge.name ?? "Insignă misterioasă"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
