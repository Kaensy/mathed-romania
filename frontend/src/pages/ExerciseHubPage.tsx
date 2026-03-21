/**
 * ExerciseHubPage — shows all exercise categories for a lesson,
 * each with three difficulty tiers (Easy / Medium / Hard).
 *
 * Route: /lesson/:lessonId/exercises
 *
 * Tier unlock rules (mirrored from backend CategoryProgress):
 *   Easy   — always available
 *   Medium — unlocked after Easy is cleared
 *   Hard   — unlocked after Easy is cleared
 *   Completing Medium OR Hard marks the category as "completed"
 *   Completing Hard also earns a bonus reward (shown as ⭐)
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link, useLocation } from "react-router-dom";
import { ArrowLeft, Lock, Star, CheckCircle, ChevronRight } from "lucide-react";
import api from "@/api/client";
import type { CategoryInfo, Difficulty, LessonCategoriesResponse, TierState } from "@/types/progress";
import { CATEGORY_LABELS } from "@/constants/categoryLabels";

// ─── Tier config ──────────────────────────────────────────────────────────────

const TIER_CONFIG: Record<Difficulty, { label: string; color: string; ring: string; bg: string }> = {
  easy:   { label: "Ușor",  color: "text-emerald-700", ring: "ring-emerald-400", bg: "bg-emerald-50" },
  medium: { label: "Mediu", color: "text-amber-700",   ring: "ring-amber-400",   bg: "bg-amber-50"   },
  hard:   { label: "Greu",  color: "text-rose-700",    ring: "ring-rose-400",    bg: "bg-rose-50"    },
};

const TIERS: Difficulty[] = ["easy", "medium", "hard"];

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ExerciseHubPage() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<LessonCategoriesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const location = useLocation();
  const fromOverview = location.state?.from === "exercises-overview";

  useEffect(() => {
    if (!lessonId) return;
    api
      .get<LessonCategoriesResponse>(`/progress/lessons/${lessonId}/categories/`)
      .then((res) => setData(res.data))
      .catch(() => setError("Nu am putut încărca exercițiile."))
      .finally(() => setLoading(false));
  }, [lessonId]);

  if (loading) return <HubSkeleton />;

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 font-medium">{error}</p>
          <button onClick={() => navigate(-1)} className="mt-4 text-indigo-600 hover:underline text-sm">
            Înapoi
          </button>
        </div>
      </div>
    );
  }

  const completedCategories = data.categories.filter(
    (c) => c.tiers.medium.cleared || c.tiers.hard.cleared,
  ).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-4">
          {fromOverview ? (
  <Link to="/exercises" className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors">
    <ArrowLeft className="w-4 h-4" />
    <span>Înapoi la Exerciții</span>
  </Link>
) : (
  <Link to={`/lesson/${lessonId}`} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors">
    <ArrowLeft className="w-4 h-4" />
    <span>Înapoi la lecție</span>
  </Link>
)}
        </div>
      </div>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Exerciții</h1>
        <p className="text-gray-500 text-sm mb-2">{data.lesson_title}</p>

        {/* Summary bar */}
        <div className="flex items-center gap-4 mb-8 text-sm text-gray-500">
          <span>
            <span className="font-semibold text-gray-800">{completedCategories}</span>
            {" "}/ {data.categories.length} categorii completate
          </span>
          {data.categories.some((c) => c.tiers.hard.cleared) && (
            <span className="flex items-center gap-1 text-amber-600 font-medium">
              <Star className="w-3.5 h-3.5 fill-amber-400" />
              Bonus obținut
            </span>
          )}
        </div>

        {data.categories.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p>Nu există exerciții disponibile pentru această lecție.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {data.categories.map((cat) => (
              <CategoryCard key={cat.category} cat={cat} lessonId={lessonId!} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Category card ────────────────────────────────────────────────────────────

function CategoryCard({ cat, lessonId }: { cat: CategoryInfo; lessonId: string }) {
  const displayLabel = CATEGORY_LABELS[cat.category] ?? cat.label;
  const isCompleted = cat.tiers.medium.cleared || cat.tiers.hard.cleared;
  const hasBonusCleared = cat.tiers.hard.cleared;

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Category header */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              {displayLabel}
              {isCompleted && (
                <CheckCircle className="w-4 h-4 text-emerald-500" />
              )}
              {hasBonusCleared && (
                <Star className="w-4 h-4 text-amber-500 fill-amber-400" />
              )}
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              {cat.exercise_count} exerciții
              {cat.exercises_attempted > 0 && (
                <> · {cat.exercises_attempted} încercări · {cat.perfect_batches} sesiuni perfecte</>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Tier buttons */}
      <div className="grid grid-cols-3 divide-x divide-gray-100">
        {TIERS.map((tier) => (
          <TierButton
            key={tier}
            tier={tier}
            state={cat.tiers[tier]}
            lessonId={lessonId}
            category={cat.category}
            isHardBonus={tier === "hard"}
          />
        ))}
      </div>
    </div>
  );
}

// ─── Tier button ──────────────────────────────────────────────────────────────

interface TierButtonProps {
  tier: Difficulty;
  state: TierState;
  lessonId: string;
  category: string;
  isHardBonus: boolean;
}

function TierButton({ tier, state, lessonId, category, isHardBonus }: TierButtonProps) {
  const navigate = useNavigate();
  const config = TIER_CONFIG[tier];
  const isLocked = !state.available;
  const isCleared = state.cleared;

  const handleClick = () => {
    if (isLocked) return;
    const params = new URLSearchParams({ category });
    params.set("difficulty", tier);
    navigate(`/lesson/${lessonId}/practice?${params}`);
  };

  if (isLocked) {
    return (
      <div className="flex flex-col items-center justify-center py-5 px-3 text-center opacity-40 cursor-not-allowed select-none">
        <Lock className="w-4 h-4 text-gray-400 mb-1.5" />
        <span className="text-xs font-medium text-gray-500">{config.label}</span>
        {isHardBonus && (
          <span className="text-xs text-amber-500 mt-0.5 flex items-center gap-0.5">
            <Star className="w-3 h-3 fill-amber-400" /> Bonus
          </span>
        )}
      </div>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={`group flex flex-col items-center justify-center py-5 px-3 text-center transition-all hover:${config.bg} focus:outline-none focus-visible:ring-2 ${config.ring}`}
    >
      {isCleared ? (
        <CheckCircle className={`w-5 h-5 mb-1.5 ${config.color}`} />
      ) : (
        <ChevronRight className={`w-5 h-5 mb-1.5 ${config.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
      )}
      <span className={`text-xs font-semibold ${config.color}`}>{config.label}</span>
      {isHardBonus && (
        <span className={`text-xs mt-0.5 flex items-center gap-0.5 ${isCleared ? "text-amber-500" : "text-gray-400"}`}>
          <Star className={`w-3 h-3 ${isCleared ? "fill-amber-400" : ""}`} /> Bonus
        </span>
      )}
      {isCleared && (
        <span className={`text-xs mt-1 ${config.color} opacity-60`}>Completat</span>
      )}
    </button>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function HubSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 h-14" />
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded-lg animate-pulse" />
        <div className="h-4 w-32 bg-gray-100 rounded animate-pulse" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100">
              <div className="h-5 w-40 bg-gray-200 rounded animate-pulse" />
              <div className="h-3 w-24 bg-gray-100 rounded animate-pulse mt-2" />
            </div>
            <div className="grid grid-cols-3 divide-x divide-gray-100">
              {[1, 2, 3].map((j) => (
                <div key={j} className="py-5 flex flex-col items-center gap-2">
                  <div className="h-5 w-5 bg-gray-200 rounded-full animate-pulse" />
                  <div className="h-3 w-10 bg-gray-100 rounded animate-pulse" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
