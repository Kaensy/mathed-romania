/**
 * QuestCard — one card for both daily and weekly quests.
 *
 * Status-driven:
 *   active     → progress bar only
 *   completed  → a loud "Revendică" button (unclaimed quests are
 *                forfeited at period rollover, so it must read urgent)
 *   claimed    → a settled, muted claimed state
 *   expired    → a dimmed, terminal state (defensive — the current
 *                period normally never shows expired)
 */
import { CheckCircle2, Coins, Sparkles } from "lucide-react";

import type { QuestAssignment } from "@/types/quests";

interface QuestCardProps {
  quest: QuestAssignment;
  /** Page-owned: runs claimQuest(id), manages claiming + error state. */
  onClaim: (id: number) => void;
  claiming: boolean;
  errorMessage?: string | null;
}

export default function QuestCard({
  quest,
  onClaim,
  claiming,
  errorMessage,
}: QuestCardProps) {
  const { progress, target, status, cadence } = quest;
  const pct = target > 0 ? Math.min(100, (progress / target) * 100) : 0;
  const isExpired = status === "expired";

  return (
    <div
      className={`bg-white rounded-2xl border shadow-sm p-5 transition-colors ${
        isExpired
          ? "border-gray-200 opacity-60"
          : status === "completed"
            ? "border-amber-200"
            : "border-gray-200"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-bold text-gray-900">{quest.title}</h3>
          <p className="mt-0.5 text-sm text-gray-500">{quest.description}</p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          {quest.xp_reward != null && (
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
              <Sparkles className="h-3 w-3" />+{quest.xp_reward} XP
            </span>
          )}
          {cadence === "daily" && quest.point_value != null && (
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700">
              <Coins className="h-3 w-3" />+{quest.point_value} pct
            </span>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="mt-4">
        <div className="mb-1 flex items-center justify-between text-xs text-gray-400">
          <span>Progres</span>
          <span className="font-medium text-gray-500">
            {Math.min(progress, target)} / {target}
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              status === "claimed"
                ? "bg-green-500"
                : status === "completed"
                  ? "bg-amber-500"
                  : "bg-indigo-500"
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Status footer */}
      <div className="mt-4">
        {status === "completed" && (
          <>
            <button
              onClick={() => onClaim(quest.id)}
              disabled={claiming}
              className="flex w-full items-center justify-center gap-2 rounded-xl
                bg-amber-500 py-3 text-sm font-bold text-white shadow-sm
                hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50
                transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              {claiming ? "Se revendică..." : "Revendică recompensa"}
            </button>
            <p className="mt-2 text-center text-xs text-amber-600">
              Nerevendicată, recompensa se pierde la resetare.
            </p>
          </>
        )}

        {status === "claimed" && (
          <div className="flex items-center justify-center gap-2 rounded-xl bg-green-50 py-2.5 text-sm font-semibold text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            <span>
              Revendicată
              {quest.claimed_at &&
                ` · ${new Date(quest.claimed_at).toLocaleTimeString("ro-RO", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}`}
            </span>
          </div>
        )}

        {status === "active" && (
          <p className="text-center text-xs text-gray-400">
            Continuă pentru a finaliza această misiune.
          </p>
        )}

        {isExpired && (
          <p className="text-center text-xs font-medium text-gray-400">
            Expirată
          </p>
        )}

        {errorMessage && (
          <p className="mt-2 text-center text-xs text-red-600">
            {errorMessage}
          </p>
        )}
      </div>
    </div>
  );
}
