import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ChevronRight, ArrowLeft, BookOpen, Lock } from "lucide-react";
import api from "@/api/client";
import { useAuth } from "@/hooks/useAuth";

interface LessonListItem {
  id: number;
  order: number;
  title: string;
  summary: string;
  exercise_count: number;
}

interface UnitDetail {
  id: number;
  order: number;
  title: string;
  description: string;
  lessons: LessonListItem[];
}

interface GradeDetail {
  id: number;
  number: number;
  name: string;
  units: UnitDetail[];
}

export default function GradePage() {
  const { gradeNumber } = useParams<{ gradeNumber: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [grade, setGrade] = useState<GradeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<GradeDetail>(`/content/grades/${gradeNumber}/`)
      .then((res) => setGrade(res.data))
      .catch(() => setError("Nu am putut încărca lecțiile. Încearcă din nou."))
      .finally(() => setLoading(false));
  }, [gradeNumber]);

  if (loading) return <GradeSkeleton />;
  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-500 font-medium">{error}</p>
        <button onClick={() => window.location.reload()} className="mt-4 text-sm text-primary-600 hover:underline">
          Reîncearcă
        </button>
      </div>
    </div>
  );
  if (!grade) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto max-w-3xl px-4 h-14 flex items-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </button>
          <div className="flex-1 text-center">
            <span className="text-sm font-medium text-gray-700">{grade.name}</span>
          </div>
          <div className="text-sm text-gray-500">{user?.first_name}</div>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Lecții — {grade.name}</h1>
        <p className="text-gray-500 text-sm mb-8">Selectează o lecție pentru a începe.</p>

        <div className="space-y-6">
          {grade.units.map((unit) => (
            <div key={unit.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {/* Unit header */}
              <div className="px-5 py-4 border-b border-gray-100 bg-gray-50">
                <p className="text-xs text-gray-400 uppercase tracking-wider font-medium mb-0.5">
                  Unitatea {unit.order}
                </p>
                <h2 className="font-semibold text-gray-800">{unit.title}</h2>
                {unit.description && (
                  <p className="text-sm text-gray-500 mt-1">{unit.description}</p>
                )}
              </div>

              {/* Lessons */}
              {unit.lessons.length === 0 ? (
                <div className="px-5 py-4 flex items-center gap-2 text-gray-400 text-sm">
                  <Lock className="w-4 h-4" />
                  <span>Lecțiile acestei unități sunt în curs de elaborare.</span>
                </div>
              ) : (
                <ul className="divide-y divide-gray-100">
                  {unit.lessons.map((lesson) => (
                    <li key={lesson.id}>
                      <Link
                        to={`/lesson/${lesson.id}`}
                        className="flex items-center gap-4 px-5 py-4 hover:bg-primary-50 transition-colors group"
                      >
                        <div className="shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-600 font-semibold text-sm flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                          {lesson.order}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-800 group-hover:text-primary-700 transition-colors truncate">
                            {lesson.title}
                          </p>
                          {lesson.summary && (
                            <p className="text-sm text-gray-500 mt-0.5 truncate">{lesson.summary}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          {lesson.exercise_count > 0 && (
                            <span className="flex items-center gap-1 text-xs text-gray-400">
                              <BookOpen className="w-3.5 h-3.5" />
                              {lesson.exercise_count}
                            </span>
                          )}
                          <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-primary-400 transition-colors" />
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

function GradeSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-14 bg-white border-b" />
      <div className="mx-auto max-w-3xl px-4 py-8 animate-pulse space-y-6">
        <div className="h-7 bg-gray-200 rounded w-48" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-5 py-4 bg-gray-50 border-b">
              <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
              <div className="h-5 bg-gray-200 rounded w-64" />
            </div>
            {[1, 2, 3].map((j) => (
              <div key={j} className="px-5 py-4 border-b border-gray-100 flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-gray-200 shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-100 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
