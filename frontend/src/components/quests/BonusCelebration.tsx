import { Trophy } from "lucide-react";

import { useBonusCelebration } from "@/contexts/BonusCelebrationContext";

/**
 * Full-screen daily-bonus finale. The Block 10 LevelUpCelebration
 * treatment (same backdrop + pop animations, amber ring), fired when
 * a milestone claim newly completes the 100-point rung. Reads
 * BonusCelebrationContext; auto-dismisses on the provider's timer.
 * Click the backdrop to dismiss early.
 */
export default function BonusCelebration() {
  const { celebrating, dismiss } = useBonusCelebration();
  if (!celebrating) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Bonus zilnic complet"
      onClick={dismiss}
      className="fixed inset-0 z-[1200] flex cursor-pointer items-center justify-center bg-slate-900/60 animate-level-up-backdrop"
    >
      <div className="flex flex-col items-center gap-4 px-6 text-center animate-level-up-pop">
        <div className="flex h-32 w-32 items-center justify-center rounded-full bg-amber-100 text-amber-600 shadow-2xl ring-4 ring-amber-300">
          <Trophy className="h-16 w-16" />
        </div>
        <div className="rounded-full bg-amber-500 px-6 py-2 text-2xl font-bold text-white shadow-lg ring-2 ring-amber-300">
          Bonus zilnic complet!
        </div>
        <p className="text-lg font-medium text-white drop-shadow-md">
          Ai strâns toate cele 100 de puncte de azi. Bravo!
        </p>
      </div>
    </div>
  );
}
