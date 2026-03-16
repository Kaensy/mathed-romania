/**
 * LessonViewer — the main lesson reading experience.
 *
 * Renders a full lesson: header, all blocks, navigation between lessons.
 * Handles loading, error, and empty states.
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ChevronLeft, ChevronRight, ArrowLeft, PenLine } from "lucide-react";
import { BlockRenderer } from "./Blocks";
import type { LessonDetail } from "@/types/lesson";
import api from "@/api/client";

export default function LessonViewer() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!lessonId) return;
    setLoading(true);
    setError(null);

    api
      .get<LessonDetail>(`/content/lessons/${lessonId}/`)
      .then((res) => setLesson(res.data))
      .catch(() => setError("Lecția nu a putut fi încărcată. Încearcă din nou."))
      .finally(() => setLoading(false));
  }, [lessonId]);

  // Scroll to top when lesson changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [lessonId]);

    // Mark lesson as opened when it loads
    useEffect(() => {
        if (!lessonId || !lesson) return;
        api.post(`/progress/lessons/${lessonId}/open/`).catch(() => { });
    }, [lessonId, lesson]);

  // Call open endpoint when lesson loads successfully
  useEffect(() => {
     if (!lessonId || !lesson) return;
        api
            .post(`/progress/lessons/${lessonId}/open/`)
            .catch(() => { }); // fire-and-forget, never block the UI
  }, [lessonId, lesson]);

  if (loading) return <LessonSkeleton />;
  if (error) return <LessonError message={error} />;
  if (!lesson) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top navigation bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center gap-4">
          <Link
            to={`/grade/${lesson.grade_number}`}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">{lesson.unit_title}</span>
          </Link>

          <div className="flex-1 text-center">
            <p className="text-xs text-gray-400">
              Lecția {lesson.order}
            </p>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => lesson.prev_lesson_id && navigate(`/lesson/${lesson.prev_lesson_id}`)}
              disabled={!lesson.prev_lesson_id}
              className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Lecția anterioară"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => lesson.next_lesson_id && navigate(`/lesson/${lesson.next_lesson_id}`)}
              disabled={!lesson.next_lesson_id}
              className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Lecția următoare"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Lesson content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Lesson header */}
        <header className="mb-8">
          <p className="text-indigo-500 text-sm font-medium mb-1">
            Unitatea {lesson.unit_order} — {lesson.unit_title}
          </p>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight">
            {lesson.title}
          </h1>
          {lesson.summary && (
            <p className="mt-3 text-gray-500 text-base leading-relaxed">
              {lesson.summary}
            </p>
          )}
        </header>

        {/* Blocks */}
        <div className="lesson-content">
          {lesson.blocks.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <p>Conținutul acestei lecții este în curs de elaborare.</p>
            </div>
          ) : (
            lesson.blocks.map((block, index) => (
              <BlockRenderer key={index} block={block} />
            ))
          )}
        </div>

        {/* Bottom navigation */}
              {/* Bottom navigation */}
              <div className="mt-12 pt-6 border-t border-gray-200 space-y-4">

                  {/* Practice button — shown if lesson has exercises */}
                  {lesson.exercises.length > 0 && (
                      <Link
                          to={`/lesson/${lessonId}/practice`}
                          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl
        bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors"
                      >
                          <PenLine className="w-4 h-4" />
                          Exersează — {lesson.exercises.length} exerciții
                      </Link>
                  )}

                  {/* Prev / Next */}
                  <div className="flex items-center justify-between">
                      {lesson.prev_lesson_id ? (
                          <Link
                              to={`/lesson/${lesson.prev_lesson_id}`}
                              className="flex items-center gap-2 text-gray-500 hover:text-indigo-600 transition-colors group"
                          >
                              <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
                              <span className="text-sm font-medium">Lecția anterioară</span>
                          </Link>
                      ) : (
                          <div />
                      )}

                      {lesson.next_lesson_id ? (
                          <Link
                              to={`/lesson/${lesson.next_lesson_id}`}
                              className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 transition-colors group"
                          >
                              <span className="text-sm font-medium">Lecția următoare</span>
                              <ChevronRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                          </Link>
                      ) : (
                          <div />
                      )}
                  </div>
              </div>
      </main>
    </div>
  );
}

// ─── Loading skeleton ─────────────────────────────────────────────────────────

function LessonSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-40 mb-3" />
      <div className="h-8 bg-gray-200 rounded w-3/4 mb-2" />
      <div className="h-8 bg-gray-200 rounded w-1/2 mb-8" />
      {[...Array(4)].map((_, i) => (
        <div key={i} className="space-y-2 mb-6">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
          <div className="h-4 bg-gray-200 rounded w-4/6" />
        </div>
      ))}
    </div>
  );
}

// ─── Error state ──────────────────────────────────────────────────────────────

function LessonError({ message }: { message: string }) {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16 text-center">
      <p className="text-red-500 font-medium">{message}</p>
      <button
        onClick={() => window.location.reload()}
        className="mt-4 text-sm text-indigo-600 hover:underline"
      >
        Reîncearcă
      </button>
    </div>
  );
}
