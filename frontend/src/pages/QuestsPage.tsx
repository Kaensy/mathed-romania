/**
 * QuestsPage — the /quests tabbed shell.
 *
 * Route: /quests (student-only)
 *
 * Tabs: Zilnice (daily) and Săptămânale (weekly) are functional now.
 * The tab set is config-driven (TABS) so a third "Istoric" tab drops
 * in for Phase 3 with no shell rework. Everything is driven by the
 * useQuests hook; loading / error / empty are all handled. XP toasts
 * fire globally via the client interceptor (Block 10 pipeline); only
 * claim *errors* are surfaced here (inline, per spec).
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ListChecks } from "lucide-react";

import MilestoneBar from "@/components/quests/MilestoneBar";
import QuestCard from "@/components/quests/QuestCard";
import { useBonusCelebration } from "@/contexts/BonusCelebrationContext";
import { useQuests } from "@/hooks/useQuests";

type TabId = "daily" | "weekly";

const TABS: { id: TabId; label: string }[] = [
  { id: "daily", label: "Zilnice" },
  { id: "weekly", label: "Săptămânale" },
  // Phase 3: { id: "history", label: "Istoric" }
];

function extractError(err: unknown, fallback: string): string {
  const e = err as { response?: { data?: { error?: string } } };
  return e?.response?.data?.error ?? fallback;
}

export default function QuestsPage() {
  const navigate = useNavigate();
  const { daily, weekly, bar, loading, error, claimQuest, claimMilestone, refetch } =
    useQuests();
  const { notifyBonus } = useBonusCelebration();

  const [activeTab, setActiveTab] = useState<TabId>("daily");

  const [claimingQuestId, setClaimingQuestId] = useState<number | null>(null);
  const [questError, setQuestError] = useState<{ id: number; message: string } | null>(
    null,
  );
  const [claimingThreshold, setClaimingThreshold] = useState<number | null>(null);
  const [milestoneError, setMilestoneError] = useState<string | null>(null);

  const handleClaimQuest = async (id: number) => {
    setQuestError(null);
    setClaimingQuestId(id);
    try {
      await claimQuest(id);
    } catch (err) {
      setQuestError({
        id,
        message: extractError(err, "Nu am putut revendica misiunea."),
      });
    } finally {
      setClaimingQuestId(null);
    }
  };

  const handleClaimMilestone = async (threshold: number) => {
    setMilestoneError(null);
    setClaimingThreshold(threshold);
    // The finale rung (max threshold — 100 in the catalog). The sweep
    // means a single claim can newly complete it; detect by comparing
    // claimed_thresholds before vs after. Only the finale celebrates.
    const finale = bar
      ? bar.milestones.reduce((m, r) => Math.max(m, r.threshold), 0)
      : 100;
    const had100 = bar?.claimed_thresholds.includes(finale) ?? false;
    try {
      const res = await claimMilestone(threshold);
      const has100 = res.bar.claimed_thresholds.includes(finale);
      if (!had100 && has100) notifyBonus();
    } catch (err) {
      setMilestoneError(extractError(err, "Nu am putut revendica recompensa."));
    } finally {
      setClaimingThreshold(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sticky shell: top bar + tab strip */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <div className="flex-1 text-center flex items-center justify-center gap-2">
            <ListChecks className="w-4 h-4 text-indigo-500" />
            <span className="text-sm font-medium text-gray-700">Misiuni</span>
          </div>
          <div className="w-14" />
        </div>
        <div className="max-w-2xl mx-auto px-4 flex">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab.id
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        {loading && <QuestsSkeleton />}

        {!loading && error && (
          <div className="text-center py-16">
            <p className="text-red-500 font-medium">{error}</p>
            <button
              onClick={refetch}
              className="mt-4 text-sm text-indigo-600 hover:underline"
            >
              Reîncearcă
            </button>
          </div>
        )}

        {!loading && !error && activeTab === "daily" && (
          <div className="space-y-4">
            {bar && (
              <MilestoneBar
                bar={bar}
                onClaim={handleClaimMilestone}
                claimingThreshold={claimingThreshold}
                errorMessage={milestoneError}
              />
            )}
            {daily.length === 0 ? (
              <EmptyState message="Nicio misiune zilnică momentan. Revino mai târziu." />
            ) : (
              daily.map((q) => (
                <QuestCard
                  key={q.id}
                  quest={q}
                  onClaim={handleClaimQuest}
                  claiming={claimingQuestId === q.id}
                  errorMessage={
                    questError?.id === q.id ? questError.message : null
                  }
                />
              ))
            )}
          </div>
        )}

        {!loading && !error && activeTab === "weekly" && (
          <div className="space-y-4">
            {weekly.length === 0 ? (
              <EmptyState message="Nicio misiune săptămânală momentan. Revino mai târziu." />
            ) : (
              weekly.map((q) => (
                <QuestCard
                  key={q.id}
                  quest={q}
                  onClaim={handleClaimQuest}
                  claiming={claimingQuestId === q.id}
                  errorMessage={
                    questError?.id === q.id ? questError.message : null
                  }
                />
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function EmptyState({ message }: { message: string }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-10 text-center">
      <p className="text-gray-500">{message}</p>
    </div>
  );
}

function QuestsSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="bg-white rounded-2xl border border-gray-200 p-5 space-y-4">
        <div className="h-5 bg-gray-200 rounded w-1/3" />
        <div className="h-2 bg-gray-200 rounded-full" />
        <div className="h-16" />
      </div>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="bg-white rounded-2xl border border-gray-200 p-5 space-y-4"
        >
          <div className="h-5 bg-gray-200 rounded w-1/2" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-2 bg-gray-200 rounded-full" />
        </div>
      ))}
    </div>
  );
}
