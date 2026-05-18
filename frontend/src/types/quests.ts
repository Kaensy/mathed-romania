// ─── Quest types ──────────────────────────────────────────────────────────────
//
// Mirrors the Block 11 backend exactly:
//   - apps/progress/quests/service.py :: _serialize_assignment / _serialize_bar
//   - apps/progress/quests/service.py :: build_current_period_state
//   - claim_quest / claim_milestone return shapes
// Keys match the JSON the server emits (e.g. `slug`, not `quest_slug`).

export type QuestCadence = "daily" | "weekly";

export type QuestStatus = "active" | "completed" | "claimed" | "expired";

/** Phase-2 event slugs a quest's progress is driven by (catalog goal_type). */
export type QuestGoalType =
  | "login"
  | "daily_test_started"
  | "daily_test_completed"
  | "exercise_completed"
  | "test_passed"
  | "daily_quest_claimed";

/** One catalog quest materialised for the student in the current period. */
export interface QuestAssignment {
  id: number;
  slug: string;
  cadence: QuestCadence;
  /** null only if the catalog entry was removed under an in-flight row. */
  goal_type: QuestGoalType | null;
  title: string;
  description: string;
  progress: number;
  target: number;
  status: QuestStatus;
  /** null if the catalog entry is missing. */
  xp_reward: number | null;
  /** Points toward the daily bar; null for weekly quests. */
  point_value: number | null;
  period_key: string;
  completed_at: string | null; // ISO 8601
  claimed_at: string | null; // ISO 8601
}

/** A daily points-bar milestone rung. Server-defined — never hardcode. */
export interface MilestoneRung {
  threshold: number;
  xp_reward: number;
  claimed: boolean;
}

/** The daily points bar (DailyChallengeProgress + catalog rungs). */
export interface DailyChallengeBar {
  date: string; // ISO date (Europe/Bucharest)
  points: number;
  claimed_thresholds: number[];
  milestones: MilestoneRung[];
}

/** Envelope for GET /quests/ and POST /quests/sync/. */
export interface QuestState {
  daily_period_key: string;
  weekly_period_key: string;
  daily: QuestAssignment[];
  weekly: QuestAssignment[];
  bar: DailyChallengeBar;
}

/** POST /quests/<id>/claim/ — `bar` is non-null only for a daily claim. */
export interface QuestClaimResponse {
  assignment: QuestAssignment;
  xp_gained: number;
  bar: DailyChallengeBar | null;
}

/** POST /quests/milestone/<threshold>/claim/. */
export interface MilestoneClaimResponse {
  bar: DailyChallengeBar;
  xp_gained: number;
}

/** Body of a rejected claim (4xx) — `{ "error": "<Romanian message>" }`. */
export interface QuestErrorResponse {
  error: string;
}
