import { X, Flame, Shield, Trophy } from "lucide-react";
import type { StreakData } from "@/types/progress";

interface StreakModalProps {
  streak: StreakData;
  onClose: () => void;
}

interface HeatmapCell {
  date: Date;
  dateStr: string;
  active: boolean;
  isToday: boolean;
  isFuture: boolean;
}

function buildHeatmapGrid(activeDates: string[]): HeatmapCell[][] {
  const activeSet = new Set(activeDates);
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
        active: activeSet.has(dateStr),
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

export default function StreakModal({ streak, onClose }: StreakModalProps) {
  const weeks = buildHeatmapGrid(streak.active_dates);
  const dayLabels = ["L", "Ma", "Mi", "J", "V", "S", "D"];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
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
        <div className="flex flex-col items-center pt-2">
          <Flame className="h-12 w-12 text-orange-500" />
          <div className="mt-2 text-4xl font-bold text-gray-900">
            {streak.current_streak}
          </div>
          <div className="text-sm text-gray-500">zile consecutive</div>
        </div>

        {/* Stats row */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <div className="flex items-center gap-3 rounded-xl bg-amber-50 px-4 py-3">
            <Trophy className="h-5 w-5 text-amber-500" />
            <div>
              <div className="text-xs text-gray-500">Cel mai lung</div>
              <div className="text-lg font-semibold text-gray-900">
                {streak.longest_streak}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-sky-50 px-4 py-3">
            <Shield className="h-5 w-5 text-sky-500" />
            <div>
              <div className="text-xs text-gray-500">Înghețări</div>
              <div className="text-lg font-semibold text-gray-900">
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
          <div className="flex gap-[3px]">
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
                      title={day.dateStr}
                      className={`h-3 w-3 rounded-sm ${
                        day.active ? "bg-orange-400" : "bg-gray-100"
                      } ${day.isToday ? "ring-2 ring-orange-300" : ""}`}
                    />
                  )
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
