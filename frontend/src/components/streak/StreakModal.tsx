import { X, Flame, Shield, Trophy } from "lucide-react";
import type { StreakData } from "@/types/progress";

interface StreakModalProps {
  streak: StreakData;
  onClose: () => void;
}

interface HeatmapCell {
  date: Date;
  dateStr: string;
  count: number;
  isToday: boolean;
  isFuture: boolean;
}

const MONTH_ABBR = [
  "Ian", "Feb", "Mar", "Apr", "Mai", "Iun",
  "Iul", "Aug", "Sep", "Oct", "Noi", "Dec",
];

function buildHeatmapGrid(
  counts: Record<string, number>,
): HeatmapCell[][] {
  const today = new Date();
  const todayStr = today.toISOString().split("T")[0]!;
  const start = new Date(today);
  start.setDate(start.getDate() - 90);
  while (start.getDay() !== 1) start.setDate(start.getDate() - 1);

  const weeks: HeatmapCell[][] = [];
  const cursor = new Date(start);

  while (cursor <= today) {
    const week: HeatmapCell[] = [];
    for (let d = 0; d < 7; d++) {
      const dateStr = cursor.toISOString().split("T")[0]!;
      const isFuture = cursor > today;
      week.push({
        date: new Date(cursor),
        dateStr,
        count: counts[dateStr] ?? 0,
        isToday: dateStr === todayStr,
        isFuture,
      });
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
    if (cursor > today && week.some((d) => d.isToday)) break;
  }

  return weeks;
}

function intensityClass(count: number): string {
  if (count <= 0) return "bg-gray-100";
  if (count === 1) return "bg-orange-200";
  if (count <= 4) return "bg-orange-300";
  if (count <= 9) return "bg-orange-500";
  return "bg-orange-600";
}

/**
 * Returns one label per week column — the month abbreviation when the
 * first day of the week (Monday) is the first Monday of that month
 * inside the rendered window. Empty string otherwise.
 */
function monthLabelsForWeeks(weeks: HeatmapCell[][]): string[] {
  let lastMonth = -1;
  return weeks.map((week) => {
    const anchor = week[0]!.date;
    const m = anchor.getMonth();
    if (m !== lastMonth) {
      lastMonth = m;
      return MONTH_ABBR[m]!;
    }
    return "";
  });
}

export default function StreakModal({ streak, onClose }: StreakModalProps) {
  const weeks = buildHeatmapGrid(streak.daily_counts);
  const monthLabels = monthLabelsForWeeks(weeks);
  const dayLabels = ["L", "Ma", "Mi", "J", "V", "S", "D"];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
          aria-label="Închide"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Hero */}
        <div className="flex flex-col items-center pt-4 pb-2">
          <div className="relative">
            <div
              aria-hidden
              className="absolute inset-0 -z-10 rounded-full bg-orange-300/40 blur-2xl"
            />
            <Flame
              className="h-20 w-20 text-orange-500 drop-shadow-[0_4px_12px_rgba(249,115,22,0.45)]"
              strokeWidth={1.75}
              fill="currentColor"
              fillOpacity={0.15}
            />
          </div>
          <div className="mt-3 bg-gradient-to-br from-orange-500 to-red-500 bg-clip-text text-7xl font-extrabold leading-none tracking-tight text-transparent">
            {streak.current_streak}
          </div>
          <div className="mt-2 text-sm font-medium text-gray-500">
            {streak.current_streak === 1 ? "zi consecutivă" : "zile consecutive"}
          </div>
        </div>

        {/* Stats row */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <div className="flex items-center gap-3 rounded-xl border border-amber-200/70 bg-gradient-to-br from-amber-50 to-amber-100 px-4 py-3 shadow-sm">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/70 ring-1 ring-amber-200">
              <Trophy className="h-5 w-5 text-amber-600" strokeWidth={2.25} />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-medium uppercase tracking-wide text-amber-700/80">
                Cel mai lung
              </div>
              <div className="text-xl font-bold text-gray-900">
                {streak.longest_streak}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-sky-200/70 bg-gradient-to-br from-sky-50 to-sky-100 px-4 py-3 shadow-sm">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/70 ring-1 ring-sky-200">
              <Shield className="h-5 w-5 text-sky-600" strokeWidth={2.25} />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-medium uppercase tracking-wide text-sky-700/80">
                Înghețări
              </div>
              <div className="text-xl font-bold text-gray-900">
                {streak.freeze_count}/2
              </div>
            </div>
          </div>
        </div>

        {/* Heatmap */}
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium text-gray-700">
            Activitate — ultimele 3 luni
          </div>

          {/* Month labels row, aligned to week columns */}
          <div className="flex gap-[3px] pl-4">
            {monthLabels.map((label, i) => (
              <div
                key={i}
                className="h-3 w-3 text-[10px] font-medium leading-3 text-gray-400"
              >
                {label}
              </div>
            ))}
          </div>

          <div className="mt-1 flex gap-[3px]">
            <div className="flex flex-col gap-[3px] pr-1">
              {dayLabels.map((d) => (
                <div
                  key={d}
                  className="flex h-3 w-3 items-center justify-end text-[10px] text-gray-400"
                >
                  {d}
                </div>
              ))}
            </div>
            {weeks.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-[3px]">
                {week.map((day) =>
                  day.isFuture ? (
                    <div key={day.dateStr} className="h-3 w-3" />
                  ) : (
                    <div
                      key={day.dateStr}
                      title={`${day.dateStr} — ${day.count} ${day.count === 1 ? "exercițiu" : "exerciții"}`}
                      className={`h-3 w-3 rounded-sm ${intensityClass(day.count)} ${
                        day.isToday ? "ring-2 ring-orange-400 ring-offset-1" : ""
                      }`}
                    />
                  )
                )}
              </div>
            ))}
          </div>

          {/* Intensity legend */}
          <div className="mt-3 flex items-center justify-end gap-1.5 text-[10px] text-gray-400">
            <span>mai puțin</span>
            <span className="h-3 w-3 rounded-sm bg-gray-100" />
            <span className="h-3 w-3 rounded-sm bg-orange-200" />
            <span className="h-3 w-3 rounded-sm bg-orange-300" />
            <span className="h-3 w-3 rounded-sm bg-orange-500" />
            <span className="h-3 w-3 rounded-sm bg-orange-600" />
            <span>mai mult</span>
          </div>
        </div>
      </div>
    </div>
  );
}
