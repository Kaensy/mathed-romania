// ─── Daily test types ─────────────────────────────────────────────────────────

import type { ExerciseInstance } from "@/types/progress";

export interface DailyExercise extends ExerciseInstance {
  index: number;
}

// ─── GET /progress/daily/ ────────────────────────────────────────────────────

export interface DailyTestNoExercises {
  status: "no_exercises";
  message: string;
}

export interface DailyTestAvailable {
  status: "available";
  exercise_count: number;
}

export interface DailyTestCompleted {
  status: "completed";
  completed_at: string;
  exercise_count: number;
  completed_count: number;
  exercises: DailyExercise[];
  completed_indices: number[];
  answers: Record<string, DailyAnswerValue>;
}

export interface DailyTestInProgress {
  status: "in_progress";
  exercises: DailyExercise[];
  completed_count: number;
  total_count: number;
}

export type DailyTestResponse =
  | DailyTestNoExercises
  | DailyTestAvailable
  | DailyTestCompleted
  | DailyTestInProgress;

// ─── POST /progress/daily/submit/ ────────────────────────────────────────────

export type DailyAnswerValue = string | string[] | Record<string, string>;

export interface DailySubmitPayload {
  answers: Record<string, DailyAnswerValue>;
}

export interface DailySubmitResult {
  is_correct: boolean;
  correct_answer: string | null;
}

export interface DailySubmitResponse {
  results: Record<string, DailySubmitResult>;
  is_completed: boolean;
  completed_count: number;
  total_count: number;
  pending_exercises: DailyExercise[];
}
