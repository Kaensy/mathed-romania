import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, Crown } from "lucide-react";
import api from "@/api/client";
import HomeBrand from "@/components/HomeBrand";
import type { TopicExerciseSummary, ExercisesOverviewResponse } from "@/types/progress";

export default function ExercisesOverviewPage() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState<TopicExerciseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<ExercisesOverviewResponse>("/progress/exercises-overview/")
      .then((res) => setTopics(res.data.topics))
      .catch(() => setError("Nu am putut încărca exercițiile."))
      .finally(() => setLoading(false));
  }, []);

  // Group topics by unit
  const byUnit = groupByUnit(topics);

  const totalCategories = topics.reduce((s, t) => s + t.total_categories, 0);
  const completedCategories = topics.reduce((s, t) => s + t.completed_categories, 0);
  const totalAttempted = topics.reduce((s, t) => s + t.exercises_attempted, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center gap-4">
          <HomeBrand />
          <Link
            to="/dashboard"
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <span className="text-gray-300">|</span>
          <span className="text-sm font-medium text-gray-700">Exerciții</span>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Exerciții</h1>
        <p className="text-sm text-gray-500 mb-6">Toate lecțiile cu exerciții disponibile</p>

        {/* Summary stats */}
        {totalCategories > 0 && (
          <div className="flex items-center gap-6 mb-8 text-sm text-gray-600">
            <span>
              <strong className="text-gray-900">{completedCategories}</strong> / {totalCategories} categorii completate
            </span>
            <span>
              <strong className="text-gray-900">{totalAttempted}</strong> exerciții rezolvate
            </span>
          </div>
        )}

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        {topics.length === 0 && !loading && (
          <p className="text-gray-400 text-center py-16">Nicio lecție cu exerciții disponibilă momentan.</p>
        )}

        {/* Topics grouped by unit */}
        <div className="space-y-8">
          {byUnit.map(({ unitTitle, unitTopics }) => (
            <section key={unitTitle}>
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                {unitTitle}
              </h2>

              <div className="space-y-3">
                {unitTopics.map((topic) => {
                  // Sequential number across entire list
                  const globalIndex = topics.indexOf(topic) + 1;
                  const total = topic.total_categories;
                  const easyPct = total > 0 ? (topic.easy_clear_count / total) * 100 : 0;
                  const mediumPct = total > 0 ? (topic.medium_clear_count / total) * 100 : 0;
                  const hardPct = total > 0 ? (topic.hard_clear_count / total) * 100 : 0;
                  const isMediumComplete =
                    total > 0 && topic.medium_clear_count === total;

                  return (
                    <button
                      key={topic.topic_id}
                      onClick={() => navigate(`/topic/${topic.topic_id}/exercises`)}
                      className="w-full bg-white rounded-xl border border-gray-200 shadow-sm px-5 py-4 text-left hover:border-indigo-300 hover:shadow transition-all"
                    >
                      <div className="flex items-center justify-between mb-3 gap-3">
                        <div className="flex items-center gap-2 flex-wrap min-w-0">
                          <span className="text-sm font-medium text-gray-500">
                            {globalIndex}.
                          </span>
                          <span className="font-semibold text-gray-900 truncate">
                            {topic.topic_title}
                          </span>
                          {topic.is_perfect ? (
                            <PerfectBadge />
                          ) : (
                            isMediumComplete && (
                              <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                            )
                          )}
                        </div>
                        {topic.exercises_attempted > 0 && (
                          <span className="shrink-0 text-xs text-gray-400">
                            {topic.exercises_attempted} încercări
                          </span>
                        )}
                      </div>

                      {/* Extended 3-zone progress bar: Ușor / Mediu / Greu */}
                      <ThreeZoneBar
                        easyPct={easyPct}
                        mediumPct={mediumPct}
                        hardPct={hardPct}
                      />

                      {/* Per-tier chips */}
                      <div className="mt-2 flex flex-wrap items-center gap-1.5">
                        <TierChip
                          tone="green"
                          label="Ușor"
                          count={topic.easy_clear_count}
                          total={total}
                        />
                        <TierChip
                          tone="amber"
                          label="Mediu"
                          count={topic.medium_clear_count}
                          total={total}
                        />
                        <TierChip
                          tone="red"
                          label="Greu"
                          count={topic.hard_clear_count}
                          total={total}
                        />
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </main>
    </div>
  );
}

function ThreeZoneBar({
  easyPct,
  mediumPct,
  hardPct,
}: {
  easyPct: number;
  mediumPct: number;
  hardPct: number;
}) {
  return (
    <div className="grid grid-cols-3 h-1.5 gap-px rounded-full overflow-hidden bg-gray-100">
      <div className="relative bg-gray-100">
        <div
          className="absolute inset-y-0 left-0 bg-green-500 transition-all"
          style={{ width: `${easyPct}%` }}
        />
      </div>
      <div className="relative bg-gray-100">
        <div
          className="absolute inset-y-0 left-0 bg-amber-500 transition-all"
          style={{ width: `${mediumPct}%` }}
        />
      </div>
      <div className="relative bg-gray-100">
        <div
          className="absolute inset-y-0 left-0 bg-red-500 transition-all"
          style={{ width: `${hardPct}%` }}
        />
      </div>
    </div>
  );
}

const TIER_CHIP_TONE: Record<"green" | "amber" | "red", string> = {
  green: "bg-green-100 text-green-700",
  amber: "bg-amber-100 text-amber-700",
  red:   "bg-red-100 text-red-700",
};

function TierChip({
  tone,
  label,
  count,
  total,
}: {
  tone: "green" | "amber" | "red";
  label: string;
  count: number;
  total: number;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${TIER_CHIP_TONE[tone]}`}
    >
      {label} {count}/{total}
    </span>
  );
}

function PerfectBadge() {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide
                 bg-gradient-to-r from-amber-200 via-amber-300 to-amber-200 text-amber-900
                 ring-2 ring-amber-300/70 shadow-sm shrink-0"
      aria-label="Subiect perfect"
    >
      <Crown className="w-3 h-3 fill-amber-500 text-amber-700" />
      Perfect
    </span>
  );
}

function groupByUnit(topics: TopicExerciseSummary[]) {
  const map = new Map<string, TopicExerciseSummary[]>();
  for (const topic of topics) {
    const key = topic.unit_title;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(topic);
  }
  return Array.from(map.entries()).map(([unitTitle, unitTopics]) => ({
    unitTitle,
    unitTopics,
  }));
}
