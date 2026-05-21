import { Sparkles } from "lucide-react";
import type { StudentProfile } from "@/types/auth";

/**
 * Lifetime account-level widget, paired above PetPanel on /profile.
 * Account level is derived from StudentProfile.total_xp on the backend
 * (same curve as Pet, K=50) — this component just renders the fields.
 */
export default function AccountLevelPanel({
  profile,
}: {
  profile: StudentProfile;
}) {
  const fillPct = computeBarFillPct(profile);

  return (
    <section className="mt-8">
      <div className="block w-full rounded-xl border bg-white p-5">
        <div className="flex items-center gap-4">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
            <Sparkles className="h-10 w-10" strokeWidth={1.75} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline justify-between gap-3">
              <h3 className="text-lg font-semibold text-slate-900 truncate">
                Nivel cont
              </h3>
              <span className="shrink-0 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
                Nivel {profile.account_level}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-500">
              Progresul tău general
            </p>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-indigo-500 transition-all duration-500"
                style={{ width: `${fillPct}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-slate-400">
              {profile.xp_to_next_level} XP până la nivelul{" "}
              {profile.account_level + 1} · Total:{" "}
              {profile.total_xp.toLocaleString("ro-RO")} XP
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function computeBarFillPct(profile: StudentProfile): number {
  if (profile.xp_for_next_level <= 0) return 0;
  return Math.min(
    100,
    Math.max(
      0,
      Math.round((profile.xp_into_level / profile.xp_for_next_level) * 100),
    ),
  );
}
