/**
 * DailyTestPage — one test session per day, per student.
 *
 * Route: /daily
 *
 * Flow:
 *   1. GET /progress/daily/ — returns one of three statuses:
 *      - no_exercises: student has no practiced categories yet
 *      - completed:    today's test is already finished
 *      - in_progress:  list of pending exercises with slot indices
 *   2. Student answers all pending exercises, then submits.
 *   3. POST /progress/daily/submit/ grades each slot. Correct slots lock;
 *      wrong slots are regenerated. Review + "Continuă" refetches state.
 */
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle,
  Flame,
  Play,
  Sparkles,
  Trophy,
  XCircle,
} from "lucide-react";
import api from "@/api/client";
import TestExerciseCard from "@/components/exercise/TestExerciseCard";
import type {
  DailyAnswerValue,
  DailyExercise,
  DailySubmitResponse,
  DailyTestResponse,
} from "@/types/daily";

type AnswerMap = Record<number, DailyAnswerValue>;

// ─── Main page ────────────────────────────────────────────────────────────────

export default function DailyTestPage() {
  const [state, setState] = useState<DailyTestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [answers, setAnswers] = useState<AnswerMap>({});
  const [submitting, setSubmitting] = useState(false);
  const [starting, setStarting] = useState(false);
  const [justCompleted, setJustCompleted] = useState(false);

  // The batch of exercises being reviewed after a submit — separate from `state`
  // so we can show inline results even after state refreshes.
  const [reviewed, setReviewed] = useState<{
    submission: DailySubmitResponse;
    exercises: DailyExercise[];
    answers: AnswerMap;
  } | null>(null);

  const fetchDaily = () => {
    setLoading(true);
    setError(null);
    setReviewed(null);
    setAnswers({});
    api
      .get<DailyTestResponse>("/progress/daily/")
      .then((res) => setState(res.data))
      .catch(() => setError("Nu am putut încărca testul zilnic. Încearcă din nou."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDaily();
  }, []);

  if (loading) return <DailySkeleton />;
  if (error) return <DailyErrorState message={error} onRetry={fetchDaily} />;
  if (!state) return null;

  if (state.status === "no_exercises") {
    return <NoExercisesState message={state.message} />;
  }

  if (state.status === "available") {
    return (
      <AvailableState
        exerciseCount={state.exercise_count}
        starting={starting}
        onStart={async () => {
          setStarting(true);
          setError(null);
          try {
            const res = await api.post<DailyTestResponse>("/progress/daily/start/");
            setState(res.data);
          } catch {
            setError("Nu am putut porni testul zilei. Încearcă din nou.");
          } finally {
            setStarting(false);
          }
        }}
      />
    );
  }

  if (state.status === "completed") {
    return (
      <CompletedState
        completedAt={state.completed_at}
        exerciseCount={state.exercise_count}
        exercises={state.exercises}
        storedAnswers={state.answers}
        celebrateFresh={justCompleted}
      />
    );
  }

  // in_progress — possibly after submit (reviewed != null)
  if (reviewed) {
    return (
      <ReviewState
        submission={reviewed.submission}
        exercises={reviewed.exercises}
        submittedAnswers={reviewed.answers}
        onContinue={fetchDaily}
      />
    );
  }

  return (
    <InProgressState
      exercises={state.exercises}
      totalCount={state.total_count}
      completedCount={state.completed_count}
      answers={answers}
      setAnswers={setAnswers}
      submitting={submitting}
      onSubmit={async () => {
        setSubmitting(true);
        try {
          const payload = {
            answers: Object.fromEntries(
              Object.entries(answers).map(([k, v]) => [String(k), v])
            ),
          };
          const res = await api.post<DailySubmitResponse>(
            "/progress/daily/submit/",
            payload
          );
          if (res.data.is_completed) {
            setJustCompleted(true);
            fetchDaily();
          } else {
            setReviewed({
              submission: res.data,
              exercises: state.exercises,
              answers,
            });
          }
        } catch {
          setError("Eroare la trimiterea răspunsurilor. Încearcă din nou.");
        } finally {
          setSubmitting(false);
        }
      }}
    />
  );
}

// ─── In-progress state ────────────────────────────────────────────────────────

function InProgressState({
  exercises,
  totalCount,
  completedCount,
  answers,
  setAnswers,
  submitting,
  onSubmit,
}: {
  exercises: DailyExercise[];
  totalCount: number;
  completedCount: number;
  answers: AnswerMap;
  setAnswers: React.Dispatch<React.SetStateAction<AnswerMap>>;
  submitting: boolean;
  onSubmit: () => void;
}) {
  const navigate = useNavigate();
  const allAnswered = exercises.every((ex) => answers[ex.index] !== undefined);

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar
        onBack={() => navigate("/dashboard")}
        completed={completedCount}
        total={totalCount}
      />

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" />
            Testul zilei
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Răspunde la toate exercițiile și apasă „Trimite răspunsurile”.
          </p>
        </div>

        <div className="space-y-4">
          {exercises.map((exercise, i) => (
            <TestExerciseCard
              key={exercise.index}
              exercise={exercise}
              answer={answers[exercise.index]}
              onAnswer={(ans) =>
                setAnswers((prev) => ({ ...prev, [exercise.index]: ans }))
              }
              index={i}
              total={exercises.length}
              label={`Exercițiul ${i + 1} din ${exercises.length}`}
            />
          ))}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <p className="text-xs text-gray-400">
            {Object.keys(answers).length} din {exercises.length} completate
          </p>
          <button
            onClick={onSubmit}
            disabled={!allAnswered || submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-green-600
              text-white text-sm font-semibold hover:bg-green-700
              disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? "Se trimite..." : "Trimite răspunsurile"}
          </button>
        </div>
      </main>
    </div>
  );
}

// ─── Review state (after submit, some wrong) ─────────────────────────────────

function ReviewState({
  submission,
  exercises,
  submittedAnswers,
  onContinue,
}: {
  submission: DailySubmitResponse;
  exercises: DailyExercise[];
  submittedAnswers: AnswerMap;
  onContinue: () => void;
}) {
  const navigate = useNavigate();
  const correctCount = Object.values(submission.results).filter((r) => r.is_correct).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar
        onBack={() => navigate("/dashboard")}
        completed={submission.completed_count}
        total={submission.total_count}
      />

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-6 text-center">
          <h2 className="text-xl font-bold text-gray-900">Rezultate</h2>
          <p className="text-sm text-gray-500 mt-1">
            {correctCount} din {exercises.length} corecte în această rundă.
            {submission.pending_exercises.length > 0 &&
              " Continuă pentru a reîncerca exercițiile greșite."}
          </p>
        </div>

        <div className="space-y-4">
          {exercises.map((exercise, i) => {
            const result = submission.results[String(exercise.index)];
            if (!result) return null;
            const isCorrect = result.is_correct;
            const submitted = submittedAnswers[exercise.index];
            return (
              <div key={exercise.index} className="relative">
                <TestExerciseCard
                  exercise={exercise}
                  answer={submitted}
                  onAnswer={() => {}}
                  index={i}
                  total={exercises.length}
                  label={`Exercițiul ${i + 1} din ${exercises.length}`}
                  disabled
                />
                <div
                  className={`absolute top-4 right-4 flex items-center gap-1 bg-white
                    rounded-full shadow-sm px-2 py-0.5 text-xs font-semibold
                    ${isCorrect ? "text-green-600" : "text-red-600"}`}
                >
                  {isCorrect
                    ? <CheckCircle className="w-3.5 h-3.5" />
                    : <XCircle className="w-3.5 h-3.5" />
                  }
                  <span>{isCorrect ? "Corect" : "Greșit"}</span>
                </div>
                {!isCorrect && result.correct_answer && (
                  <p className="mt-2 ml-1 text-xs text-green-600">
                    Răspunsul corect:{" "}
                    <span className="font-mono">{result.correct_answer}</span>
                  </p>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onContinue}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold
              hover:bg-indigo-700 transition-colors"
          >
            Continuă
          </button>
        </div>
      </main>
    </div>
  );
}

// ─── Completed state ──────────────────────────────────────────────────────────

function CompletedState({
  completedAt,
  exerciseCount,
  exercises,
  storedAnswers,
  celebrateFresh = false,
}: {
  completedAt: string | null;
  exerciseCount: number;
  exercises?: DailyExercise[];
  storedAnswers?: Record<string, DailyAnswerValue>;
  celebrateFresh?: boolean;
}) {
  const navigate = useNavigate();
  const dateLabel = completedAt
    ? new Date(completedAt).toLocaleString("ro-RO", {
        hour: "2-digit",
        minute: "2-digit",
        day: "numeric",
        month: "long",
      })
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center">
          <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            {celebrateFresh
              ? <Sparkles className="w-10 h-10 text-green-600" />
              : <Trophy className="w-10 h-10 text-green-600" />
            }
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            Testul zilei completat!
          </h2>
          <p className="text-gray-500 mb-4">
            Ai rezolvat toate {exerciseCount} exercițiile de astăzi. Revino mâine pentru altele noi.
          </p>
          {dateLabel && (
            <p className="text-xs text-gray-400 mb-6">Completat la {dateLabel}</p>
          )}
          <button
            onClick={() => navigate("/dashboard")}
            className="w-full py-3 rounded-xl bg-indigo-600 text-white font-medium
              hover:bg-indigo-700 transition-colors text-sm"
          >
            Înapoi la pagina principală
          </button>
        </div>

        {exercises && exercises.length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-semibold text-gray-600 mb-3">
              Recapitulare
            </h3>
            <div className="space-y-4">
              {exercises.map((exercise, i) => (
                <div key={exercise.index} className="relative">
                  <TestExerciseCard
                    exercise={exercise}
                    answer={storedAnswers?.[String(exercise.index)]}
                    onAnswer={() => {}}
                    index={i}
                    total={exercises.length}
                    label={`Exercițiul ${i + 1} din ${exercises.length}`}
                    disabled
                  />
                  <div className="absolute top-4 right-4 flex items-center gap-1 text-green-600 bg-white rounded-full shadow-sm px-2 py-0.5 text-xs font-semibold">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Corect</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Available state (not yet started today) ─────────────────────────────────

function AvailableState({
  exerciseCount,
  starting,
  onStart,
}: {
  exerciseCount: number;
  starting: boolean;
  onStart: () => void;
}) {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center max-w-md w-full">
        <div className="w-20 h-20 rounded-full bg-orange-100 flex items-center justify-center mx-auto mb-4">
          <Flame className="w-10 h-10 text-orange-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">
          Testul zilei te așteaptă
        </h2>
        <p className="text-gray-500 mb-6">
          {exerciseCount} {exerciseCount === 1 ? "exercițiu" : "exerciții"} din categoriile
          pe care le-ai practicat. Începe când ești gata!
        </p>
        <button
          onClick={onStart}
          disabled={starting}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl
            bg-orange-500 text-white font-semibold hover:bg-orange-600
            disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
        >
          <Play className="w-4 h-4" />
          {starting ? "Se pregătește..." : "Începe testul zilei"}
        </button>
        <button
          onClick={() => navigate("/dashboard")}
          className="w-full mt-2 py-3 rounded-xl border border-gray-200 text-gray-600
            font-medium hover:bg-gray-50 transition-colors text-sm"
        >
          Înapoi la pagina principală
        </button>
      </div>
    </div>
  );
}

// ─── No-exercises state ───────────────────────────────────────────────────────

function NoExercisesState({ message }: { message: string }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center max-w-md w-full">
        <div className="w-20 h-20 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
          <Flame className="w-10 h-10 text-indigo-500" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          Încă nu ai un test zilnic
        </h2>
        <p className="text-gray-500 mb-6">{message}</p>
        <div className="flex flex-col gap-2">
          <Link
            to="/exercises"
            className="w-full py-3 rounded-xl bg-indigo-600 text-white font-medium
              hover:bg-indigo-700 transition-colors text-sm"
          >
            Începe cu câteva lecții!
          </Link>
          <Link
            to="/dashboard"
            className="w-full py-3 rounded-xl border border-gray-200 text-gray-600
              font-medium hover:bg-gray-50 transition-colors text-sm"
          >
            Înapoi la pagina principală
          </Link>
        </div>
      </div>
    </div>
  );
}

// ─── Small helpers ────────────────────────────────────────────────────────────

function TopBar({
  onBack,
  completed,
  total,
}: {
  onBack: () => void;
  completed: number;
  total: number;
}) {
  const pct = total > 0 ? (completed / total) * 100 : 0;
  return (
    <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
        <button
          onClick={onBack}
          className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Înapoi</span>
        </button>
        <div className="flex-1 text-center">
          <span className="text-sm text-gray-500 font-medium">Testul zilei</span>
        </div>
        <div className="text-sm text-gray-500">
          <span className="font-medium text-indigo-600">{completed}</span>
          <span>/{total} completate</span>
        </div>
      </div>
      <div className="h-1 bg-gray-100">
        <div
          className="h-1 bg-indigo-500 transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function DailySkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-14 bg-white border-b border-gray-200" />
      <div className="max-w-2xl mx-auto px-4 py-8 animate-pulse space-y-4">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <div className="h-5 bg-gray-200 rounded w-3/4" />
          <div className="h-12 bg-gray-200 rounded-xl" />
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <div className="h-5 bg-gray-200 rounded w-2/3" />
          <div className="h-12 bg-gray-200 rounded-xl" />
        </div>
      </div>
    </div>
  );
}

function DailyErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-500 font-medium">{message}</p>
        <button
          onClick={onRetry}
          className="mt-4 text-sm text-indigo-600 hover:underline"
        >
          Reîncearcă
        </button>
      </div>
    </div>
  );
}
