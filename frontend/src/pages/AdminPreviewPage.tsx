/**
 * AdminPreviewPage — admin-only page to preview exercise instances.
 *
 * Route: /admin-preview/exercise/:exerciseId
 *
 * Renders the exact same ExerciseCard students see. Submits answers
 * to the real grading endpoint (session_id=null so no tier tracking).
 * "Next instance" regenerates a fresh random instance without reloading.
 */
import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { RotateCcw, ArrowLeft, FlaskConical } from "lucide-react";
import api from "@/api/client";
import ExerciseCard from "@/components/exercise/ExerciseCard";
import type { ExerciseInstance, Difficulty } from "@/types/progress";

  interface PreviewResponse {
    instance: ExerciseInstance;
    exercise_id: number;
    topic_title: string;
    exercise_type: string;
    difficulty: string;
    category: string;
  }

const DIFFICULTY_LABEL: Record<string, string> = {
  easy: "Ușor",
  medium: "Mediu",
  hard: "Greu",
};

export default function AdminPreviewPage() {
  const { exerciseId } = useParams<{ exerciseId: string }>();
  const navigate = useNavigate();

  const [instance, setInstance] = useState<ExerciseInstance | null>(null);
  const [meta, setMeta] = useState<Omit<PreviewResponse, "instance"> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [instanceKey, setInstanceKey] = useState(0); // forces ExerciseCard remount on refresh

  const fetchInstance = useCallback(() => {
    if (!exerciseId) return;
    setLoading(true);
    setError(null);
    api
      .get<PreviewResponse>(`/progress/exercises/${exerciseId}/preview-instance/`)
      .then((res) => {
        setInstance(res.data.instance);
        setMeta({
          exercise_id: res.data.exercise_id,
          topic_title: res.data.topic_title,
          exercise_type: res.data.exercise_type,
          difficulty: res.data.difficulty,
          category: res.data.category,
        });
      })
      .catch((err) => {
  if (err?.response?.status === 403) {
    setError("Acces refuzat — această pagină este disponibilă doar pentru administratori.");
  } else {
    setError(err?.response?.data?.error ?? "Nu am putut genera instanța. Verifică template-ul exercițiului.");
  }
})
      .finally(() => setLoading(false));
  }, [exerciseId]);

  useEffect(() => {
    fetchInstance();
  }, [fetchInstance]);

  const handleNextInstance = () => {
    setInstance(null);
    setInstanceKey((k) => k + 1);
    fetchInstance();
  };

  // ── Loading ──────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600" />
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────
  if (error || !instance || !meta) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl border border-red-200 p-8 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FlaskConical className="w-6 h-6 text-red-500" />
          </div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Eroare la generare</h2>
          <p className="text-sm text-red-600 font-mono bg-red-50 rounded-lg p-3 text-left mb-6">
            {error}
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => navigate(-1)}
              className="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 text-sm font-medium"
            >
              Înapoi
            </button>
            <button
              onClick={fetchInstance}
              className="flex-1 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 text-sm font-medium"
            >
              Reîncearcă
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Main ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <div className="flex-1" />
          {/* Admin preview badge */}
          <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-100 border border-amber-300 rounded-full">
            <FlaskConical className="w-3.5 h-3.5 text-amber-600" />
            <span className="text-xs font-semibold text-amber-700">Admin Preview</span>
          </div>
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Exercise metadata */}
        <div className="mb-4">
          <p className="text-xs text-gray-400 mb-1">{meta.topic_title}</p>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
              #{meta.exercise_id}
            </span>
            <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
              {meta.exercise_type}
            </span>
            <DifficultyBadge difficulty={meta.difficulty} />
            {meta.category && (
              <span className="text-xs px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded font-mono">
                {meta.category}
              </span>
            )}
          </div>
        </div>

        {/* The actual exercise — same component students use */}
        <ExerciseCard
  key={instanceKey}
  exercise={instance}
  sessionId={null}
  previewMode={true}   // ← add this
  disableGlossary={true}
  onResult={() => {}}
  onNext={handleNextInstance}
  isLast={false}
/>

        {/* "Generate new instance" button shown below the card */}
        <button
          onClick={handleNextInstance}
          className="mt-4 w-full py-3 border-2 border-dashed border-gray-200 text-gray-400
            hover:border-indigo-300 hover:text-indigo-500 rounded-xl text-sm font-medium
            transition-colors flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Generează altă instanță
        </button>

        {/* Hint: instance JSON for debugging */}
        <details className="mt-6">
          <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600 select-none">
            Arată JSON instanță (debug)
          </summary>
          <pre className="mt-2 bg-gray-900 text-green-400 text-xs rounded-xl p-4 overflow-auto leading-relaxed">
            {JSON.stringify(instance, null, 2)}
          </pre>
        </details>
      </main>
    </div>
  );
}

// ─── Difficulty badge ─────────────────────────────────────────────────────────

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const config: Record<string, string> = {
    easy:   "bg-emerald-50 text-emerald-700 border border-emerald-200",
    medium: "bg-amber-50 text-amber-700 border border-amber-200",
    hard:   "bg-red-50 text-red-700 border border-red-200",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded font-medium ${config[difficulty] ?? "bg-gray-100 text-gray-600"}`}>
      {DIFFICULTY_LABEL[difficulty] ?? difficulty}
    </span>
  );
}
