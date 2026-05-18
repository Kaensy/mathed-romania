/**
 * MilestoneBar — the daily points bar (Daily tab only).
 *
 * A horizontal track filled by today's points, with the five rungs
 * from `bar.milestones` positioned by threshold. Each rung renders
 * locked / claimable / claimed; a claimable rung is the claim action.
 * The top (finale) rung is visually distinct. Claim feedback is
 * intentionally subtle this phase — the XP toast already fires; the
 * big celebration is Phase 3.
 */
import { Check, Lock, Sparkles, Trophy } from "lucide-react";

import type { DailyChallengeBar } from "@/types/quests";

interface MilestoneBarProps {
  bar: DailyChallengeBar;
  /** Page-owned: runs claimMilestone(threshold), manages state. */
  onClaim: (threshold: number) => void;
  claimingThreshold: number | null;
  errorMessage?: string | null;
}

export default function MilestoneBar({
  bar,
  onClaim,
  claimingThreshold,
  errorMessage,
}: MilestoneBarProps) {
  const max =
    bar.milestones.reduce((m, r) => Math.max(m, r.threshold), 0) || 100;
  const fillPct = Math.min(100, (bar.points / max) * 100);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
      <div className="mb-1 flex items-baseline justify-between">
        <h2 className="font-bold text-gray-900">Provocarea zilei</h2>
        <span className="text-sm text-gray-500">
          <span className="font-semibold text-indigo-600">{bar.points}</span>
          {" / "}
          {max} puncte
        </span>
      </div>
      <p className="mb-6 text-xs text-gray-400">
        Revendică misiunile zilnice pentru a strânge puncte și a debloca
        recompense.
      </p>

      {/* Track + rungs. Horizontal inset keeps the end rung/label from
          clipping the card edge; vertical room is reserved above and
          below for the absolutely-placed nodes + labels. */}
      <div className="px-3 pt-6">
        <div className="relative h-2 rounded-full bg-gray-100">
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-indigo-400 to-indigo-600 transition-all duration-500"
            style={{ width: `${fillPct}%` }}
          />
          {bar.milestones.map((rung) => {
            const leftPct = (rung.threshold / max) * 100;
            const claimable = !rung.claimed && bar.points >= rung.threshold;
            const isFinale = rung.threshold === max;
            const busy = claimingThreshold === rung.threshold;

            const size = isFinale ? "h-10 w-10" : "h-7 w-7";
            let nodeClass: string;
            if (rung.claimed) {
              nodeClass = "bg-green-500 text-white ring-2 ring-green-200";
            } else if (claimable) {
              nodeClass =
                "bg-amber-500 text-white ring-4 ring-amber-200 animate-pulse";
            } else {
              nodeClass = isFinale
                ? "bg-white border-2 border-amber-200 text-amber-300"
                : "bg-white border-2 border-gray-200 text-gray-300";
            }

            const Icon = rung.claimed
              ? Check
              : isFinale
                ? Trophy
                : claimable
                  ? Sparkles
                  : Lock;

            return (
              <div
                key={rung.threshold}
                className="absolute top-1/2 flex flex-col items-center"
                style={{
                  left: `${leftPct}%`,
                  transform: "translate(-50%, -50%)",
                }}
              >
                <button
                  type="button"
                  disabled={!claimable || busy}
                  onClick={() => onClaim(rung.threshold)}
                  aria-label={
                    rung.claimed
                      ? `Prag ${rung.threshold} puncte revendicat`
                      : claimable
                        ? `Revendică pragul de ${rung.threshold} puncte`
                        : `Pragul de ${rung.threshold} puncte blocat`
                  }
                  className={`flex items-center justify-center rounded-full
                    shadow-sm transition-transform ${size} ${nodeClass}
                    ${claimable && !busy ? "cursor-pointer hover:scale-110" : "cursor-default"}`}
                >
                  <Icon className={isFinale ? "h-5 w-5" : "h-3.5 w-3.5"} />
                </button>

                {/* Label + reward below the node. */}
                <div className="mt-2 w-16 text-center">
                  <div
                    className={`text-[11px] font-semibold ${
                      isFinale ? "text-amber-600" : "text-gray-500"
                    }`}
                  >
                    {rung.threshold} pct
                  </div>
                  <div className="text-[10px] text-gray-400">
                    +{rung.xp_reward} XP
                  </div>
                  {claimable && (
                    <div
                      className={`mt-0.5 text-[10px] font-semibold ${
                        busy ? "text-gray-400" : "text-amber-600"
                      }`}
                    >
                      {busy ? "..." : "Revendică"}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        {/* Reserve vertical room for the absolutely-placed labels. */}
        <div className="h-20" />
      </div>

      {errorMessage && (
        <p className="mt-1 text-center text-xs text-red-600">{errorMessage}</p>
      )}
    </div>
  );
}
