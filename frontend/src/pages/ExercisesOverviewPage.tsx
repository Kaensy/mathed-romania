/**
 * ExercisesOverviewPage — global overview of all lessons with exercises.
 *
 * Route: /exercises
 *
 * Shows every published lesson that has at least one active exercise,
 * grouped by unit, with per-lesson completion progress (categories cleared,
 * attempts made). Clicking a lesson card navigates to its ExerciseHubPage.
 */
import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, PenLine, Star } from "lucide-react";
import api from "@/api/client";
import { CATEGORY_LABELS } from "@/constants/categoryLabels";

// ─── Types ────────────────────────────────────────────────────────────────────

interface LessonExerciseSummary {
  lesson_id: number;
  lesson_title: string;
  unit_id: number;
  unit_title: string;
  unit_order: number;
  lesson_order: number;
  total_categories: number;
  completed_categories: number;
  exercises_attempted: number;
}

interface ExercisesOverviewResponse {
  lessons: LessonExerciseSummary[];
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ExercisesOverviewPage() {
  const navigate = useNavigate();
  const [lessons, setLessons] = useState<LessonExerciseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<ExercisesOverviewResponse>("/progress/exercises-overview/")
      .then((res) => setLessons(res.data.lessons))
      .catch(() => setError("Nu am putut încărca exercițiile."))
      .finally(() => setLoading(false));
  }, []);

  // Group lessons by unit
  const byUnit = groupByUnit(lessons);

  const totalCategories = lessons.reduce((s, l) => s + l.total_categories, 0);
  const completedCategories = lessons.reduce((s, l) => s + l.completed_categories, 0);
  const totalAttempted = lessons.reduce((s, l) => s + l.exercises_attempted, 0);

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
        <p className="text-gray-500 text-sm mb-6">
          Toate lecțiile cu exerciții disponibile
        </p>

        {/* Summary strip */}
        {!loading && !error && lessons.length > 0 && (
          <div className="flex flex-wrap gap-6 mb-8 text-sm text-gray-500">
            <span>
              <span className="font-semibold text-gray-800">{completedCategories}</span>
              {" / "}{totalCategories} categorii completate
            </span>
            <span>
              <span className="font-semibold text-gray-800">{totalAttempted}</span>
              {" "}exerciții rezolvate
            </span>
          </div>
        )}

        {loading && <SkeletonList />}

        {error && (
          <div className="text-center py-16 text-red-500">
            <p>{error}</p>
            <button onClick={() => navigate(-1)} className="mt-4 text-indigo-600 hover:underline text-sm">
              Înapoi
            </button>
          </div>
        )}

        {!loading && !error && lessons.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <PenLine className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p>Nu există exerciții disponibile încă.</p>
          </div>
        )}

        {!loading && !error && byUnit.map(({ unitTitle, unitOrder, lessons: unitLessons }) => (
          <section key={unitOrder} className="mb-10">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              {unitTitle}
            </h2>
            <div className="space-y-3">
              {unitLessons.map((lesson) => (
                <LessonCard key={lesson.lesson_id} lesson={lesson} />
              ))}
            </div>
          </section>
        ))}
      </main>
    </div>
  );
}

// ─── Lesson card ──────────────────────────────────────────────────────────────

function LessonCard({ lesson }: { lesson: LessonExerciseSummary }) {
  const isAllDone = lesson.completed_categories === lesson.total_categories && lesson.total_categories > 0;
  const pct = lesson.total_categories > 0
    ? Math.round((lesson.completed_categories / lesson.total_categories) * 100)
    : 0;

  return (
    <Link
  to={`/lesson/${lesson.lesson_id}/exercises`}
  state={{ from: "exercises-overview" }}
      className="block bg-white rounded-2xl border border-gray-200 shadow-sm px-5 py-4
        hover:border-indigo-300 hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 font-mono shrink-0">
              {lesson.lesson_order}.
            </span>
            <h3 className="font-semibold text-gray-900 text-sm truncate">
              {lesson.lesson_title}
            </h3>
            {isAllDone && (
              <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
            )}
          </div>

          {/* Progress bar */}
          <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-1.5 rounded-full transition-all duration-500 ${
                isAllDone ? "bg-emerald-500" : "bg-indigo-400"
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>

          {/* Stats row */}
          <div className="mt-1.5 flex items-center gap-3 text-xs text-gray-400">
            <span>
              {lesson.completed_categories}/{lesson.total_categories} categorii
            </span>
            {lesson.exercises_attempted > 0 && (
              <span>{lesson.exercises_attempted} încercări</span>
            )}
          </div>
        </div>

        <div className="text-xs font-medium text-gray-400 shrink-0 pt-0.5">
          {pct}%
        </div>
      </div>
    </Link>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function groupByUnit(lessons: LessonExerciseSummary[]) {
  const map = new Map<number, { unitTitle: string; unitOrder: number; lessons: LessonExerciseSummary[] }>();
  for (const lesson of lessons) {
    if (!map.has(lesson.unit_id)) {
      map.set(lesson.unit_id, {
        unitTitle: lesson.unit_title,
        unitOrder: lesson.unit_order,
        lessons: [],
      });
    }
    map.get(lesson.unit_id)!.lessons.push(lesson);
  }
  return Array.from(map.values()).sort((a, b) => a.unitOrder - b.unitOrder);
}

function SkeletonList() {
  return (
    <div className="space-y-3 animate-pulse">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-white rounded-2xl border border-gray-200 px-5 py-4">
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
          <div className="h-1.5 bg-gray-100 rounded-full" />
          <div className="h-3 bg-gray-100 rounded w-1/3 mt-1.5" />
        </div>
      ))}
    </div>
  );
}
