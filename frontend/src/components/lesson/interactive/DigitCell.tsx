/**
 * DigitCell — a single, fixed-width cell in a notebook-grid digit layout.
 *
 * Two variants share a layout so column arithmetic, exercise input mode, and the
 * ciornă can stack DigitCells freely without rewriting cell styling each time.
 *
 *   - `display`  : renders a fixed digit (or empty), supports the column-arithmetic
 *                  styles already in use — carry/result tone+emphasis, reveal-opacity
 *                  gating, active-column highlight.
 *   - `editable` : an <input> styled to look like a cell. Reports digit keystrokes
 *                  and Backspace via callbacks; the parent owns the digit model
 *                  (prepend / overtype / trim semantics).
 *
 * Editable cells bring up the numeric keypad on mobile (inputMode="numeric") and
 * select-on-focus so the next keystroke replaces the current value — the calculator
 * grow/shrink flow lives in the parent's onDigit / onBackspace handlers.
 */

type Size = "sm" | "md";
type Emphasis = "normal" | "bold";
type Tone = "default" | "rose";

interface BaseProps {
  /** Optional left border (when stacking cells in a row). */
  borderLeft?: boolean;
  /** Active-column highlight tint. */
  active?: boolean;
  /** Cell height tier. `md` = h-9 / text-lg; `sm` = h-5 / text-[0.7rem]. */
  size?: Size;
}

export interface DigitCellDisplayProps extends BaseProps {
  variant?: "display";
  /** Digit to render, or null for empty. */
  digit: number | null | undefined;
  /** When false, the digit fades to opacity-0 (for reveal animations). Default true. */
  revealed?: boolean;
  emphasis?: Emphasis;
  tone?: Tone;
}

export interface DigitCellEditableProps extends BaseProps {
  variant: "editable";
  /** Current digit, or null when the cell is empty (e.g., the grow slot). */
  digit: number | null;
  /** Fired when the user types a digit 0–9. */
  onDigit: (d: number) => void;
  /** Fired on Backspace. The parent decides what to trim. */
  onBackspace: () => void;
  /** Accessible label for screen readers. */
  ariaLabel?: string;
  /** Faint glyph rendered when digit is null. Defaults to a centered middle-dot. */
  placeholder?: string;
  /** Callback ref to the underlying <input>. Parents use this to drive chain-typing focus. */
  inputRef?: (el: HTMLInputElement | null) => void;
  /** Visual weight — `bold` for result-row cells. */
  emphasis?: Emphasis;
}

export type DigitCellProps = DigitCellDisplayProps | DigitCellEditableProps;

const SIZE_HEIGHT: Record<Size, string> = { sm: "h-5", md: "h-9" };
const SIZE_TEXT: Record<Size, string> = { sm: "text-[0.7rem]", md: "text-lg" };
const SIZE_LEADING: Record<Size, string> = { sm: "leading-5", md: "leading-9" };

const TONE_COLOR: Record<Tone, string> = {
  default: "text-gray-900",
  rose: "text-rose-500",
};

export default function DigitCell(props: DigitCellProps) {
  const size: Size = props.size ?? "md";
  const heightCls = SIZE_HEIGHT[size];
  const textSizeCls = SIZE_TEXT[size];
  const leadingCls = SIZE_LEADING[size];
  const borderCls = props.borderLeft ? "border-l border-blue-200" : "";
  const activeCls = props.active ? "bg-blue-200/60" : "";

  if (props.variant === "editable") {
    return <EditableCell {...props} heightCls={heightCls} textSizeCls={textSizeCls} leadingCls={leadingCls} borderCls={borderCls} activeCls={activeCls} />;
  }

  const tone = props.tone ?? "default";
  const toneCls = TONE_COLOR[tone];
  const emphasisCls = (props.emphasis ?? "normal") === "bold" ? "font-semibold" : "";
  const revealed = props.revealed ?? true;
  const opacityCls = revealed ? "opacity-100" : "opacity-0";

  return (
    <div
      className={[
        "w-8 flex items-center justify-center transition-colors duration-200",
        heightCls,
        textSizeCls,
        toneCls,
        emphasisCls,
        borderCls,
        activeCls,
      ].join(" ")}
    >
      <span className={"transition-opacity duration-200 " + opacityCls}>
        {props.digit ?? ""}
      </span>
    </div>
  );
}

function EditableCell({
  digit,
  onDigit,
  onBackspace,
  ariaLabel,
  placeholder,
  inputRef,
  emphasis,
  heightCls,
  textSizeCls,
  leadingCls,
  borderCls,
  activeCls,
}: DigitCellEditableProps & {
  heightCls: string;
  textSizeCls: string;
  leadingCls: string;
  borderCls: string;
  activeCls: string;
}) {
  const value = digit === null ? "" : String(digit);
  const emphasisCls = emphasis === "bold" ? "font-semibold" : "";

  return (
    <input
      ref={inputRef}
      type="text"
      inputMode="numeric"
      autoComplete="off"
      aria-label={ariaLabel}
      placeholder={placeholder ?? "·"}
      value={value}
      // Select-on-focus so a fresh keystroke replaces the current digit (calculator feel).
      onFocus={(e) => e.currentTarget.select()}
      // Tapping the cell on touch devices doesn't always fire focus reliably for select();
      // explicit selection on pointer-up covers that path.
      onPointerUp={(e) => {
        const el = e.currentTarget;
        // Defer to next tick so the browser-native click-to-cursor doesn't undo our select.
        window.setTimeout(() => {
          if (document.activeElement === el) el.select();
        }, 0);
      }}
      onKeyDown={(e) => {
        if (e.key === "Backspace") {
          e.preventDefault();
          onBackspace();
        }
      }}
      onChange={(e) => {
        const v = e.target.value;
        if (v === "") return; // empty changes are handled via Backspace path
        const last = v.charAt(v.length - 1);
        if (last >= "0" && last <= "9") onDigit(Number(last));
      }}
      className={[
        "w-8 text-center font-mono p-0 m-0 bg-transparent",
        "transition-colors duration-200",
        "text-gray-900",
        "placeholder:text-gray-300",
        "focus:bg-blue-100/70 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:ring-inset",
        heightCls,
        textSizeCls,
        leadingCls,
        borderCls,
        activeCls,
        emphasisCls,
      ].join(" ")}
    />
  );
}
