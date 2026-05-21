import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate, Link } from "react-router-dom";
import { Flame, CheckCircle2, Target } from "lucide-react";
import api from "@/api/client";
import type { DashboardStats, WeakCategoriesResponse, WeakCategory } from "@/types/progress";
import type { DailyTestResponse } from "@/types/daily";
import { useCosmetics } from "@/hooks/useCosmetics";
import { useStreak } from "@/hooks/useStreak";
import StreakBadge from "@/components/streak/StreakBadge";
import StreakModal from "@/components/streak/StreakModal";
import HomeBrand from "@/components/HomeBrand";
import AvatarPreview, {
  buildPreviewSelection,
} from "@/components/cosmetics/AvatarPreview";
import PetPanel from "@/components/pets/PetPanel";
import QuestSummaryCard from "@/components/quests/QuestSummaryCard";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weakCategories, setWeakCategories] = useState<WeakCategory[] | null>(null);
  const [streakModalOpen, setStreakModalOpen] = useState(false);
  const { streak, loading: loadingStreak } = useStreak();
  const { state: cosmeticState } = useCosmetics();

  // Resolve the equipped frame + avatar so the header circle shows the
  // student's current combo. Reads off the shared CosmeticsContext, so
  // equipping in the wardrobe modal updates this header in the same
  // render tick without a page reload.
  const headerAvatar = useMemo(() => {
    if (!cosmeticState) return null;
    return buildPreviewSelection(
      cosmeticState.cosmetics,
      cosmeticState.equipped,
      cosmeticState.avatar_source,
      cosmeticState.avatar_image_url,
    );
  }, [cosmeticState]);

  useEffect(() => {
    api
      .get<DashboardStats>("/progress/dashboard/")
      .then((res) => setStats(res.data))
      .catch(() => {/* non-fatal — show placeholders */});
  }, []);

  useEffect(() => {
    if (user?.user_type !== "student") return;
    api
      .get<WeakCategoriesResponse>("/progress/weak-categories/?limit=3")
      .then((res) => setWeakCategories(res.data.categories))
      .catch(() => {/* non-fatal — hide widget */});
  }, [user?.user_type]);

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <HomeBrand />
          <div className="flex items-center gap-4">
            <Link
              to="/glossary"
              className="text-sm text-gray-600 hover:text-indigo-600 transition-colors"
            >
              Glosar
            </Link>
            {user.user_type === "student" && !loadingStreak && streak && (
              <StreakBadge
                count={streak.current_streak}
                onClick={() => setStreakModalOpen(true)}
              />
            )}
            <Link
              to="/profile"
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600 transition-colors"
            >
              {user.user_type === "student" && (
                <AvatarPreview
                  size="sm"
                  avatarSource={headerAvatar?.avatarSource ?? null}
                  avatarImageUrl={headerAvatar?.avatarImageUrl ?? null}
                  presetAssetRef={headerAvatar?.presetAssetRef ?? null}
                  frameAssetRef={headerAvatar?.frameAssetRef ?? null}
                  initials={`${user.first_name.charAt(0)}${user.last_name.charAt(0)}`}
                />
              )}
              <span>
                {user.first_name} {user.last_name}
              </span>
            </Link>
            <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
              {user.user_type === "student" ? "Elev" : user.user_type === "teacher" ? "Profesor" : "Admin"}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 transition hover:bg-gray-50"
            >
              Deconectare
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        {/* 1. Top strip — greeting (left) + aggregate stats (right) */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-xl font-bold text-gray-900">
            Bună, {user.first_name}!
          </h2>

          {user.user_type === "student" && (
            <div className="flex items-center gap-5 rounded-xl border bg-white px-5 py-3">
              <div>
                <p className="text-xs text-gray-500">Lecții finalizate</p>
                <p className="text-lg font-bold text-gray-900">
                  {stats ? `${stats.completed_lessons}/${stats.total_lessons}` : "—"}
                </p>
              </div>
              <div className="h-9 w-px bg-gray-200" />
              <div>
                <p className="text-xs text-gray-500">Exerciții rezolvate</p>
                <p className="text-lg font-bold text-gray-900">
                  {stats ? String(stats.exercises_attempted) : "—"}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 2. Big curriculum nav row — the headliner */}
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <Link
            to="/grade/5"
            className="rounded-2xl border bg-white p-8 hover:border-indigo-300 hover:shadow-md transition-all block"
          >
            <div className="mb-4 text-4xl">📚</div>
            <h3 className="text-lg font-bold text-gray-900">Lecții</h3>
            <p className="mt-1 text-sm text-gray-500">Clasa a V-a — Matematică</p>
          </Link>
          <Link
            to="/exercises"
            className="rounded-2xl border bg-white p-8 hover:border-indigo-300 hover:shadow-md transition-all block"
          >
            <div className="mb-4 text-4xl">✏️</div>
            <h3 className="text-lg font-bold text-gray-900">Exerciții</h3>
            <p className="mt-1 text-sm text-gray-500">Toate exercițiile tale</p>
          </Link>
          <div className="flex flex-col">
            <Link
              to="/tests"
              className="rounded-2xl border bg-white p-8 hover:border-indigo-300 hover:shadow-md transition-all block"
            >
              <div className="mb-4 text-4xl">🏆</div>
              <h3 className="text-lg font-bold text-gray-900">Teste</h3>
              <p className="mt-1 text-sm text-gray-500">Evaluările lecțiilor</p>
            </Link>
            {user.user_type === "student" && (
              <Link
                to="/test-history"
                className="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-700 hover:underline self-end"
              >
                Vezi istoricul →
              </Link>
            )}
          </div>
        </div>

        {/* 3. Pet panel — unchanged widget */}
        {user.user_type === "student" && <PetPanel />}

        {/* 4. Daily test + Quests — two columns desktop, stacked < md */}
        {user.user_type === "student" && (
          <div className="grid gap-4 md:grid-cols-2">
            <DailyTestCard />
            <QuestSummaryCard />
          </div>
        )}

        {/* 5. Recomandat pentru tine — weak categories */}
        {user.user_type === "student" && weakCategories && weakCategories.length > 0 && (
          <section className="mt-8">
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-5 h-5 text-indigo-500" />
              <h3 className="text-base font-semibold text-gray-700">
                Recomandat pentru tine
              </h3>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {weakCategories.map((cat) => (
                <WeakCategoryCard key={`${cat.topic_id}-${cat.category}`} cat={cat} />
              ))}
            </div>
          </section>
        )}

        {/* Per-unit progress — only show if we have data and user is student */}
        {user.user_type === "student" && stats && stats.units.length > 0 && (
          <div className="mt-8">
            <h3 className="text-base font-semibold text-gray-700 mb-3">Progres pe unități</h3>
            <div className="space-y-3">
              {stats.units.filter(u => u.total_lessons > 0).map((unit) => {
                const pct = Math.round((unit.completed_lessons / unit.total_lessons) * 100);
                return (
                  <div key={unit.unit_id} className="bg-white rounded-xl border border-gray-200 px-5 py-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{unit.unit_title}</span>
                      <span className="text-xs text-gray-400">
                        {unit.completed_lessons}/{unit.total_lessons} lecții
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-2 bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>

      {streakModalOpen && streak && (
        <StreakModal streak={streak} onClose={() => setStreakModalOpen(false)} />
      )}
    </div>
  );
}

function DailyTestCard() {
  const [state, setState] = useState<DailyTestResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<DailyTestResponse>("/progress/daily/")
      .then((res) => setState(res.data))
      .catch(() => {/* non-fatal — hide card */})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mt-8 rounded-xl border bg-white p-5 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gray-200 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-32" />
            <div className="h-3 bg-gray-100 rounded w-48" />
          </div>
        </div>
      </div>
    );
  }

  if (!state) return null;

  if (state.status === "no_exercises") {
    return (
      <div className="mt-8 rounded-xl border bg-white p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
          <Flame className="w-6 h-6 text-gray-400" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-700">Testul Zilei</h3>
          <p className="text-sm text-gray-500 mt-0.5">
            Rezolvă exerciții pentru a debloca testul zilei.
          </p>
        </div>
      </div>
    );
  }

  if (state.status === "available") {
    return (
      <Link
        to="/daily"
        className="mt-8 block rounded-xl border-2 border-orange-200 bg-gradient-to-br
          from-orange-50 to-white p-5 hover:border-orange-400 hover:shadow-sm transition-all"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
            <Flame className="w-6 h-6 text-orange-500" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900">Testul Zilei</h3>
            <p className="text-sm text-gray-600 mt-0.5">
              {state.exercise_count} {state.exercise_count === 1 ? "exercițiu" : "exerciții"} te așteaptă astăzi.
            </p>
          </div>
          <span className="shrink-0 px-4 py-2 rounded-lg bg-orange-500 text-white text-sm font-semibold">
            Începe
          </span>
        </div>
      </Link>
    );
  }

  if (state.status === "in_progress") {
    const cta = state.completed_count === 0 ? "Începe" : "Continuă";
    const pct = state.total_count > 0
      ? (state.completed_count / state.total_count) * 100
      : 0;
    return (
      <Link
        to="/daily"
        className="mt-8 block rounded-xl border-2 border-indigo-200 bg-gradient-to-br
          from-indigo-50 to-white p-5 hover:border-indigo-400 hover:shadow-sm transition-all"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
            <Flame className="w-6 h-6 text-orange-500" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900">Testul Zilei</h3>
            <p className="text-sm text-gray-600 mt-0.5">
              {state.completed_count}/{state.total_count} completate
            </p>
            <div className="h-1.5 mt-2 bg-white/80 rounded-full overflow-hidden">
              <div
                className="h-1.5 bg-indigo-500 rounded-full transition-all duration-500"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
          <span className="shrink-0 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold">
            {cta}
          </span>
        </div>
      </Link>
    );
  }

  // completed
  const timeLabel = formatShortTime(state.completed_at);
  return (
    <div className="mt-8 rounded-xl border border-green-200 bg-green-50/60 p-5 flex items-center gap-4">
      <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center shrink-0">
        <CheckCircle2 className="w-6 h-6 text-green-600" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900">Testul Zilei</h3>
        <p className="text-sm text-green-700 mt-0.5">
          Completat ✓
          {timeLabel && <span className="text-gray-400"> • la {timeLabel}</span>}
        </p>
      </div>
      <Link
        to="/daily"
        className="shrink-0 text-sm text-indigo-600 hover:underline"
      >
        Vezi rezultatele
      </Link>
    </div>
  );
}

function formatShortTime(iso: string): string | null {
  try {
    return new Date(iso).toLocaleTimeString("ro-RO", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return null;
  }
}

function WeakCategoryCard({ cat }: { cat: WeakCategory }) {
  const pct = Math.round(cat.accuracy * 100);
  const barColor =
    cat.accuracy < 0.4
      ? "bg-red-400"
      : cat.accuracy < 0.7
      ? "bg-amber-400"
      : "bg-emerald-400";

  return (
    <div className="rounded-xl border bg-white p-4 flex flex-col gap-3">
      <div className="min-w-0">
        <p className="font-semibold text-gray-900 truncate" title={cat.category_label}>
          {cat.category_label}
        </p>
        <p className="text-xs text-gray-500 truncate mt-0.5" title={cat.topic_title}>
          {cat.topic_title}
        </p>
      </div>
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Acuratețe</span>
          <span className="text-xs font-medium text-gray-600">{pct}%</span>
        </div>
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      <Link
        to={`/topic/${cat.topic_id}/practice`}
        state={{ category: cat.category, from: "dashboard" }}
        className="mt-auto text-center text-sm font-medium text-indigo-600 hover:text-indigo-700 rounded-lg border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 transition-colors px-3 py-1.5"
      >
        Exersează
      </Link>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// FILE 2: Add to LessonViewer.tsx — insert this useEffect after the existing
// lesson-fetch useEffect (around line 35 in your current file).
//
// Also add this import at the top of LessonViewer.tsx:
//   import api from "@/api/client";
// (it's likely already there)
// ─────────────────────────────────────────────────────────────────────────────

/*
  // Call open endpoint when lesson loads successfully
  useEffect(() => {
    if (!lessonId || !lesson) return;
    api
      .post(`/progress/lessons/${lessonId}/open/`)
      .catch(() => {}); // fire-and-forget, never block the UI
  }, [lessonId, lesson]);
*/


// ─────────────────────────────────────────────────────────────────────────────
// FILE 3: Add to App.tsx — import and route for PracticePage
//
// Add import:
//   import PracticePage from "@/pages/PracticePage";
//
// Add route inside AppRoutes() alongside the other protected routes:
//   <Route
//     path="/lesson/:lessonId/practice"
//     element={<ProtectedRoute><PracticePage /></ProtectedRoute>}
//   />
// ─────────────────────────────────────────────────────────────────────────────
