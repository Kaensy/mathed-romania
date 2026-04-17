import { useEffect, useState, useCallback } from "react";
import api from "@/api/client";
import type { StreakData } from "@/types/progress";

export function useStreak() {
  const [streak, setStreak] = useState<StreakData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStreak = useCallback(async () => {
    try {
      const res = await api.get<StreakData>("/progress/streak/");
      setStreak(res.data);
    } catch {
      // Non-fatal — streak display is supplementary
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStreak();
  }, [fetchStreak]);

  return { streak, loading, refetch: fetchStreak };
}
