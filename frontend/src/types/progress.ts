// ─── Exercise instance ────────────────────────────────────────────────────────

export type ExerciseType =
  | "fill_blank"
  | "multi_fill_blank"
  | "multiple_choice"
  | "comparison"
  | "drag_order";

export type Difficulty = "easy" | "medium" | "hard";

export interface ExerciseOption {
  id: string;
  text: string;
}

export interface MultiField {
  key: string;
  label: string;
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
  follow_up_question?: string;

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

// ─── Practice session ─────────────────────────────────────────────────────────

export interface PracticeSession {
  topic_id: number;
  session_id: string;
  exercises: ExerciseInstance[];
  practice_minimum: number;
}

// ─── Attempt submission ───────────────────────────────────────────────────────

export interface AttemptPayload {
  exercise_id: number;
  instance_token: string;
  answer: string | string[] | Record<string, string>;
  session_id: string | null;
}

export interface FollowUp {
    question: string;
    expected: string;
}

export interface AttemptResult {
    is_correct: boolean;
    correct_answer: string | null;
    follow_up?: FollowUp | null;
    tier_cleared: Difficulty | null;
    error: string | null;
  }

// ─── Category tier state ──────────────────────────────────────────────────────

export interface TierState {
  available: boolean;
  cleared: boolean;
}

export interface CategoryTiers {
  easy: TierState;
  medium: TierState;
  hard: TierState;
}

export interface CategoryInfo {
  category: string;
  label: string;
  exercise_count: number;
  exercises_attempted: number;
  perfect_batches: number;
  tiers: CategoryTiers;
}

export interface TopicCategoriesResponse {
  topic_id: number;
  topic_title: string;
  categories: CategoryInfo[];
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

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

// ─── Exercises overview ───────────────────────────────────────────────────────

export interface TopicExerciseSummary {
  topic_id: number;
  topic_title: string;
  unit_id: number;
  unit_title: string;
  unit_order: number;
  topic_order: number;
  total_categories: number;
  completed_categories: number;
  exercises_attempted: number;
}

export interface ExercisesOverviewResponse {
  topics: TopicExerciseSummary[];
}

// ─── Tests overview ───────────────────────────────────────────────────────────

export interface TopicTestSummary {
  test_id: number;
  topic_id: number;
  topic_title: string;
  unit_id: number;
  unit_title: string;
  unit_order: number;
  topic_order: number;
  pass_threshold: number;
  time_limit_minutes: number | null;
  attempts_count: number;
  passed: boolean | null;
  best_score: number | null;
}

export interface TestsOverviewResponse {
  tests: TopicTestSummary[];
}
