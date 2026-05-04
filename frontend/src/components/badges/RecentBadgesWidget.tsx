import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trophy } from "lucide-react";

import api from "@/api/client";
import { useBadgeNotifications } from "@/contexts/BadgeNotificationContext";
import BadgeIcon from "./BadgeIcon";
import type { AchievementListResponse, Badge } from "@/types/badges";

export default function RecentBadgesWidget() {
  const [recent, setRecent] = useState<Badge[]>([]);
  const { pendingBadges } = useBadgeNotifications();

  useEffect(() => {
    api
      .get<AchievementListResponse>("/progress/achievements/")
      .then((res) => {
        const earned = res.data.achievements.filter((b) => b.earned);
        earned.sort((a, b) => {
          const ta = a.earned_at ? new Date(a.earned_at).getTime() : 0;
          const tb = b.earned_at ? new Date(b.earned_at).getTime() : 0;
          return tb - ta;
        });
        setRecent(earned.slice(0, 4));
      })
      .catch(() => {/* non-fatal — hide widget */});
  }, [pendingBadges.length]);

  if (recent.length === 0) return null;

  return (
    <section className="mt-8">
      <Link to="/profile" className="block group">
        <div className="flex items-center gap-2 mb-3">
          <Trophy className="w-5 h-5 text-indigo-500" />
          <h3 className="text-base font-semibold text-gray-700 group-hover:text-indigo-700 transition-colors">
            Insigne recente
          </h3>
        </div>
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
          {recent.map((badge) => (
            <div
              key={badge.key}
              className="rounded-xl border bg-white p-4 flex flex-col items-center gap-2 group-hover:border-indigo-300 group-hover:shadow-sm transition-all"
            >
              <BadgeIcon
                iconName={badge.icon_name}
                family={badge.family}
                size={40}
              />
              <span className="text-xs font-medium text-gray-700 text-center line-clamp-2">
                {badge.name ?? "Insignă"}
              </span>
            </div>
          ))}
        </div>
      </Link>
    </section>
  );
}
