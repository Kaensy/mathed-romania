import { useEffect, useRef, useState } from "react";

import { fetchPetMe } from "@/api/pets";
import { useLevelUp } from "@/contexts/LevelUpContext";
import { useXpNotifications } from "@/contexts/XPNotificationContext";
import type { PetMe } from "@/types/pets";
import LevelUpCelebration from "./LevelUpCelebration";
import PetDetailModal from "./PetDetailModal";
import PetSprite from "./petIcons";

/**
 * Dashboard pet widget. Refetches whenever XPNotificationContext's
 * `awardVersion` changes (i.e., when xp_gained > 0 fires) so level and
 * progress bar update without a manual page reload.
 */
export default function PetPanel() {
  const [pet, setPet] = useState<PetMe | null>(null);
  const [loading, setLoading] = useState(true);
  const [hidden, setHidden] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const { awardVersion } = useXpNotifications();
  const { notifyLevelUp } = useLevelUp();
  // Tracks the level seen on the previous fetch so we can detect
  // transitions across refetches. Null on first mount — that fetch
  // should never celebrate (we don't know whether the user just
  // signed in or actually leveled up).
  const prevLevelRef = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchPetMe()
      .then((data) => {
        if (cancelled) return;
        setPet(data);
        // Multi-level jumps coalesce: we always pass the current
        // (highest-reached) level, so two-level-at-once still pops
        // exactly one celebration at the top level.
        if (
          prevLevelRef.current !== null
          && data.level > prevLevelRef.current
        ) {
          notifyLevelUp(data.level);
        }
        prevLevelRef.current = data.level;
      })
      .catch(() => {
        if (!cancelled) setHidden(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [awardVersion, notifyLevelUp]);

  if (hidden) return null;

  if (loading || !pet) {
    return (
      <section className="mt-8 rounded-xl border bg-white p-5 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="h-20 w-20 rounded-full bg-slate-200 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-40 rounded bg-slate-200" />
            <div className="h-3 w-24 rounded bg-slate-100" />
            <div className="h-2 rounded-full bg-slate-100" />
          </div>
        </div>
      </section>
    );
  }

  const fillPct = computeBarFillPct(pet);

  return (
    <>
      <section className="mt-8">
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="block w-full rounded-xl border bg-white p-5 text-left hover:border-indigo-300 hover:shadow-sm transition-all"
        >
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
              <PetSprite kind={pet.pet_kind} size={56} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline justify-between gap-3">
                <h3 className="text-lg font-semibold text-slate-900 truncate">
                  {pet.display_name}
                </h3>
                <span className="shrink-0 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
                  Nivel {pet.level}
                </span>
              </div>
              <p className="mt-0.5 text-xs text-slate-500">{pet.kind_display}</p>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-indigo-500 transition-all duration-500"
                  style={{ width: `${fillPct}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-slate-400">
                {pet.xp_to_next_level} XP până la nivel {pet.level + 1} · XP total:{" "}
                {pet.total_xp.toLocaleString("ro-RO")}
              </p>
            </div>
          </div>
        </button>
      </section>

      {modalOpen && (
        <PetDetailModal
          pet={pet}
          onClose={() => setModalOpen(false)}
          onPetUpdated={(updated) => setPet(updated)}
        />
      )}

      <LevelUpCelebration
        displayName={pet.display_name}
        kind={pet.pet_kind}
      />
    </>
  );
}

// K mirrors apps/pets/levels.py; threshold(L) = (L-1)^2 * K, so the
// XP band of level L is (2L - 1) * K wide.
const LEVEL_K = 50;

/** 0–100 fill percentage of the bar within the current level. */
function computeBarFillPct(pet: PetMe): number {
  const band = (2 * pet.level - 1) * LEVEL_K;
  if (band <= 0) return 0;
  const offset = band - pet.xp_to_next_level;
  return Math.min(100, Math.max(0, Math.round((offset / band) * 100)));
}
