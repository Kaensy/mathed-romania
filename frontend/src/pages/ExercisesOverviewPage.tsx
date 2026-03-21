import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, PenLine, Star } from "lucide-react";
import api from "@/api/client";
import { CATEGORY_LABELS } from "@/constants/categoryLabels";
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
                {unitTopics.map((topic, indexInUnit) => {
                  // Sequential number across entire list
                  const globalIndex = topics.indexOf(topic) + 1;
                  const progressPct =
                    topic.total_categories > 0
                      ? Math.round((topic.completed_categories / topic.total_categories) * 100)
                      : 0;
                  const isComplete = progressPct === 100 && topic.total_categories > 0;

                  return (
                    <button
                      key={topic.topic_id}
                      onClick={() => navigate(`/topic/${topic.topic_id}/exercises`)}
                      className="w-full bg-white rounded-xl border border-gray-200 shadow-sm px-5 py-4 text-left hover:border-indigo-300 hover:shadow transition-all"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-500">
                            {globalIndex}.
                          </span>
                          <span className="font-semibold text-gray-900">
                            {topic.topic_title}
                          </span>
                          {isComplete && (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {progressPct}%
                        </span>
                      </div>

                      {/* Progress bar */}
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isComplete ? "bg-green-500" : "bg-indigo-500"
                          }`}
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>

                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span>
                          {topic.completed_categories}/{topic.total_categories} categor{topic.total_categories === 1 ? "ie" : "ii"}
                        </span>
                        {topic.exercises_attempted > 0 && (
                          <span>{topic.exercises_attempted} încercări</span>
                        )}
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
