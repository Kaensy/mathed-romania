import { useEffect } from "react";
import { X } from "lucide-react";
import { GiPadlock } from "react-icons/gi";

import BadgeIcon from "./BadgeIcon";
import type { Badge } from "@/types/badges";

interface BadgeDetailModalProps {
  badge: Badge;
  onClose: () => void;
}

function formatBadgeDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("ro-RO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function BadgeDetailModal({ badge, onClose }: BadgeDetailModalProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const earned = badge.earned === true;
  const secretLocked = !earned && badge.secret;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md rounded-2xl bg-white p-8 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
          aria-label="Închide"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex flex-col items-center text-center pt-2">
          {secretLocked ? (
            <GiPadlock size={80} className="text-slate-400" aria-hidden />
          ) : (
            <BadgeIcon
              iconName={badge.icon_name}
              family={badge.family}
              size={80}
              muted={!earned}
            />
          )}

          {secretLocked ? (
            <>
              <h2 className="mt-4 text-xl font-bold text-gray-500 italic">
                Insignă secretă
              </h2>
              <p className="mt-3 text-sm text-gray-500 leading-relaxed">
                Continuă să explorezi platforma pentru a o descoperi.
              </p>
            </>
          ) : earned ? (
            <>
              <h2 className="mt-4 text-xl font-bold text-gray-900">
                {badge.name}
              </h2>
              {badge.description && (
                <p className="mt-3 text-sm text-gray-600 leading-relaxed">
                  {badge.description}
                </p>
              )}
              {badge.earned_at && (
                <p className="mt-4 text-xs text-gray-400">
                  Câștigată pe {formatBadgeDate(badge.earned_at)}
                </p>
              )}
            </>
          ) : (
            <>
              <h2 className="mt-4 text-xl font-bold text-gray-500">
                {badge.name}
              </h2>
              {badge.description && (
                <p className="mt-3 text-sm text-gray-600 leading-relaxed">
                  {badge.description}
                </p>
              )}
              <p className="mt-4 text-xs text-gray-400 italic">
                Nu este încă deblocată.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
