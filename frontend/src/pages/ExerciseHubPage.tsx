// frontend/src/pages/ExerciseHubPage.tsx
/**
 * ExerciseHubPage — shows all exercise categories for a lesson.
 *
 * Route: /lesson/:lessonId/exercises
 *
 * Student sees each category (or "Toate exercițiile" if uncategorized),
 * their best score, and can start a 5-exercise session for any category.
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, ChevronRight, Star } from "lucide-react";
import api from "@/api/client";

interface CategoryInfo {
  category: string;
  label: string;
  exercise_count: number;
  correct_attempts: number;
  total_attempts: number;
  best_session_score: number | null; // best X out of 5
}

interface LessonCategoriesResponse {
  lesson_id: number;
  lesson_title: string;
  categories: CategoryInfo[];
}

export default function ExerciseHubPage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<LessonCategoriesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!lessonId) return;
    api
      .get<LessonCategoriesResponse>(`/progress/lessons/${lessonId}/categories/`)
      .then((res) => setData(res.data))
      .catch(() => setError("Nu am putut încărca exercițiile."))
      .finally(() => setLoading(false));
  }, [lessonId]);

  if (loading) return <HubSkeleton />;
  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 font-medium">{error}</p>
          <button onClick={() => navigate(-1)} className="mt-4 text-indigo-600 hover:underline text-sm">
            Înapoi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          <Link
            to={`/lesson/${lessonId}`}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi la lecție</span>
          </Link>
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Exerciții</h1>
        <p className="text-gray-500 text-sm mb-8">{data.lesson_title}</p>

        <div className="space-y-3">
          {data.categories.map((cat) => {
            const hasAttempts = cat.total_attempts > 0;
            const accuracyPct = hasAttempts
              ? Math.round((cat.correct_attempts / cat.total_attempts) * 100)
              : null;

            return (
              <Link
                key={cat.category}
                to={`/lesson/${lessonId}/practice${cat.category ? `?category=${cat.category}` : ""}`}
                className="block bg-white rounded-xl border border-gray-200 shadow-sm
                  hover:border-indigo-300 hover:shadow-md transition-all group"
              >
                <div className="px-5 py-4 flex items-center gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800 group-hover:text-indigo-700 transition-colors">
                      {cat.label}
                    </p>
                    <p className="text-sm text-gray-400 mt-0.5">
                      {cat.exercise_count} {cat.exercise_count === 1 ? "tip de exercițiu" : "tipuri de exerciții"}
                    </p>
                  </div>

                  {/* Score display */}
                  <div className="shrink-0 text-right">
                    {cat.best_session_score !== null ? (
                      <div className="flex items-center gap-1.5">
                        <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                        <span className="font-bold text-gray-800">
                          {cat.best_session_score}/5
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400">Neînceput</span>
                    )}
                    {accuracyPct !== null && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {cat.correct_attempts}/{cat.total_attempts} corecte
                      </p>
                    )}
                  </div>

                  <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-indigo-400 transition-colors shrink-0" />
                </div>

                {/* Progress bar */}
                {cat.best_session_score !== null && (
                  <div className="px-5 pb-4">
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-1.5 bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${(cat.best_session_score / 5) * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </Link>
            );
          })}
        </div>
      </main>
    </div>
  );
}

function HubSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-14 bg-white border-b border-gray-200" />
      <div className="max-w-2xl mx-auto px-4 py-8 animate-pulse space-y-3">
        <div className="h-7 bg-gray-200 rounded w-40 mb-6" />
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 h-20" />
        ))}
      </div>
    </div>
  );
}
