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
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  Trophy,
  RotateCcw,
} from "lucide-react";
import api from "@/api/client";
import { InlineMath, BlockMath } from "@/lib/math";
import type { ExerciseInstance } from "@/types/progress";
import type {
  TestFinishResponse,
  TestStartResponse,
} from "@/types/test";

// ─── Main page ────────────────────────────────────────────────────────────────

export default function TestPage() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

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
      .catch(() => setError("Nu am putut încărca testul. Încearcă din nou."))
      .finally(() => setLoading(false));
  }, [testId]);

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
  if (error) return <TestError message={error} onRetry={() => navigate("/tests")} />;
  if (result) {
    return (
      <TestResultScreen
        result={result}
        exercises={exercises}
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
            onClick={() => navigate("/tests")}
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

// ─── Test exercise card ───────────────────────────────────────────────────────

interface TestExerciseCardProps {
  exercise: ExerciseInstance;
  answer: string | string[] | Record<string, string> | undefined;
    onAnswer: (answer: string | string[] | Record<string, string>) => void;

  index: number;
  total: number;
}

function TestExerciseCard({ exercise, answer, onAnswer, index, total }: TestExerciseCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-gray-400">
            Întrebarea {index + 1} din {total}
          </span>
          <DifficultyBadge difficulty={exercise.difficulty} />
        </div>
        <p className="text-gray-800 font-medium text-lg leading-relaxed">
          <InlineMath text={exercise.question} />
        </p>

        {/* Comparison display */}
        {exercise.exercise_type === "comparison" && exercise.left && exercise.right && (
          <div className="mt-4 flex items-center justify-center gap-6 py-3 bg-gray-50 rounded-xl">
            <BlockMath latex={exercise.left} />
            <span className="text-2xl text-gray-300">?</span>
            <BlockMath latex={exercise.right} />
          </div>
        )}
      </div>

      {/* Input */}

      <div className="px-6 py-5">

        {exercise.exercise_type === "multi_fill_blank" && exercise.fields && (
          exercise.display_mode === "inline_between" && exercise.between_value ? (
            // ── Inline between layout: [ ] < n < [ ] ──
            <div className="flex items-center justify-center gap-3 py-2 flex-wrap">
              <input
                type="text"
                value={((answer as Record<string, string>) ?? {})[exercise.fields[0].key] ?? ""}
                onChange={(e) =>
                  onAnswer({
                    ...((answer as Record<string, string>) ?? {}),
                    [exercise.fields[0].key]: e.target.value,
                  })
                }
                placeholder="?"
                className="w-24 px-3 py-2 rounded-xl border border-gray-200 bg-gray-50
                  text-gray-800 text-lg text-center font-semibold outline-none
                  focus:border-indigo-400 focus:bg-white transition-colors"
              />
              <span className="text-2xl text-gray-400 font-bold">&lt;</span>
              <span className="text-2xl text-gray-800 font-semibold px-2">
                <InlineMath text={`$${exercise.between_value}$`} />
              </span>
              <span className="text-2xl text-gray-400 font-bold">&lt;</span>
              <input
                type="text"
                value={((answer as Record<string, string>) ?? {})[exercise.fields[1].key] ?? ""}
                onChange={(e) =>
                  onAnswer({
                    ...((answer as Record<string, string>) ?? {}),
                    [exercise.fields[1].key]: e.target.value,
                  })
                }
                placeholder="?"
                className="w-24 px-3 py-2 rounded-xl border border-gray-200 bg-gray-50
                  text-gray-800 text-lg text-center font-semibold outline-none
                  focus:border-indigo-400 focus:bg-white transition-colors"
              />
            </div>
          ) : (
            // ── Default stacked layout ──
            <div className="space-y-3">
              {exercise.fields.map((field) => (
                <div key={field.key} className="flex items-center gap-3">
                  <span className="text-gray-700 font-medium w-6 text-right shrink-0">
                    {field.label} =
                  </span>
                  <input
                    type="text"
                    value={((answer as Record<string, string>) ?? {})[field.key] ?? ""}
                    onChange={(e) =>
                      onAnswer({
                        ...((answer as Record<string, string>) ?? {}),
                        [field.key]: e.target.value,
                      })
                    }
                    placeholder="cifră..."
                    className="flex-1 px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
                      text-gray-800 text-base outline-none focus:border-indigo-400 focus:bg-white
                      transition-colors"
                  />
                </div>
              ))}
            </div>
          )
        )}

        {exercise.exercise_type === "fill_blank" && (
          <input
            type="text"
            value={(answer as string) ?? ""}
            onChange={(e) => onAnswer(e.target.value)}
            placeholder={exercise.placeholder ?? "Răspuns..."}
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
              text-gray-800 text-base outline-none focus:border-indigo-400 focus:bg-white
              transition-colors"
          />
        )}

        {exercise.display_mode === "digit_click" && (
          <TestDigitClickInput
            numberString={exercise.number_string ?? ""}
            answer={(answer as string) ?? ""}
            onSelect={onAnswer}
          />
        )}

        {(exercise.exercise_type === "multiple_choice" || exercise.exercise_type === "comparison") &&
          exercise.display_mode !== "digit_click" &&
          exercise.options && exercise.options.length > 0 && (
          <div className="grid grid-cols-2 gap-3">
            {exercise.options.map((opt) => (
              <button
                key={opt.id}
                onClick={() => onAnswer(opt.id)}
                className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all text-left
                  ${answer === opt.id
                    ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                    : "border-gray-200 bg-gray-50 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50"
                  }`}
              >
                <InlineMath text={opt.text} />
              </button>
            ))}
          </div>
        )}

        {exercise.exercise_type === "drag_order" && exercise.items && (
          <TestDragOrderInput
            items={answer as string[] ?? [...exercise.items]}
            onChange={onAnswer}
          />
        )}
      </div>
    </div>
  );
}

// ─── Digit click (test version — no result state) ─────────────────────────────

function TestDigitClickInput({
  numberString,
  answer,
  onSelect,
}: {
  numberString: string;
  answer: string;
  onSelect: (pos: string) => void;
}) {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-center justify-center gap-1">
        {numberString.split("").map((digit, index) => {
          const posId = String(index);
          const isSelected = answer === posId;
          return (
            <button
              key={index}
              onClick={() => onSelect(posId)}
              style={{ width: "72px", height: "88px", fontSize: "2.5rem" }}
              className={`rounded-xl border-2 font-bold transition-all duration-150 select-none
                ${isSelected
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700 scale-105"
                  : "border-gray-200 bg-white text-gray-800 hover:border-indigo-400 hover:bg-indigo-50 cursor-pointer"
                }`}
            >
              {digit}
            </button>
          );
        })}
      </div>
      <p className="text-xs text-gray-400">Apăsați cifra corectă</p>
    </div>
  );
}

// ─── Drag order (test version) ────────────────────────────────────────────────

function TestDragOrderInput({
  items,
  onChange,
}: {
  items: string[];
  onChange: (items: string[]) => void;
}) {
  const dragItem = { current: null as number | null };
  const dragOver = { current: null as number | null };

  const handleDragEnd = () => {
    if (dragItem.current === null || dragOver.current === null) return;
    const newItems = [...items];
    const dragged = newItems.splice(dragItem.current, 1)[0];
    if (dragged !== undefined) newItems.splice(dragOver.current, 0, dragged);
    onChange(newItems);
    dragItem.current = null;
    dragOver.current = null;
  };

  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div
          key={`${item}-${i}`}
          draggable
          onDragStart={() => { dragItem.current = i; }}
          onDragEnter={() => { dragOver.current = i; }}
          onDragEnd={handleDragEnd}
          onDragOver={(e) => e.preventDefault()}
          className="flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-200
            bg-gray-50 text-sm font-medium text-gray-700 cursor-grab active:cursor-grabbing
            select-none"
        >
          <span className="text-gray-300">⠿</span>
          <InlineMath text={item} />
        </div>
      ))}
      <p className="text-xs text-gray-400 mt-1">Trage elementele pentru a le reordona.</p>
    </div>
  );
}

// ─── Result screen ────────────────────────────────────────────────────────────

interface TestResultScreenProps {
  result: TestFinishResponse;
  exercises: ExerciseInstance[];
  onRetry: () => void;
}

function TestResultScreen({ result, exercises, onRetry }: TestResultScreenProps) {
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
              onClick={() => navigate("/tests")}
              className="flex-1 py-3 rounded-xl border border-gray-200 text-gray-600
                font-medium hover:bg-gray-50 transition-colors text-sm"
            >
              Înapoi la teste
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

        {/* Per-question breakdown */}
        <h3 className="text-sm font-semibold text-gray-600 mb-3">Recapitulare</h3>
        <div className="space-y-3">
          {exercises.map((exercise, i) => {
            const answerRecord = result.answers[String(i)];
            const isCorrect = answerRecord?.is_correct ?? false;
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
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 font-medium">
                    <InlineMath text={exercise.question} />
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Răspunsul tău: <span className="font-mono">
                      {answerRecord?.answer !== undefined
                        ? exercise.display_mode === "digit_click" && exercise.number_string
                          ? exercise.number_string[parseInt(String(answerRecord.answer), 10)] ?? String(answerRecord.answer)
                          : String(answerRecord.answer)
                        : "—"}
                    </span>
                  </p>
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

// ─── Helpers ──────────────────────────────────────────────────────────────────

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const map: Record<string, string> = {
    easy: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    hard: "bg-red-100 text-red-700",
  };
  const label: Record<string, string> = {
    easy: "ușor",
    medium: "mediu",
    hard: "dificil",
  };
  return (
    <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium
      ${map[difficulty] ?? "bg-gray-100 text-gray-600"}`}
    >
      {label[difficulty] ?? difficulty}
    </span>
  );
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
