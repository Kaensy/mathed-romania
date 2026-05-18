/**
 * QuestSummaryCard — compact dashboard widget (student only).
 *
 * A daily summary alongside the pet panel / daily-test / "Recomandat"
 * cards: claimed-vs-total, the bonus meter (points / max), and a loud
 * nudge when any quest is completed-but-unclaimed (those are forfeited
 * at rollover). Links to /quests. No quest list, no milestone bar —
 * that is the page's job. Non-fatal: hides itself on error.
 */
import { Link } from "react-router-dom";
import { ListChecks, Sparkles } from "lucide-react";

import { useQuests } from "@/hooks/useQuests";

export default function QuestSummaryCard() {
  const { daily, weekly, bar, loading, error } = useQuests();

  if (loading) {
    return (
      <div className="mt-8 rounded-xl border bg-white p-5 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gray-200 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-32" />
            <div className="h-3 bg-gray-100 rounded w-48" />
          </div>
        </div>
      </div>
    );
  }

  // Non-fatal — hide the widget rather than break the dashboard.
  if (error || !bar) return null;

  const dailyClaimed = daily.filter((q) => q.status === "claimed").length;
  const dailyTotal = daily.length;
  const hasUnclaimed = [...daily, ...weekly].some(
    (q) => q.status === "completed",
  );

  const max =
    bar.milestones.reduce((m, r) => Math.max(m, r.threshold), 0) || 100;
  const pct = Math.min(100, (bar.points / max) * 100);

  const accent = hasUnclaimed
    ? {
        border: "border-amber-200",
        from: "from-amber-50",
        bubble: "bg-amber-100 text-amber-500",
        meter: "bg-amber-500",
        cta: "bg-amber-500",
        ctaLabel: "Revendică",
      }
    : {
        border: "border-indigo-200",
        from: "from-indigo-50",
        bubble: "bg-indigo-100 text-indigo-500",
        meter: "bg-indigo-500",
        cta: "bg-indigo-600",
        ctaLabel: "Vezi",
      };

  return (
    <Link
      to="/quests"
      className={`mt-8 block rounded-xl border-2 ${accent.border}
        bg-gradient-to-br ${accent.from} to-white p-5
        hover:shadow-sm transition-all`}
    >
      <div className="flex items-center gap-4">
        <div
          className={`w-12 h-12 rounded-full ${accent.bubble}
            flex items-center justify-center shrink-0`}
        >
          {hasUnclaimed ? (
            <Sparkles className="w-6 h-6" />
          ) : (
            <ListChecks className="w-6 h-6" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900">Misiuni</h3>
          <p className="text-sm text-gray-600 mt-0.5">
            {hasUnclaimed
              ? "Ai recompense de revendicat înainte de resetare!"
              : `${dailyClaimed}/${dailyTotal} misiuni zilnice revendicate`}
          </p>
          <div className="mt-2">
            <div className="flex justify-between text-[11px] text-gray-400 mb-0.5">
              <span>Bonus zilnic</span>
              <span>
                {bar.points}/{max}
              </span>
            </div>
            <div className="h-1.5 bg-white/80 rounded-full overflow-hidden">
              <div
                className={`h-1.5 ${accent.meter} rounded-full transition-all duration-500`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        </div>
        <span
          className={`shrink-0 px-4 py-2 rounded-lg ${accent.cta}
            text-white text-sm font-semibold`}
        >
          {accent.ctaLabel}
        </span>
      </div>
    </Link>
  );
}
