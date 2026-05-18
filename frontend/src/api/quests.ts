import api from "@/api/client";
import type {
  MilestoneClaimResponse,
  QuestClaimResponse,
  QuestState,
} from "@/types/quests";

/**
 * POST /api/v1/progress/quests/sync/ — idempotently ensure the
 * student's current-period quest rows + today's points bar, then
 * return the full current-period state. The explicit write that the
 * useQuests mount relies on (sync-on-mount precedent).
 */
export async function syncQuests(): Promise<QuestState> {
  const res = await api.post<QuestState>("/progress/quests/sync/");
  return res.data;
}

/**
 * GET /api/v1/progress/quests/ — read-only current-period state.
 * Never creates rows; syncQuests is the only writer.
 */
export async function getQuests(): Promise<QuestState> {
  const res = await api.get<QuestState>("/progress/quests/");
  return res.data;
}

/**
 * POST /api/v1/progress/quests/<assignmentId>/claim/ — claim a
 * completed quest. `bar` is non-null for a daily claim (its
 * point_value accrued to today's bar). XP toast fires automatically
 * via the shared client interceptor (Block 10 pipeline).
 */
export async function claimQuest(
  assignmentId: number,
): Promise<QuestClaimResponse> {
  const res = await api.post<QuestClaimResponse>(
    `/progress/quests/${assignmentId}/claim/`,
  );
  return res.data;
}

/**
 * POST /api/v1/progress/quests/milestone/<threshold>/claim/ — claim a
 * daily points-bar milestone rung.
 */
export async function claimMilestone(
  threshold: number,
): Promise<MilestoneClaimResponse> {
  const res = await api.post<MilestoneClaimResponse>(
    `/progress/quests/milestone/${threshold}/claim/`,
  );
  return res.data;
}
