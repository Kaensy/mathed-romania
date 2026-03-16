// ─── Exercise instance (returned by /practice/ endpoint) ─────────────────────

export type ExerciseType = "fill_blank" | "multiple_choice" | "comparison" | "drag_order";
export type Difficulty = "easy" | "medium" | "hard";

export interface ExerciseOption {
  id: string;
  text: string;
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
  exercises: ExerciseInstance[];
  practice_minimum: number;
}

// ─── Attempt submission ────────────────────────────────────────────────────────

export interface AttemptPayload {
  exercise_id: number;
  instance_token: string;
  answer: string | string[];
}

export interface AttemptResult {
  is_correct: boolean;
  correct_answer: string | null;
  error: string | null;
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
  total_attempts: number;
  correct_attempts: number;
  accuracy_percent: number;
  units: UnitProgress[];
}
