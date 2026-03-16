/**
 * PracticePage — exercise session for a lesson.
 *
 * Route: /lesson/:lessonId/practice
 */
import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, XCircle, ChevronRight, Trophy, RotateCcw } from "lucide-react";
import api from "@/api/client";
import { InlineMath, BlockMath } from "@/lib/math";
import type {
  AttemptResult,
  ExerciseInstance,
  ExerciseOption,
  PracticeSession,
} from "@/types/progress";

// ─── Main page ────────────────────────────────────────────────────────────────

export default function PracticePage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<PracticeSession | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [finished, setFinished] = useState(false);

  const fetchSession = () => {
    if (!lessonId) return;
    setLoading(true);
    setError(null);
    api
      .get<PracticeSession>(`/progress/lessons/${lessonId}/practice/?count=10`)
      .then((res) => setSession(res.data))
      .catch(() => setError("Nu am putut încărca exercițiile. Încearcă din nou."))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchSession(); }, [lessonId]);

  const handleAnswerResult = (isCorrect: boolean) => {
    if (isCorrect) {
      const newCount = correctCount + 1;
      setCorrectCount(newCount);
      const minimum = session?.practice_minimum ?? 5;
      if (newCount >= minimum && currentIndex >= (session?.exercises.length ?? 0) - 1) {
        setFinished(true);
        return;
      }
    }
  };

  const handleNext = () => {
    const minimum = session?.practice_minimum ?? 5;
    if (currentIndex + 1 >= (session?.exercises.length ?? 0)) {
      if (correctCount >= minimum) {
        setFinished(true);
      } else {
        fetchSession();
        setCurrentIndex(0);
      }
      return;
    }
    setCurrentIndex((i) => i + 1);
  };

  const handleComplete = async () => {
    try {
      await api.post(`/progress/lessons/${lessonId}/complete/`);
    } catch {
      // Best-effort
    }
    navigate(`/lesson/${lessonId}`);
  };

  if (loading) return <PracticeSkeleton />;
  if (error) return <PracticeError message={error} onRetry={fetchSession} />;
  if (!session || session.exercises.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Această lecție nu are exerciții disponibile momentan.</p>
          <Link to={`/lesson/${lessonId}`} className="mt-4 inline-block text-indigo-600 hover:underline text-sm">
            ← Înapoi la lecție
          </Link>
        </div>
      </div>
    );
  }

  if (finished) {
    return (
      <CompletionScreen
        correctCount={correctCount}
        total={session.exercises.length}
        minimum={session.practice_minimum}
        onComplete={handleComplete}
        onRetry={() => { fetchSession(); setCurrentIndex(0); setCorrectCount(0); setFinished(false); }}
        lessonId={lessonId!}
      />
    );
  }

  const exercise = session.exercises[currentIndex];
  const minimum = session.practice_minimum;

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
          <div className="flex-1" />
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="font-medium text-indigo-600">{correctCount}</span>
            <span>/</span>
            <span>{minimum}</span>
            <span className="hidden sm:inline text-gray-400">corecte</span>
          </div>
        </div>
        <div className="h-1 bg-gray-100">
          <div
            className="h-1 bg-indigo-500 transition-all duration-500"
            style={{ width: `${Math.min((correctCount / minimum) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Exercise */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-4 flex items-center justify-between text-xs text-gray-400">
          <span>Exercițiu {currentIndex + 1} din {session.exercises.length}</span>
          <DifficultyBadge difficulty={exercise.difficulty} />
        </div>
        <ExerciseCard
          key={`${exercise.exercise_id}-${currentIndex}`}
          exercise={exercise}
          onResult={handleAnswerResult}
          onNext={handleNext}
        />
      </main>
    </div>
  );
}

// ─── Exercise card ────────────────────────────────────────────────────────────

interface ExerciseCardProps {
  exercise: ExerciseInstance;
  onResult: (isCorrect: boolean) => void;
  onNext: () => void;
}

function ExerciseCard({ exercise, onResult, onNext }: ExerciseCardProps) {
  const [answer, setAnswer] = useState<string | string[]>(
    exercise.exercise_type === "drag_order" ? [...(exercise.items ?? [])] : ""
  );
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (exercise.exercise_type === "fill_blank") {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [exercise.exercise_type]);

  const handleSubmit = async () => {
    if (submitting || result) return;
    const trimmed = typeof answer === "string" ? answer.trim() : answer;
    if (!trimmed || (Array.isArray(trimmed) && trimmed.length === 0)) return;

    setSubmitting(true);
    try {
      const res = await api.post<AttemptResult>("/progress/exercises/attempt/", {
        exercise_id: exercise.exercise_id,
        instance_token: exercise.instance_token,
        answer: trimmed,
      });
      setResult(res.data);
      onResult(res.data.is_correct);
    } catch {
      // Network error — allow retry
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      if (result) onNext();
      else handleSubmit();
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Question */}
      <div className="px-6 pt-6 pb-4">
        <p className="text-gray-800 font-medium text-lg leading-relaxed">
          <InlineMath text={exercise.question} />
        </p>
        {exercise.hint && !result && (
          <p className="mt-2 text-sm text-gray-400 italic">
            <InlineMath text={exercise.hint} />
          </p>
        )}

        {/* Comparison display */}
        {exercise.exercise_type === "comparison" && exercise.left && exercise.right && (
          <div className="mt-4 flex items-center justify-center gap-6 py-3 bg-gray-50 rounded-xl">
            <div className="text-center">
              <BlockMath latex={exercise.left} />
            </div>
            <span className="text-2xl text-gray-300">?</span>
            <div className="text-center">
              <BlockMath latex={exercise.right} />
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="px-6 pb-6">

        {/* Fill blank */}
        {exercise.exercise_type === "fill_blank" && (
          <input
            ref={inputRef}
            type="text"
            value={answer as string}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!!result}
            placeholder={exercise.placeholder ?? "Răspuns..."}
            className={`w-full px-4 py-3 rounded-xl border text-gray-800 text-base transition-colors outline-none
              ${result
                ? result.is_correct
                  ? "border-green-400 bg-green-50"
                  : "border-red-400 bg-red-50"
                : "border-gray-200 bg-gray-50 focus:border-indigo-400 focus:bg-white"
              }`}
          />
        )}

        {/* Digit click */}
        {exercise.display_mode === "digit_click" && (
          <DigitClickInput
            numberString={exercise.number_string ?? ""}
            answer={answer as string}
            onSelect={(pos) => { if (!result) setAnswer(pos); }}
            result={result}
          />
        )}

        {/* Standard multiple choice / comparison options */}
        {(exercise.exercise_type === "multiple_choice" || exercise.exercise_type === "comparison") &&
          exercise.display_mode !== "digit_click" &&
          exercise.options && exercise.options.length > 0 && (
          <div className="grid grid-cols-2 gap-3 mt-2">
            {exercise.options.map((opt) => {
              const isSelected = answer === opt.id;
              const isCorrectOpt = result && result.correct_answer === opt.id;
              const isWrongSelected = result && !result.is_correct && isSelected;
              return (
                <button
                  key={opt.id}
                  onClick={() => { if (!result) setAnswer(opt.id); }}
                  disabled={!!result}
                  className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all text-left
                    ${isCorrectOpt
                      ? "border-green-400 bg-green-50 text-green-700"
                      : isWrongSelected
                      ? "border-red-400 bg-red-50 text-red-700"
                      : isSelected
                      ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                      : "border-gray-200 bg-gray-50 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50"
                    }`}
                >
                  <InlineMath text={opt.text} />
                </button>
              );
            })}
          </div>
        )}

        {/* Drag to order */}
        {exercise.exercise_type === "drag_order" && exercise.items && (
          <DragOrderInput
            items={answer as string[]}
            onChange={setAnswer}
            disabled={!!result}
            result={result}
            correctOrder={result?.correct_answer?.split(", ") ?? []}
          />
        )}

        {/* Feedback */}
        {result && (
          <div className={`mt-4 flex items-start gap-3 p-3 rounded-xl
            ${result.is_correct ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}
          >
            {result.is_correct
              ? <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
              : <XCircle className="w-5 h-5 shrink-0 mt-0.5" />
            }
            <div>
              <p className="font-medium text-sm">
                {result.is_correct ? "Corect! Bine lucrat!" : "Răspuns greșit."}
              </p>
              {!result.is_correct && result.correct_answer && (
                <p className="text-sm mt-1 opacity-80">
                  Răspuns corect: poziția {result.correct_answer}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="mt-4 flex gap-3">
          {!result ? (
            <button
              onClick={handleSubmit}
              disabled={submitting || (typeof answer === "string" ? !answer.trim() : answer.length === 0)}
              className="flex-1 py-3 rounded-xl bg-indigo-600 text-white font-semibold text-sm
                hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? "Se verifică..." : "Verifică"}
            </button>
          ) : (
            <button
              onClick={onNext}
              className="flex-1 py-3 rounded-xl bg-indigo-600 text-white font-semibold text-sm
                hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              Continuă
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Digit click input ────────────────────────────────────────────────────────

interface DigitClickProps {
  numberString: string;
  answer: string;
  onSelect: (position: string) => void;
  result: AttemptResult | null;
}

function DigitClickInput({ numberString, answer, onSelect, result }: DigitClickProps) {
  return (
    <div className="mt-8 flex flex-col items-center gap-6">
      <div className="flex items-center justify-center gap-1">
        {numberString.split("").map((digit, index) => {
          const posId = String(index);
          const isSelected = answer === posId;
          const isCorrect = result && result.correct_answer === posId;
          const isWrong = result && !result.is_correct && isSelected;

          return (
            <button
              key={index}
              onClick={() => onSelect(posId)}
              disabled={!!result}
              style={{ width: "72px", height: "88px", fontSize: "2.5rem" }}
              className={`
                rounded-xl border-2 font-bold transition-all duration-150 select-none
                ${isCorrect
                  ? "border-green-400 bg-green-50 text-green-700"
                  : isWrong
                  ? "border-red-400 bg-red-50 text-red-700"
                  : isSelected
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                  : result
                  ? "border-gray-200 bg-gray-50 text-gray-400"
                  : "border-gray-200 bg-white text-gray-800 hover:border-indigo-400 hover:bg-indigo-50 cursor-pointer"
                }
              `}
            >
              {digit}
            </button>
          );
        })}
      </div>
      {!result && (
        <p className="text-xs text-gray-400">Apăsați cifra corectă</p>
      )}
    </div>
  );
}

// ─── Drag-to-order input ──────────────────────────────────────────────────────

interface DragOrderProps {
  items: string[];
  onChange: (items: string[]) => void;
  disabled: boolean;
  result: AttemptResult | null;
  correctOrder: string[];
}

function DragOrderInput({ items, onChange, disabled, result, correctOrder }: DragOrderProps) {
  const dragItem = useRef<number | null>(null);
  const dragOver = useRef<number | null>(null);

  const handleDragStart = (index: number) => { dragItem.current = index; };
  const handleDragEnter = (index: number) => { dragOver.current = index; };

  const handleDragEnd = () => {
    if (dragItem.current === null || dragOver.current === null) return;
    const newItems = [...items];
    const dragged = newItems.splice(dragItem.current, 1)[0];
    newItems.splice(dragOver.current, 0, dragged);
    onChange(newItems);
    dragItem.current = null;
    dragOver.current = null;
  };

  return (
    <div className="mt-3 space-y-2">
      {items.map((item, i) => {
        const isCorrectPos = result && correctOrder[i] === item;
        const isWrongPos = result && !result.is_correct && correctOrder[i] !== item;

        return (
          <div
            key={`${item}-${i}`}
            draggable={!disabled}
            onDragStart={() => handleDragStart(i)}
            onDragEnter={() => handleDragEnter(i)}
            onDragEnd={handleDragEnd}
            onDragOver={(e) => e.preventDefault()}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl border text-sm font-medium
              transition-colors select-none
              ${disabled ? "" : "cursor-grab active:cursor-grabbing"}
              ${isCorrectPos
                ? "border-green-400 bg-green-50 text-green-700"
                : isWrongPos
                ? "border-red-400 bg-red-50 text-red-700"
                : "border-gray-200 bg-gray-50 text-gray-700"
              }`}
          >
            {!disabled && <span className="text-gray-300">⠿</span>}
            <InlineMath text={item} />
          </div>
        );
      })}
      <p className="text-xs text-gray-400 mt-1">Trage elementele pentru a le reordona.</p>
    </div>
  );
}

// ─── Completion screen ────────────────────────────────────────────────────────

interface CompletionScreenProps {
  correctCount: number;
  total: number;
  minimum: number;
  onComplete: () => void;
  onRetry: () => void;
  lessonId: string;
}

function CompletionScreen({ correctCount, total, minimum, onComplete, onRetry }: CompletionScreenProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 max-w-md w-full text-center">
        <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
          <Trophy className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Lecție finalizată!</h2>
        <p className="text-gray-500 mb-6">
          Ai răspuns corect la{" "}
          <span className="font-semibold text-indigo-600">{correctCount}</span>{" "}
          din {total} exerciții (minim necesar: {minimum}).
        </p>
        <div className="flex flex-col gap-3">
          <button
            onClick={onComplete}
            className="w-full py-3 rounded-xl bg-indigo-600 text-white font-semibold
              hover:bg-indigo-700 transition-colors"
          >
            Marchează lecția ca finalizată
          </button>
          <button
            onClick={onRetry}
            className="w-full py-3 rounded-xl border border-gray-200 text-gray-600 font-medium
              hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Mai exersează
          </button>
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
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${map[difficulty] ?? "bg-gray-100 text-gray-600"}`}>
      {label[difficulty] ?? difficulty}
    </span>
  );
}

function PracticeSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-14 bg-white border-b border-gray-200" />
      <div className="max-w-2xl mx-auto px-4 py-8 animate-pulse">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
          <div className="h-6 bg-gray-200 rounded w-3/4" />
          <div className="h-12 bg-gray-200 rounded-xl" />
          <div className="h-10 bg-gray-200 rounded-xl" />
        </div>
      </div>
    </div>
  );
}

function PracticeError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-500 font-medium">{message}</p>
        <button onClick={onRetry} className="mt-4 text-sm text-indigo-600 hover:underline">
          Reîncearcă
        </button>
      </div>
    </div>
  );
}
