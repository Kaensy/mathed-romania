/**
 * PracticePage — exercise session for a topic.
 *
 * Route: /topic/:topicId/practice
 * State: { category?: string, difficulty?: Difficulty }  (passed via navigate)
 *
 * Flow:
 *   1. Fetch a batch of 5 randomised exercises (filtered by category + difficulty)
 *   2. Render one exercise at a time
 *   3. Submit each answer with the batch's session_id; show immediate feedback
 *   4. On completion, show results + whether a tier was cleared
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link, useLocation } from "react-router-dom";
import { ArrowLeft, Trophy, RotateCcw, Star } from "lucide-react";
import api from "@/api/client";
import type {
  Difficulty,
  ExerciseInstance,
  PracticeSession,
} from "@/types/progress";
import ExerciseCard from "@/components/exercise/ExerciseCard";

const DIFFICULTY_LABEL: Record<Difficulty, string> = {
  easy: "Ușor",
  medium: "Mediu",
  hard: "Greu",
};

// ─── Main page ────────────────────────────────────────────────────────────────

export default function PracticePage() {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Category and difficulty come from navigation state (set by ExerciseHubPage)
  const navState = location.state as { category?: string; difficulty?: Difficulty; from?: string } | null;
  const category = navState?.category ?? null;
  const difficulty = navState?.difficulty ?? null;
  const origin = navState?.from;

  /** Navigate back to ExerciseHubPage, preserving the origin chain. */
  const goBackToHub = () =>
    navigate(`/topic/${topicId}/exercises`, { state: origin ? { from: origin } : undefined });

  const [session, setSession] = useState<PracticeSession | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [finished, setFinished] = useState(false);

  const [questionResults, setQuestionResults] = useState<{
    exercise: ExerciseInstance;
    is_correct: boolean;
    answer: string | string[];
  }[]>([]);

  const [tierCleared, setTierCleared] = useState<Difficulty | null>(null);

  const fetchSession = () => {
    if (!topicId) return;
    setLoading(true);
    setError(null);

    const params = new URLSearchParams({ count: "5" });
    if (category !== null) params.set("category", category);
    if (difficulty !== null) params.set("difficulty", difficulty);

    api
      .get<PracticeSession>(`/progress/topics/${topicId}/practice/?${params}`)
      .then((res) => setSession(res.data))
      .catch(() => setError("Nu am putut încărca exercițiile. Încearcă din nou."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSession();
  }, [topicId]);

  const handleAnswerResult = (
    isCorrect: boolean,
    exercise: ExerciseInstance,
    answer: string | string[] | Record<string, string>,
    tierClearedFromAttempt: Difficulty | null,
  ) => {
    setQuestionResults((prev) => [...prev, { exercise, is_correct: isCorrect, answer }]);
    if (tierClearedFromAttempt) {
      setTierCleared(tierClearedFromAttempt);
    }
  };

  const handleNext = () => {
    const nextIndex = currentIndex + 1;
    if (nextIndex >= (session?.exercises.length ?? 0)) {
      setFinished(true);
      return;
    }
    setCurrentIndex(nextIndex);
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setQuestionResults([]);
    setFinished(false);
    setTierCleared(null);
    fetchSession();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 font-medium">{error}</p>
          <button onClick={goBackToHub} className="mt-4 text-indigo-600 hover:underline text-sm">
            Înapoi
          </button>
        </div>
      </div>
    );
  }

  if (finished) {
    const correctCount = questionResults.filter((r) => r.is_correct).length;
    const total = questionResults.length;
    const isPerfect = correctCount === total && total === 5;

    return (
      <CompletionScreen
        correctCount={correctCount}
        total={total}
        isPerfect={isPerfect}
        tierCleared={tierCleared}
        onRestart={handleRestart}
        topicId={topicId!}
        category={category}
        origin={origin}
      />
    );
  }

  const currentExercise = session.exercises[currentIndex];
  if (!currentExercise) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          <button
            onClick={goBackToHub}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <div className="flex-1" />
          <span className="text-sm text-gray-500">
            {currentIndex + 1} / {session.exercises.length}
          </span>
          {difficulty && (
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
              {DIFFICULTY_LABEL[difficulty]}
            </span>
          )}
        </div>
        {/* Progress bar */}
        <div className="h-1 bg-gray-100">
          <div
            className="h-1 bg-indigo-500 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / session.exercises.length) * 100}%` }}
          />
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <ExerciseCard
          key={currentIndex}
          exercise={currentExercise}
          sessionId={session.session_id}
          onResult={handleAnswerResult}
          onNext={handleNext}
          isLast={currentIndex === session.exercises.length - 1}
        />
      </main>
    </div>
  );
}


// ─── Completion screen ────────────────────────────────────────────────────────

interface CompletionScreenProps {
  correctCount: number;
  total: number;
  isPerfect: boolean;
  tierCleared: Difficulty | null;
  onRestart: () => void;
  topicId: string;
  category: string | null;
  origin?: string;
}

function CompletionScreen({
  correctCount,
  total,
  isPerfect,
  tierCleared,
  onRestart,
  topicId,
  category,
  origin,
}: CompletionScreenProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
        {isPerfect ? (
          <div className="text-5xl mb-4">🎉</div>
        ) : (
          <Trophy className="w-12 h-12 text-indigo-500 mx-auto mb-4" />
        )}

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {isPerfect ? "Sesiune perfectă!" : "Sesiune completă"}
        </h2>

        <p className="text-gray-500 mb-6">
          Ai răspuns corect la{" "}
          <span className="font-semibold text-gray-800">{correctCount} din {total}</span>{" "}
          exerciții.
        </p>

        {tierCleared && (
          <div className="mb-6 flex items-center gap-2 justify-center bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
            <Star className="w-5 h-5 text-amber-500 fill-amber-400" />
            <span className="font-semibold text-amber-800">
              Nivel {DIFFICULTY_LABEL[tierCleared]} deblocat!
            </span>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <button
            onClick={onRestart}
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Încearcă din nou
          </button>
          <Link
            to={`/topic/${topicId}/exercises`}
            state={origin ? { from: origin } : undefined}
            className="w-full py-3 border border-gray-200 text-gray-600 font-medium rounded-xl hover:bg-gray-50 transition-colors block"
          >
            Înapoi la exerciții
          </Link>
        </div>
      </div>
    </div>
  );
}