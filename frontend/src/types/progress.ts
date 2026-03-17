// ─── Exercise instance (returned by /practice/ endpoint) ─────────────────────

export type ExerciseType = "fill_blank" | "multi_fill_blank" | "multiple_choice" | "comparison" | "drag_order";
export type Difficulty = "easy" | "medium" | "hard";

export interface ExerciseOption {
  id: string;
  text: string;
}

export interface MultiField {
  key: string;    // e.g. "a", "b", "c", "d"
  label: string;  // displayed next to the input
}

export interface ExerciseInstance {
  exercise_id: number;
  exercise_type: ExerciseType;
  difficulty: Difficulty;
  instance_token: string;
  display_mode?: "digit_click" | string;
  number_string?: string;

  // Common
  question: string;
  hint?: string;

  // fill_blank
  answer_input?: "number" | "expression";
  placeholder?: string;

  // multi_fill_blank
  fields?: MultiField[];

  // multiple_choice & comparison
  options?: ExerciseOption[];

  // comparison
  left?: string;
  right?: string;

  // drag_order
  items?: string[];
  order_direction?: "ascending" | "descending";
}

// ─── Practice session (returned by /practice/ endpoint) ───────────────────────

export interface PracticeSession {
  lesson_id: number;
  session_id: string;   // UUID — must be sent back with every attempt
  exercises: ExerciseInstance[];
  practice_minimum: number;
}

// ─── Attempt submission ────────────────────────────────────────────────────────

export interface AttemptPayload {
  exercise_id: number;
  instance_token: string;
  answer: string | string[] | Record<string, string>;
  session_id: string | null;
}

export interface AttemptResult {
  is_correct: boolean;
  correct_answer: string | null;
  tier_cleared: Difficulty | null;  // non-null when a tier was just unlocked
  error: string | null;
}

// ─── Category tier state ───────────────────────────────────────────────────────

export interface TierState {
  available: boolean;
  cleared: boolean;
}

export interface CategoryTiers {
  easy: TierState;
  medium: TierState;
  hard: TierState;
}

// ─── Category info (returned by /categories/ endpoint) ────────────────────────

export interface CategoryInfo {
  category: string;
  label: string;
  exercise_count: number;
  exercises_attempted: number;
  perfect_batches: number;
  tiers: CategoryTiers;
}

export interface LessonCategoriesResponse {
  lesson_id: number;
  lesson_title: string;
  categories: CategoryInfo[];
}

// ─── Dashboard ─────────────────────────────────────────────────────────────────

export interface UnitProgress {
  unit_id: number;
  unit_title: string;
  grade_number: number;
  total_lessons: number;
  completed_lessons: number;
}

export interface DashboardStats {
  total_lessons: number;
  completed_lessons: number;
  in_progress_lessons: number;
  exercises_attempted: number;
  perfect_batches: number;
  units: UnitProgress[];
}
