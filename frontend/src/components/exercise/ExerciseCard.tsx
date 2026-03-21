/**
 * ExerciseCard — renders a single interactive exercise instance.
 *
 * Used by: PracticePage, AdminPreviewPage
 *
 * Display modes (set via template "display_mode" field):
 *   comparison + drag_symbol  → drag <, =, > into the box between two numbers
 *   drag_order + drag_number  → drag number chips into ordered position slots
 */
import { useEffect, useRef, useState } from "react";
import { CheckCircle, XCircle, ChevronRight, Trophy } from "lucide-react";
import api from "@/api/client";
import { InlineMath } from "@/lib/math";
import type { AttemptResult, Difficulty, ExerciseInstance } from "@/types/progress";

// ─── Props ────────────────────────────────────────────────────────────────────

export interface ExerciseCardProps {
  exercise: ExerciseInstance;
  sessionId: string | null;
  onResult: (
    isCorrect: boolean,
    exercise: ExerciseInstance,
    answer: string | string[] | Record<string, string>,
    tierCleared: Difficulty | null,
  ) => void;
  onNext: () => void;
  isLast: boolean;
  previewMode?: boolean;
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function ExerciseCard({
  exercise,
  sessionId,
  onResult,
  onNext,
  isLast,
  previewMode = false,
}: ExerciseCardProps) {
  const initAnswer = (): string | string[] | Record<string, string> => {
    if (exercise.exercise_type === "drag_order") {
      // drag_number: empty slots; drag_order: shuffled item list
      if (exercise.display_mode === "drag_number") {
        return Array(exercise.items?.length ?? 0).fill("");
      }
      return [...(exercise.items ?? [])];
    }
    if (exercise.exercise_type === "multi_fill_blank") {
      return Object.fromEntries((exercise.fields ?? []).map((f) => [f.key, ""]));
    }
    return "";
  };

  const [answer, setAnswer] = useState<string | string[] | Record<string, string>>(initAnswer);
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!result) inputRef.current?.focus();
  }, [result]);

  const isAnswerEmpty = (): boolean => {
    if (typeof answer === "string") return answer.trim() === "";
    if (Array.isArray(answer)) {
      // "" marks an unfilled slot (drag_number), so any "" means incomplete
      return answer.length === 0 || answer.some((a) => a === "");
    }
    return Object.values(answer).some((v) => v.trim() === "");
  };

  const submit = async () => {
    if (submitting || result || isAnswerEmpty()) return;
    setSubmitting(true);
    try {
      const url = previewMode
        ? "/progress/exercises/attempt/?preview=true"
        : "/progress/exercises/attempt/";
      const res = await api.post<AttemptResult>(url, {
        exercise_id: exercise.exercise_id,
        instance_token: exercise.instance_token,
        answer: typeof answer === "string" ? answer.trim() : answer,
        session_id: sessionId,
      });
      setResult(res.data);
      onResult(
        res.data.is_correct,
        exercise,
        typeof answer === "string" ? answer.trim() : answer,
        res.data.tier_cleared ?? null,
      );
    } catch {
      setResult({ is_correct: false, correct_answer: null, tier_cleared: null, error: "Eroare de rețea." });
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      if (result) onNext();
      else submit();
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      {/* Question */}
      <div className="text-lg font-medium text-gray-800 mb-6 leading-relaxed">
        <InlineMath text={exercise.question} />
      </div>

      {/* Input area */}
      {!result && (
        <div className="space-y-4">
          {exercise.exercise_type === "multi_fill_blank" && exercise.fields ? (
            <div className="space-y-3">
              {exercise.fields.map((field) => (
                <div key={field.key} className="flex items-center gap-3">
                  <span className="text-gray-700 font-medium w-6 text-right shrink-0">
                    <InlineMath text={field.label} /> =
                  </span>
                  <input
                    type="text"
                    value={(answer as Record<string, string>)[field.key] ?? ""}
                    onChange={(e) =>
                      setAnswer((prev) => ({
                        ...(prev as Record<string, string>),
                        [field.key]: e.target.value,
                      }))
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="răspuns..."
                    className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none text-lg"
                  />
                </div>
              ))}
            </div>

          ) : exercise.display_mode === "digit_click" ? (
            <DigitClickInput
              numberString={exercise.number_string ?? ""}
              answer={answer as string}
              onSelect={setAnswer}
            />

          ) : exercise.exercise_type === "fill_blank" ? (
            <input
              ref={inputRef}
              type="text"
              value={answer as string}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={exercise.placeholder ?? "Răspunsul tău…"}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:outline-none text-lg"
            />

          ) : exercise.exercise_type === "comparison" && exercise.left && exercise.right ? (
            exercise.display_mode === "drag_symbol" ? (
              <DragSymbolInput
                left={exercise.left}
                right={exercise.right}
                answer={answer as string}
                onSelect={setAnswer}
              />
            ) : (
              <ComparisonInput
                left={exercise.left}
                right={exercise.right}
                options={exercise.options ?? []}
                answer={answer as string}
                onSelect={setAnswer}
              />
            )

          ) : exercise.exercise_type === "multiple_choice" && exercise.options ? (
            <div className="grid grid-cols-2 gap-3">
              {exercise.options.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setAnswer(opt.id)}
                  onKeyDown={handleKeyDown}
                  className={`px-4 py-3 rounded-xl border-2 text-sm font-medium transition-all text-left
                    ${answer === opt.id
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-gray-200 bg-gray-50 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50"
                    }`}
                >
                  <InlineMath text={opt.text} />
                </button>
              ))}
            </div>

          ) : exercise.exercise_type === "drag_order" && exercise.items ? (
            exercise.display_mode === "drag_number" ? (
              <DragNumberInput
                items={exercise.items}
                direction={exercise.order_direction ?? "ascending"}
                answer={answer as string[]}
                onChange={setAnswer}
              />
            ) : (
              <DragOrderInput
                items={answer as string[]}
                onChange={setAnswer}
              />
            )
          ) : null}

          <button
            onClick={submit}
            disabled={submitting || isAnswerEmpty()}
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? "Se verifică…" : "Verifică"}
          </button>
        </div>
      )}

      {/* Result feedback */}
      {result && (
        <>
          <div className={`rounded-xl p-4 mb-4 ${
            result.is_correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
          }`}>
            <div className="flex items-center gap-2 font-semibold">
              {result.is_correct ? (
                <><CheckCircle className="w-5 h-5 text-green-600" /><span className="text-green-700">Corect!</span></>
              ) : (
                <><XCircle className="w-5 h-5 text-red-600" /><span className="text-red-700">Incorect</span></>
              )}
            </div>
            {!result.is_correct && result.correct_answer && (
              <p className="text-sm text-red-600 mt-1">
                Răspuns corect: <strong><InlineMath text={result.correct_answer} /></strong>
              </p>
            )}
            <p className="text-sm text-gray-400 mt-1">
              Răspunsul tău:{" "}
              <span className="font-mono">
                {typeof answer === "object" && !Array.isArray(answer)
                  ? Object.entries(answer).map(([k, v]) => `${k}=${v}`).join(", ")
                  : Array.isArray(answer)
                  ? answer.join(", ")
                  : String(answer)}
              </span>
            </p>
          </div>

          <button
            onClick={onNext}
            onKeyDown={(e) => e.key === "Enter" && onNext()}
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            {isLast ? (
              <><Trophy className="w-4 h-4" /> Finalizează</>
            ) : (
              <><span>Următorul</span><ChevronRight className="w-4 h-4" /></>
            )}
          </button>
        </>
      )}
    </div>
  );
}

// ─── DragSymbolInput ──────────────────────────────────────────────────────────
// For: comparison + display_mode = "drag_symbol"
// Student drags or clicks <, =, > into the box between the two numbers.
// Clicking a placed symbol or the box clears the selection.

function DragSymbolInput({
  left,
  right,
  answer,
  onSelect,
}: {
  left: string;
  right: string;
  answer: string;
  onSelect: (val: string) => void;
}) {
  const SYMBOLS = ["<", "=", ">"];
  const dragging = useRef<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Numbers + drop zone row */}
      <div className="flex items-center justify-center gap-5">
        <div className="text-2xl font-bold text-gray-800 min-w-[80px] text-right">
          <InlineMath text={left} />
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => { if (dragging.current) onSelect(dragging.current); }}
          onClick={() => answer && onSelect("")}
          className={`w-16 h-16 rounded-2xl border-2 flex items-center justify-center
            text-2xl font-bold transition-all select-none
            ${answer
              ? "border-indigo-400 bg-indigo-50 text-indigo-700 cursor-pointer hover:border-red-300 hover:bg-red-50 hover:text-red-500"
              : "border-dashed border-gray-300 bg-gray-50 text-gray-300"
            }`}
        >
          {answer || "?"}
        </div>

        <div className="text-2xl font-bold text-gray-800 min-w-[80px] text-left">
          <InlineMath text={right} />
        </div>
      </div>

      {/* Symbol chips */}
      <div className="flex justify-center gap-4">
        {SYMBOLS.map((sym) => (
  sym === answer ? null : (
    <div
      key={sym}
      draggable
      onDragStart={() => { dragging.current = sym; }}
      onDragEnd={() => { dragging.current = null; }}
      onClick={() => onSelect(sym)}
      className="w-14 h-14 rounded-xl border-2 border-gray-200 bg-white text-gray-700
        flex items-center justify-center text-2xl font-bold cursor-grab
        active:cursor-grabbing select-none hover:border-indigo-300
        hover:bg-indigo-50 transition-all"
    >
      {sym}
    </div>
  )
))}
      </div>

      <p className="text-xs text-gray-400 text-center">
        Trage sau apasă simbolul · apasă caseta pentru a anula
      </p>
    </div>
  );
}

// ─── DragNumberInput ──────────────────────────────────────────────────────────
// For: drag_order + display_mode = "drag_number"
// N empty position slots at the top, shuffled number chips below.
// Drag or click a chip to place it in a slot.
// Click a filled slot to return its chip to the pool.
// Slot ↔ slot drag also works (swaps contents).

function DragNumberInput({
  items,
  direction,
  onChange,
}: {
  items: string[];
  direction: string;
  answer: string[];
  onChange: (items: string[]) => void;
}) {
  const [slots, setSlots] = useState<(string | null)[]>(
    () => Array(items.length).fill(null),
  );
  const [pool, setPool] = useState<string[]>(() => [...items]);
  const draggingFrom = useRef<{ source: "pool" | "slot"; index: number } | null>(null);

  const commit = (newSlots: (string | null)[], newPool: string[]) => {
    setSlots(newSlots);
    setPool(newPool);
    onChange(newSlots.map((s) => s ?? ""));
  };

  const placeInSlot = (
    slotIdx: number,
    item: string,
    fromPool: boolean,
    fromSlotIdx?: number,
  ) => {
    const newSlots = [...slots];
    const newPool = [...pool];
    const displaced = newSlots[slotIdx];

    if (fromPool) {
      const poolIdx = newPool.indexOf(item);
      if (poolIdx !== -1) newPool.splice(poolIdx, 1);
      if (displaced !== null) newPool.push(displaced);
    } else if (fromSlotIdx !== undefined) {
      // Swap: put displaced into the source slot
      newSlots[fromSlotIdx] = displaced;
    }

    newSlots[slotIdx] = item;
    commit(newSlots, newPool);
  };

  const returnToPool = (slotIdx: number) => {
    const item = slots[slotIdx];
    if (item === null) return;
    const newSlots = [...slots];
    newSlots[slotIdx] = null;
    commit(newSlots, [...pool, item]);
  };

  const directionLabel = direction === "ascending"
    ? "↑ crescător — de la cel mai mic la cel mai mare"
    : "↓ descrescător — de la cel mai mare la cel mai mic";

  return (
      <div className="space-y-4">
        <p className="text-xs text-center text-gray-500 font-medium">{directionLabel}</p>

        {/* Position slots */}
        <div className="flex flex-wrap justify-center gap-3">
          {slots.map((slot, i) => (
              <div key={i} className="flex items-center gap-3">
                <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => {
                      const src = draggingFrom.current;
                      if (!src) return;
                      const item = src.source === "pool" ? pool[src.index] : slots[src.index];
                      if (!item) return;
                      placeInSlot(i, item, src.source === "pool", src.source === "slot" ? src.index : undefined);
                    }}
                    onClick={() => slot && returnToPool(i)}
                    className={`w-20 h-14 rounded-xl border-2 flex items-center justify-center
          text-sm font-bold transition-all
          ${slot
                        ? "border-indigo-400 bg-indigo-50 text-indigo-700 cursor-pointer hover:border-red-300 hover:bg-red-50 hover:text-red-500"
                        : "border-dashed border-gray-300 bg-gray-50 text-gray-300 cursor-default"
                    }`}
                >
                  {slot ? <InlineMath text={slot}/> : <span className="text-lg">?</span>}
                </div>
                {i < slots.length - 1 && (
                    <span className="text-gray-400 font-bold text-lg">
          {direction === "ascending" ? "<" : ">"}
        </span>
                )}
              </div>
          ))}
        </div>

        {/* Number chips pool */}
        <div className="flex flex-wrap justify-center gap-3 min-h-[56px] py-1">
          {pool.map((item, i) => (
              <div
                  key={`${item}-${i}`}
                  draggable
                  onDragStart={() => {
                    draggingFrom.current = {source: "pool", index: i};
                  }}
                  onDragEnd={() => {
                    draggingFrom.current = null;
                  }}
                  onClick={() => {
                    const emptyIdx = slots.indexOf(null);
                    if (emptyIdx !== -1) placeInSlot(emptyIdx, item, true);
                  }}
                  className="w-20 h-14 rounded-xl border-2 border-gray-200 bg-white flex items-center
              justify-center text-sm font-bold text-gray-700 cursor-grab active:cursor-grabbing
              select-none hover:border-indigo-300 hover:bg-indigo-50 transition-all"
              >
                <InlineMath text={item}/>
              </div>
          ))}
          {pool.length === 0 && (
              <p className="text-xs text-gray-300 self-center italic">toate numerele au fost plasate</p>
          )}
        </div>

        <p className="text-xs text-gray-400 text-center">
          Trage sau apasă numerele · apasă un slot pentru a returna
        </p>
      </div>
  );
}

// ─── DigitClickInput ──────────────────────────────────────────────────────────

function DigitClickInput({
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
                    style={{width: "72px", height: "88px", fontSize: "2.5rem"}}
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

// ─── ComparisonInput (button fallback) ───────────────────────────────────────

function ComparisonInput({
  left,
  right,
  options,
  answer,
  onSelect,
}: {
  left: string;
  right: string;
  options: { id: string; text: string }[];
  answer: string;
  onSelect: (val: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-center gap-6 py-4 bg-gray-50 rounded-xl">
        <InlineMath text={left} />
        <span className="text-2xl text-gray-300">?</span>
        <InlineMath text={right} />
      </div>
      <div className="flex justify-center gap-3">
        {options.map((opt) => (
          <button
            key={opt.id}
            onClick={() => onSelect(opt.id)}
            className={`w-16 h-16 rounded-xl border-2 text-xl font-bold transition-all
              ${answer === opt.id
                ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                : "border-gray-200 bg-gray-50 text-gray-700 hover:border-indigo-300"
              }`}
          >
            {opt.text}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── DragOrderInput (reorder list) ────────────────────────────────────────────

function DragOrderInput({
  items,
  onChange,
}: {
  items: string[];
  onChange: (items: string[]) => void;
}) {
  const dragItem = useRef<number | null>(null);
  const dragOver = useRef<number | null>(null);

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
            bg-gray-50 text-sm font-medium text-gray-700 cursor-grab active:cursor-grabbing select-none"
        >
          <span className="text-gray-300">⠿</span>
          <InlineMath text={item} />
        </div>
      ))}
      <p className="text-xs text-gray-400 mt-1">Trage elementele pentru a le reordona.</p>
    </div>
  );
}
