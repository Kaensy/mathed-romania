// ─── Test session ─────────────────────────────────────────────────────────────

import type { ExerciseInstance } from "@/types/progress";

export interface TestStartResponse {
  attempt_id: number;
  exercises: ExerciseInstance[];
  answers: Record<string, AnswerRecord>;
  resumed: boolean;
}

export interface AnswerRecord {
  answer: string | string[];
  is_correct: boolean;
  exercise_id: number;
  weight: number;
  correct_answer?: string | null;
}

export interface TestAnswerResponse {
  received: boolean;
  index: number;
}

export interface TestFinishResponse {
  score: number;
  passed: boolean;
  pass_threshold: number;
  answers: Record<string, AnswerRecord>;
}

export interface TestResultResponse {
  score: number;
  passed: boolean;
  pass_threshold: number;
  finished_at: string;
  answers: Record<string, AnswerRecord>;
  exercise_instances: ExerciseInstance[];
}

export interface TestHistoryAttempt {
  attempt_id: number;
  test_id: number;
  test_scope: "topic" | "unit";
  test_title: string;
  score: number | null;
  passed: boolean | null;
  pass_threshold: number;
  started_at: string;
  finished_at: string;
  exercise_count: number;
}

export interface TestHistoryResponse {
  attempts: TestHistoryAttempt[];
}
