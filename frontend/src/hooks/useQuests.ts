import { useCallback, useEffect, useState } from "react";

import {
  claimMilestone as apiClaimMilestone,
  claimQuest as apiClaimQuest,
  syncQuests,
} from "@/api/quests";
import type {
  DailyChallengeBar,
  MilestoneClaimResponse,
  QuestAssignment,
  QuestClaimResponse,
  QuestState,
} from "@/types/quests";

/**
 * Quest data hook.
 *
 * On mount it calls `syncQuests` — the explicit POST that ensures the
 * current-period rows exist and returns the full state (the Block 2
 * sync-on-mount precedent; a GET would observe nothing on a fresh
 * period). The claim actions patch local state straight from the claim
 * response, so there is no follow-up refetch. XP toasts are emitted by
 * the shared client interceptor (Block 10 pipeline) — not here.
 */
export function useQuests() {
  const [state, setState] = useState<QuestState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setState(await syncQuests());
    } catch {
      setError("Nu am putut încărca misiunile.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const claimQuest = useCallback(
    async (assignmentId: number): Promise<QuestClaimResponse> => {
      const res = await apiClaimQuest(assignmentId);
      setState((prev) => {
        if (!prev) return prev;
        const patch = (list: QuestAssignment[]) =>
          list.map((q) => (q.id === res.assignment.id ? res.assignment : q));
        return {
          ...prev,
          daily: patch(prev.daily),
          weekly: patch(prev.weekly),
          // bar is non-null only for a daily claim (point_value accrued).
          bar: res.bar ?? prev.bar,
        };
      });
      return res;
    },
    [],
  );

  const claimMilestone = useCallback(
    async (threshold: number): Promise<MilestoneClaimResponse> => {
      const res = await apiClaimMilestone(threshold);
      setState((prev) => (prev ? { ...prev, bar: res.bar } : prev));
      return res;
    },
    [],
  );

  const daily: QuestAssignment[] = state?.daily ?? [];
  const weekly: QuestAssignment[] = state?.weekly ?? [];
  const bar: DailyChallengeBar | null = state?.bar ?? null;

  return {
    daily,
    weekly,
    bar,
    loading,
    error,
    claimQuest,
    claimMilestone,
    refetch: load,
  };
}
