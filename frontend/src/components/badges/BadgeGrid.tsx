import { useEffect, useState } from "react";
import { Trophy } from "lucide-react";
import { GiPadlock } from "react-icons/gi";

import api from "@/api/client";
import { useBadgeNotifications } from "@/contexts/BadgeNotificationContext";
import BadgeIcon from "./BadgeIcon";
import BadgeDetailModal from "./BadgeDetailModal";
import type { AchievementListResponse, Badge } from "@/types/badges";

export default function BadgeGrid() {
  const [badges, setBadges] = useState<Badge[] | null>(null);
  const [selected, setSelected] = useState<Badge | null>(null);
  const { pendingBadges } = useBadgeNotifications();

  useEffect(() => {
    api
      .get<AchievementListResponse>("/progress/achievements/")
      .then((res) => {
        const sorted = [...res.data.achievements].sort((a, b) => {
          const aEarned = a.earned === true;
          const bEarned = b.earned === true;
          if (aEarned && bEarned) {
            const ta = a.earned_at ? new Date(a.earned_at).getTime() : 0;
            const tb = b.earned_at ? new Date(b.earned_at).getTime() : 0;
            return tb - ta;
          }
          if (aEarned) return -1;
          if (bEarned) return 1;
          return 0;
        });
        setBadges(sorted);
      })
      .catch(() => setBadges([]));
  }, [pendingBadges.length]);

  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <Trophy className="w-5 h-5 text-indigo-500" />
        <h3 className="text-sm font-semibold text-gray-600">Insigne</h3>
      </div>

      {badges === null ? (
        <BadgeGridSkeleton />
      ) : (
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {badges.map((badge) => (
            <BadgeCard
              key={badge.key}
              badge={badge}
              onClick={() => setSelected(badge)}
            />
          ))}
        </div>
      )}

      {selected && (
        <BadgeDetailModal badge={selected} onClose={() => setSelected(null)} />
      )}
    </section>
  );
}

function BadgeCard({ badge, onClick }: { badge: Badge; onClick: () => void }) {
  const earned = badge.earned === true;
  const secretLocked = !earned && badge.secret;

  const ringByFamily: Record<Badge["family"], string> = {
    progress: "hover:ring-indigo-200",
    mastery: "hover:ring-amber-200",
    consistency: "hover:ring-orange-200",
    discovery: "hover:ring-teal-200",
  };

  const baseClasses =
    "rounded-xl border bg-white p-4 flex flex-col items-center gap-2 transition-all hover:shadow-sm hover:ring-2";
  const stateClasses = earned
    ? `${ringByFamily[badge.family]}`
    : "opacity-70 hover:ring-slate-200";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${baseClasses} ${stateClasses}`}
    >
      {secretLocked ? (
        <GiPadlock size={40} className="text-slate-400" aria-hidden />
      ) : (
        <BadgeIcon
          iconName={badge.icon_name}
          family={badge.family}
          size={40}
          muted={!earned}
        />
      )}
      {secretLocked ? (
        <span className="text-xs italic text-gray-400 text-center line-clamp-2">
          ???
        </span>
      ) : (
        <span
          className={`text-xs text-center line-clamp-2 ${
            earned ? "font-semibold text-gray-900" : "font-medium text-gray-500"
          }`}
        >
          {badge.name}
        </span>
      )}
    </button>
  );
}

function BadgeGridSkeleton() {
  return (
    <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="rounded-xl border bg-white p-4 flex flex-col items-center gap-2 animate-pulse"
        >
          <div className="h-10 w-10 rounded-full bg-gray-200" />
          <div className="h-3 w-20 bg-gray-100 rounded" />
        </div>
      ))}
    </div>
  );
}
