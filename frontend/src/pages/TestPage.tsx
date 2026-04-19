/**
 * TestPage — structured lesson/unit test.
 *
 * Route: /test/:testId
 *
 * Differences from PracticePage:
 *   - No immediate feedback after each answer
 *   - Progress bar shows answered count, not correct count
 *   - Can navigate back and change answers before finishing
 *   - Final screen reveals score, pass/fail, and per-question breakdown
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  Trophy,
  RotateCcw,
  Target,
} from "lucide-react";
import api from "@/api/client";
import { InlineMath } from "@/lib/math";
import type { ExerciseInstance } from "@/types/progress";
import type {
  TestFinishResponse,
  TestResultResponse,
  TestStartResponse,
} from "@/types/test";
import TestExerciseCard, { DifficultyBadge } from "@/components/exercise/TestExerciseCard";

// ─── Main page ────────────────────────────────────────────────────────────────

export default function TestPage() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const isReview = searchParams.get("review") === "true";
  const backTarget = (location.state as { from?: string } | null)?.from
    ?? (isReview ? "/test-history" : "/tests");

  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [exercises, setExercises] = useState<ExerciseInstance[]>([]);
  const [answers, setAnswers] = useState<Record<number, string | string[] | Record<string, string>>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TestFinishResponse | null>(null);

  useEffect(() => {
    if (!testId) return;
    setLoading(true);

    if (isReview) {
      api
        .get<TestResultResponse>(`/progress/tests/${testId}/result/`)
        .then((res) => {
          setExercises(res.data.exercise_instances);
          setResult({
            score: res.data.score,
            passed: res.data.passed,
            pass_threshold: res.data.pass_threshold,
            answers: res.data.answers,
          });
        })
        .catch(() => setError("Nu am putut încărca rezultatele testului."))
        .finally(() => setLoading(false));
      return;
    }

    api
      .post<TestStartResponse>(`/progress/tests/${testId}/start/`)
      .then((res) => {
        setAttemptId(res.data.attempt_id);
        setExercises(res.data.exercises);
        // Restore answers if resuming
        const restored: Record<number, string | string[]> = {};
        Object.entries(res.data.answers).forEach(([idx, rec]) => {
          restored[Number(idx)] = rec.answer;
        });
        setAnswers(restored);
      })
      .catch((err) => {
        if (err?.response?.data?.locked) {
          setError(
            "Testul nu este disponibil încă. Completează testul anterior pentru a-l debloca."
          );
        } else {
          setError("Nu am putut încărca testul. Încearcă din nou.");
        }
      })
      .finally(() => setLoading(false));
  }, [testId, isReview]);

  const handleAnswer = (index: number, ans: string | string[] | Record<string, string>) => {
    setAnswers((prev) => ({ ...prev, [index]: ans }));
  };

  const handleFinish = async () => {
    if (!attemptId || !testId) return;
    setSubmitting(true);

    // Submit all answers
    try {
      for (const [idx, answer] of Object.entries(answers)) {
        const exercise = exercises[Number(idx)];
        if (!exercise) continue;
        await api.post(`/progress/tests/${testId}/answer/`, {
          attempt_id: attemptId,
          index: Number(idx),
          instance_token: exercise.instance_token,
          answer,
        });
      }

      // Finish the attempt
      const res = await api.post<TestFinishResponse>(
        `/progress/tests/${testId}/finish/`,
        { attempt_id: attemptId }
      );
      setResult(res.data);
    } catch {
      setError("Eroare la trimiterea testului. Încearcă din nou.");
    } finally {
      setSubmitting(false);
    }
  };

  const answeredCount = Object.keys(answers).length;
  const totalCount = exercises.length;
  const allAnswered = answeredCount === totalCount;

  if (loading) return <TestSkeleton />;
  if (error) return <TestError message={error} onRetry={() => navigate(backTarget)} />;
  if (result) {
    return (
      <TestResultScreen
        result={result}
        exercises={exercises}
        backTo={backTarget}
        onRetry={() => {
          setResult(null);
          setAnswers({});
          setCurrentIndex(0);
          setAttemptId(null);
          setLoading(true);
          api
            .post<TestStartResponse>(`/progress/tests/${testId}/start/`)
            .then((res) => {
              setAttemptId(res.data.attempt_id);
              setExercises(res.data.exercises);
            })
            .finally(() => setLoading(false));
        }}
      />
    );
  }
  if (exercises.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Testul nu are exerciții configurate.</p>
          <button
            onClick={() => navigate("/tests")}
            className="mt-4 text-indigo-600 hover:underline text-sm"
          >
            Înapoi
          </button>
        </div>
      </div>
    );
  }

  const exercise = exercises[currentIndex];
  const currentAnswer = answers[currentIndex];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          <button
            onClick={() => navigate(backTarget)}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <div className="flex-1 text-center">
            <span className="text-sm text-gray-500 font-medium">Test</span>
          </div>
          <div className="text-sm text-gray-500">
            <span className="font-medium text-indigo-600">{answeredCount}</span>
            <span>/{totalCount} răspuns</span>
          </div>
        </div>
        {/* Progress bar — answered count */}
        <div className="h-1 bg-gray-100">
          <div
            className="h-1 bg-indigo-500 transition-all duration-300"
            style={{ width: `${(answeredCount / totalCount) * 100}%` }}
          />
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Question navigator */}
        <div className="flex gap-1.5 flex-wrap mb-6">
          {exercises.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i)}
              className={`w-8 h-8 rounded-lg text-xs font-semibold transition-colors
                ${i === currentIndex
                  ? "bg-indigo-600 text-white"
                  : answers[i] !== undefined
                  ? "bg-indigo-100 text-indigo-700"
                  : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                }`}
            >
              {i + 1}
            </button>
          ))}
        </div>

        {/* Exercise */}
        <TestExerciseCard
          exercise={exercise!}
          answer={currentAnswer}
          onAnswer={(ans) => handleAnswer(currentIndex, ans)}
          index={currentIndex}
          total={totalCount}
        />

        {/* Navigation */}
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={currentIndex === 0}
            className="flex items-center gap-1 px-4 py-2.5 rounded-xl border border-gray-200
              text-gray-600 text-sm font-medium hover:bg-gray-50 disabled:opacity-40
              disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Înapoi
          </button>

          <div className="flex-1" />

          {currentIndex < totalCount - 1 ? (
            <button
              onClick={() => setCurrentIndex((i) => i + 1)}
              className="flex items-center gap-1 px-4 py-2.5 rounded-xl bg-indigo-600
                text-white text-sm font-semibold hover:bg-indigo-700 transition-colors"
            >
              Următor
              <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              disabled={!allAnswered || submitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-green-600
                text-white text-sm font-semibold hover:bg-green-700
                disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? "Se trimite..." : "Finalizează testul"}
            </button>
          )}
        </div>

        {/* Finish shortcut if all answered and not on last */}
        {allAnswered && currentIndex < totalCount - 1 && (
          <div className="mt-3 text-center">
            <button
              onClick={handleFinish}
              disabled={submitting}
              className="text-sm text-green-600 hover:underline font-medium"
            >
              {submitting ? "Se trimite..." : "Toate răspunsurile completate — finalizează acum"}
            </button>
          </div>
        )}

        {/* Warning if not all answered */}
        {!allAnswered && currentIndex === totalCount - 1 && (
          <div className="mt-3 flex items-center gap-2 text-amber-600 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>
              Mai ai {totalCount - answeredCount} întrebări fără răspuns.
            </span>
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Result screen ────────────────────────────────────────────────────────────

interface TestResultScreenProps {
  result: TestFinishResponse;
  exercises: ExerciseInstance[];
  onRetry: () => void;
  backTo?: string;
}

function TestResultScreen({ result, exercises, onRetry, backTo = "/tests" }: TestResultScreenProps) {
  const navigate = useNavigate();
  const scoreInt = Math.round(Number(result.score));
  const romanianGrade = Math.round((scoreInt / 100) * 9 + 1);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Score card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center mb-6">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4
            ${result.passed ? "bg-green-100" : "bg-red-100"}`}
          >
            {result.passed
              ? <Trophy className="w-10 h-10 text-green-600" />
              : <XCircle className="w-10 h-10 text-red-500" />
            }
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            {result.passed ? "Test promovat!" : "Test nepromovat"}
          </h2>
          <p className="text-gray-500 mb-4">
            Nota estimată: <span className="font-bold text-indigo-600 text-xl">{romanianGrade}/10</span>
            <span className="text-gray-400 text-sm ml-2">({scoreInt}%)</span>
          </p>
          <p className="text-sm text-gray-400">
            Prag de promovare: {result.pass_threshold}%
          </p>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => navigate(backTo)}
              className="flex-1 py-3 rounded-xl border border-gray-200 text-gray-600
                font-medium hover:bg-gray-50 transition-colors text-sm"
            >
              Înapoi
            </button>
            {!result.passed && (
              <button
                onClick={onRetry}
                className="flex-1 py-3 rounded-xl border border-indigo-200 text-indigo-600
                  font-medium hover:bg-indigo-50 transition-colors text-sm
                  flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reîncearcă
              </button>
            )}
          </div>
        </div>

        <CategoryBreakdown exercises={exercises} answers={result.answers} />

        {/* Per-question breakdown */}
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Recapitulare</h3>
        <div className="space-y-3">
          {exercises.map((exercise, i) => {
            const answerRecord = result.answers[String(i)];
            const isCorrect = answerRecord?.is_correct ?? false;
            const isComparison = Boolean(exercise.left && exercise.right);
            const rawStudentAnswer = answerRecord?.answer;
            const studentAnswerText = isComparison && typeof rawStudentAnswer === "string" && rawStudentAnswer.length > 0
              ? `${exercise.left} ${rawStudentAnswer} ${exercise.right}`
              : formatAnswerForDisplay(rawStudentAnswer, exercise);
            const rawCorrectAnswer = answerRecord?.correct_answer;
            const correctAnswerText = rawCorrectAnswer
              ? isComparison
                ? `${exercise.left} ${rawCorrectAnswer} ${exercise.right}`
                : formatCorrectAnswerForDisplay(rawCorrectAnswer, exercise)
              : null;
            return (
              <div
                key={i}
                className={`bg-white rounded-xl border px-5 py-4 flex items-start gap-4
                  ${isCorrect ? "border-green-200" : "border-red-200"}`}
              >
                <div className={`mt-0.5 shrink-0 ${isCorrect ? "text-green-500" : "text-red-500"}`}>
                  {isCorrect
                    ? <CheckCircle className="w-5 h-5" />
                    : <XCircle className="w-5 h-5" />
                  }
                </div>
                <div className="flex-1 min-w-0 space-y-1.5">
                  {exercise.category_label && (
                    <p className="text-[11px] uppercase tracking-wide text-gray-400 font-medium">
                      {exercise.category_label}
                    </p>
                  )}
                  <p className="text-sm text-gray-800 font-medium break-words">
                    <InlineMath text={exercise.question} />
                  </p>
                  {(exercise.exercise_type === "comparison" || (exercise.left && exercise.right)) && (
                    <p className="text-sm text-gray-700 break-words">
                      <InlineMath text={exercise.left ?? ""} />
                      <span className="mx-2 text-gray-400">___</span>
                      <InlineMath text={exercise.right ?? ""} />
                    </p>
                  )}
                  {(exercise.exercise_type === "drag_order" || exercise.items) && exercise.items && exercise.items.length > 0 && (
                    <p className="text-sm text-gray-700 break-words">
                      <span className="text-gray-500">Numere: </span>
                      {exercise.items.map((item, idx) => (
                        <span key={idx}>
                          <InlineMath text={item} />
                          {idx < exercise.items!.length - 1 && <span className="text-gray-400">, </span>}
                        </span>
                      ))}
                    </p>
                  )}
                  <p className="text-xs text-gray-500">
                    Răspunsul tău:{" "}
                    <span className="text-gray-700">
                      {studentAnswerText !== null
                        ? renderAnswerValue(studentAnswerText, exercise)
                        : <span className="text-gray-400">—</span>}
                    </span>
                  </p>
                  {!isCorrect && correctAnswerText && (
                    <p className="text-xs text-green-600">
                      Răspuns corect:{" "}
                      <span className="font-medium">
                        {renderAnswerValue(correctAnswerText, exercise)}
                      </span>
                    </p>
                  )}
                </div>
                <DifficultyBadge difficulty={exercise.difficulty} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Category breakdown ──────────────────────────────────────────────────────

function CategoryBreakdown({
  exercises,
  answers,
}: {
  exercises: ExerciseInstance[];
  answers: TestFinishResponse["answers"];
}) {
  const navigate = useNavigate();

  const groups = new Map<
    string,
    { label: string; topicId: number | null; total: number; wrong: number }
  >();

  exercises.forEach((ex, i) => {
    const category = ex.category;
    if (!category) return;
    const existing = groups.get(category) ?? {
      label: ex.category_label ?? category,
      topicId: ex.topic_id ?? null,
      total: 0,
      wrong: 0,
    };
    existing.total += 1;
    if (answers[String(i)]?.is_correct === false) {
      existing.wrong += 1;
    }
    groups.set(category, existing);
  });

  const weakGroups = Array.from(groups.entries())
    .filter(([, g]) => g.wrong > 0)
    .sort(([, a], [, b]) => b.wrong - a.wrong);

  if (weakGroups.length === 0) return null;

  return (
    <section className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Target className="w-4 h-4 text-indigo-500" />
        <h3 className="text-sm font-semibold text-gray-600">Categorii de îmbunătățit</h3>
      </div>
      <div className="space-y-2">
        {weakGroups.map(([category, g]) => (
          <div
            key={category}
            className="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center gap-3"
          >
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-800 text-sm truncate" title={g.label}>
                {g.label}
              </p>
              <p className="text-xs text-red-500 mt-0.5">
                {g.wrong} din {g.total} {g.total === 1 ? "greșit" : "greșite"}
              </p>
            </div>
            {g.topicId !== null && (
              <button
                onClick={() =>
                  navigate(`/topic/${g.topicId}/practice`, {
                    state: { category, from: "test_result" },
                  })
                }
                className="shrink-0 text-xs font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-1.5 transition-colors"
              >
                Exersează
              </button>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatAnswerForDisplay(
  answer: string | string[] | undefined,
  exercise: ExerciseInstance,
): string | string[] | null {
  if (answer === undefined || answer === null) return null;

  if (Array.isArray(answer)) {
    if (answer.length === 0) return null;
    if (exercise.display_mode === "digit_click" && exercise.number_string) {
      const digits = answer
        .map((pos) => exercise.number_string![Number(pos)])
        .filter((d) => d !== undefined);
      return digits.length > 0 ? digits.join(", ") : null;
    }
    return answer;
  }

  const str = String(answer);
  return str.length > 0 ? str : null;
}

function formatCorrectAnswerForDisplay(
  correctAnswer: string,
  exercise: ExerciseInstance,
): string | string[] {
  if (exercise.exercise_type === "drag_order" && correctAnswer.includes(",")) {
    return correctAnswer.split(",").map((s) => s.trim());
  }
  return correctAnswer;
}

function renderAnswerValue(value: string | string[], exercise: ExerciseInstance) {
  if (Array.isArray(value)) {
    const separator =
      exercise.order_direction === "ascending"
        ? "<"
        : exercise.order_direction === "descending"
        ? ">"
        : "→";
    return value.map((item, idx) => (
      <span key={idx}>
        <InlineMath text={item} />
        {idx < value.length - 1 && <span className="mx-1 text-gray-400">{separator}</span>}
      </span>
    ));
  }
  return <InlineMath text={value} />;
}

function TestSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-14 bg-white border-b border-gray-200" />
      <div className="max-w-2xl mx-auto px-4 py-8 animate-pulse space-y-4">
        <div className="flex gap-1.5">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="w-8 h-8 bg-gray-200 rounded-lg" />
          ))}
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <div className="h-5 bg-gray-200 rounded w-3/4" />
          <div className="h-12 bg-gray-200 rounded-xl" />
        </div>
      </div>
    </div>
  );
}

function TestError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-500 font-medium">{message}</p>
        <button onClick={onRetry} className="mt-4 text-sm text-indigo-600 hover:underline">
          Înapoi
        </button>
      </div>
    </div>
  );
}
