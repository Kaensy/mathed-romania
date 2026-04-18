import { InlineMath, BlockMath } from "@/lib/math";
import type { ExerciseInstance } from "@/types/progress";

type AnswerValue = string | string[] | Record<string, string>;

interface TestExerciseCardProps {
  exercise: ExerciseInstance;
  answer: AnswerValue | undefined;
  onAnswer: (answer: AnswerValue) => void;
  index: number;
  total: number;
  label?: string;
  disabled?: boolean;
}

export default function TestExerciseCard({
  exercise,
  answer,
  onAnswer,
  index,
  total,
  label,
  disabled = false,
}: TestExerciseCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 pt-5 pb-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-gray-400">
            {label ?? `Întrebarea ${index + 1} din ${total}`}
          </span>
          <DifficultyBadge difficulty={exercise.difficulty} />
        </div>
        <p className="text-gray-800 font-medium text-lg leading-relaxed">
          <InlineMath text={exercise.question} />
        </p>

        {exercise.exercise_type === "comparison" && exercise.left && exercise.right && (
          <div className="mt-4 flex items-center justify-center gap-6 py-3 bg-gray-50 rounded-xl">
            <BlockMath latex={exercise.left} />
            <span className="text-2xl text-gray-300">?</span>
            <BlockMath latex={exercise.right} />
          </div>
        )}
      </div>

      <div className="px-6 py-5">
        {exercise.exercise_type === "multi_fill_blank" && exercise.fields && (
          exercise.display_mode === "inline_between" && exercise.between_value ? (
            <div className="flex items-center justify-center gap-3 py-2 flex-wrap">
              <input
                type="text"
                disabled={disabled}
                value={((answer as Record<string, string>) ?? {})[exercise.fields[0]!.key] ?? ""}
                onChange={(e) =>
                  onAnswer({
                    ...((answer as Record<string, string>) ?? {}),
                    [exercise.fields![0]!.key]: e.target.value,
                  })
                }
                placeholder="?"
                className="w-24 px-3 py-2 rounded-xl border border-gray-200 bg-gray-50
                  text-gray-800 text-lg text-center font-semibold outline-none
                  focus:border-indigo-400 focus:bg-white transition-colors
                  disabled:opacity-60 disabled:cursor-not-allowed"
              />
              <span className="text-2xl text-gray-400 font-bold">&lt;</span>
              <span className="text-2xl text-gray-800 font-semibold px-2">
                <InlineMath text={`$${exercise.between_value}$`} />
              </span>
              <span className="text-2xl text-gray-400 font-bold">&lt;</span>
              <input
                type="text"
                disabled={disabled}
                value={((answer as Record<string, string>) ?? {})[exercise.fields[1]!.key] ?? ""}
                onChange={(e) =>
                  onAnswer({
                    ...((answer as Record<string, string>) ?? {}),
                    [exercise.fields![1]!.key]: e.target.value,
                  })
                }
                placeholder="?"
                className="w-24 px-3 py-2 rounded-xl border border-gray-200 bg-gray-50
                  text-gray-800 text-lg text-center font-semibold outline-none
                  focus:border-indigo-400 focus:bg-white transition-colors
                  disabled:opacity-60 disabled:cursor-not-allowed"
              />
            </div>
          ) : (
            <div className="space-y-3">
              {exercise.fields.map((field) => (
                <div key={field.key} className="flex items-center gap-3">
                  <span className="text-gray-700 font-medium w-6 text-right shrink-0">
                    {field.label} =
                  </span>
                  <input
                    type="text"
                    disabled={disabled}
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
                      transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                </div>
              ))}
            </div>
          )
        )}

        {exercise.exercise_type === "fill_blank" && (
          <input
            type="text"
            disabled={disabled}
            value={(answer as string) ?? ""}
            onChange={(e) => onAnswer(e.target.value)}
            placeholder={exercise.placeholder ?? "Răspuns..."}
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50
              text-gray-800 text-base outline-none focus:border-indigo-400 focus:bg-white
              transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          />
        )}

        {exercise.display_mode === "digit_click" && (
          <TestDigitClickInput
            numberString={exercise.number_string ?? ""}
            answer={(answer as string) ?? ""}
            onSelect={onAnswer}
            disabled={disabled}
          />
        )}

        {(exercise.exercise_type === "multiple_choice" || exercise.exercise_type === "comparison") &&
          exercise.display_mode !== "digit_click" &&
          exercise.options && exercise.options.length > 0 && (
          <div className="grid grid-cols-2 gap-3">
            {exercise.options.map((opt) => (
              <button
                key={opt.id}
                disabled={disabled}
                onClick={() => onAnswer(opt.id)}
                className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all text-left
                  disabled:opacity-60 disabled:cursor-not-allowed
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
            items={(answer as string[]) ?? [...exercise.items]}
            onChange={onAnswer}
            disabled={disabled}
          />
        )}
      </div>
    </div>
  );
}

function TestDigitClickInput({
  numberString,
  answer,
  onSelect,
  disabled,
}: {
  numberString: string;
  answer: string;
  onSelect: (pos: string) => void;
  disabled?: boolean;
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
              disabled={disabled}
              onClick={() => onSelect(posId)}
              style={{ width: "72px", height: "88px", fontSize: "2.5rem" }}
              className={`rounded-xl border-2 font-bold transition-all duration-150 select-none
                disabled:opacity-60 disabled:cursor-not-allowed
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

function TestDragOrderInput({
  items,
  onChange,
  disabled,
}: {
  items: string[];
  onChange: (items: string[]) => void;
  disabled?: boolean;
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
          draggable={!disabled}
          onDragStart={() => { dragItem.current = i; }}
          onDragEnter={() => { dragOver.current = i; }}
          onDragEnd={handleDragEnd}
          onDragOver={(e) => e.preventDefault()}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-200
            bg-gray-50 text-sm font-medium text-gray-700 select-none
            ${disabled ? "opacity-60 cursor-not-allowed" : "cursor-grab active:cursor-grabbing"}`}
        >
          <span className="text-gray-300">⠿</span>
          <InlineMath text={item} />
        </div>
      ))}
      <p className="text-xs text-gray-400 mt-1">Trage elementele pentru a le reordona.</p>
    </div>
  );
}

export function DifficultyBadge({ difficulty }: { difficulty: string }) {
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
