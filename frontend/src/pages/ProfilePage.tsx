/**
 * ProfilePage — consolidated student progress view.
 *
 * Route: /profile
 *
 * Sections:
 *   1. Student info header (name, email, type badge, streak)
 *   2. Stats overview (2x2 grid)
 *   3. Weak categories list (up to 10)
 *   4. Future placeholder (badges, test history)
 */
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BookOpen,
  PenLine,
  BarChart3,
  CheckCircle2,
  Target,
  Sparkles,
} from "lucide-react";
import api from "@/api/client";
import { useAuth } from "@/hooks/useAuth";
import { useStreak } from "@/hooks/useStreak";
import StreakBadge from "@/components/streak/StreakBadge";
import StreakModal from "@/components/streak/StreakModal";
import type {
  DashboardStats,
  WeakCategoriesResponse,
  WeakCategory,
} from "@/types/progress";

export default function ProfilePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { streak, loading: loadingStreak } = useStreak();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [weakCategories, setWeakCategories] = useState<WeakCategory[] | null>(null);
  const [streakModalOpen, setStreakModalOpen] = useState(false);

  const isStudent = user?.user_type === "student";

  useEffect(() => {
    if (!isStudent) return;
    api
      .get<DashboardStats>("/progress/dashboard/")
      .then((res) => setStats(res.data))
      .catch(() => {/* non-fatal */})
      .finally(() => setLoadingStats(false));
  }, [isStudent]);

  useEffect(() => {
    if (!isStudent) return;
    api
      .get<WeakCategoriesResponse>("/progress/weak-categories/?limit=10")
      .then((res) => setWeakCategories(res.data.categories))
      .catch(() => setWeakCategories([]));
  }, [isStudent]);

  if (!user) return null;

  const completionPct = stats
    ? Math.round((stats.completed_lessons / (stats.total_lessons || 1)) * 100)
    : 0;

  const typeLabel =
    user.user_type === "student"
      ? "Elev"
      : user.user_type === "teacher"
      ? "Profesor"
      : "Admin";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto flex max-w-3xl items-center gap-4 px-6 py-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Înapoi</span>
          </button>
          <h1 className="text-base font-semibold text-gray-800">Profilul meu</h1>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8 space-y-8">
        {/* ── Section 1: Student info ───────────────────────────── */}
        <section className="rounded-2xl border bg-white p-6 flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
            <span className="text-indigo-700 font-bold text-lg">
              {user.first_name.charAt(0)}
              {user.last_name.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-lg font-bold text-gray-900">
                {user.first_name} {user.last_name}
              </h2>
              <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
                {typeLabel}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-0.5 truncate">{user.email}</p>
          </div>
          {isStudent && !loadingStreak && streak && (
            <StreakBadge
              count={streak.current_streak}
              onClick={() => setStreakModalOpen(true)}
            />
          )}
        </section>

        {/* ── Section 2: Stats overview ─────────────────────────── */}
        {isStudent && (
          <section>
            <h3 className="text-sm font-semibold text-gray-600 mb-3">Statistici</h3>
            <div className="grid gap-4 grid-cols-2">
              <StatCard
                loading={loadingStats}
                icon={<BookOpen className="w-5 h-5 text-indigo-500" />}
                label="Lecții finalizate"
                value={stats ? `${stats.completed_lessons} / ${stats.total_lessons}` : "—"}
                sub={stats ? `${completionPct}% completat` : undefined}
              />
              <StatCard
                loading={loadingStats}
                icon={<PenLine className="w-5 h-5 text-emerald-500" />}
                label="Exerciții rezolvate"
                value={stats ? String(stats.exercises_attempted) : "—"}
              />
              <StatCard
                loading={loadingStats}
                icon={<CheckCircle2 className="w-5 h-5 text-green-500" />}
                label="Sesiuni perfecte"
                value={stats ? String(stats.perfect_batches) : "—"}
              />
              <StatCard
                loading={loadingStats}
                icon={<BarChart3 className="w-5 h-5 text-amber-500" />}
                label="În progres"
                value={stats ? String(stats.in_progress_lessons) : "—"}
                sub="lecții deschise"
              />
            </div>
          </section>
        )}

        {/* ── Section 3: Weak categories ────────────────────────── */}
        {isStudent && (
          <section>
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-5 h-5 text-indigo-500" />
              <h3 className="text-sm font-semibold text-gray-600">
                Categorii de îmbunătățit
              </h3>
            </div>
            {weakCategories === null ? null : weakCategories.length === 0 ? (
              <div className="rounded-xl border border-dashed border-gray-200 bg-white px-5 py-8 text-center">
                <Sparkles className="w-6 h-6 text-indigo-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">
                  Nicio categorie slabă detectată. Continuă să exersezi!
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {weakCategories.map((cat) => (
                  <WeakCategoryRow key={`${cat.topic_id}-${cat.category}`} cat={cat} />
                ))}
              </div>
            )}
          </section>
        )}

        {/* Block 9: Badges grid will go here */}
      </main>

      {streakModalOpen && streak && (
        <StreakModal streak={streak} onClose={() => setStreakModalOpen(false)} />
      )}
    </div>
  );
}

// ─── Weak category row ────────────────────────────────────────────────────────

function WeakCategoryRow({ cat }: { cat: WeakCategory }) {
  const pct = Math.round(cat.accuracy * 100);
  const barColor =
    cat.accuracy < 0.4
      ? "bg-red-400"
      : cat.accuracy < 0.7
      ? "bg-amber-400"
      : "bg-emerald-400";

  return (
    <div className="rounded-xl border bg-white p-4 flex items-center gap-4">
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-gray-900 truncate" title={cat.category_label}>
          {cat.category_label}
        </p>
        <p className="text-xs text-gray-500 truncate mt-0.5" title={cat.topic_title}>
          {cat.topic_title}
        </p>
        <div className="mt-2 flex items-center gap-3">
          <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-1.5 rounded-full transition-all duration-500 ${barColor}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="text-xs font-medium text-gray-600 shrink-0">{pct}%</span>
        </div>
        <p className="text-xs text-gray-400 mt-1.5">
          {cat.total_attempts} încercări · {formatRelativeDate(cat.last_attempted_at)}
        </p>
      </div>
      <Link
        to={`/topic/${cat.topic_id}/practice`}
        state={{ category: cat.category, from: "profile" }}
        className="shrink-0 text-sm font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-1.5 transition-colors"
      >
        Exersează
      </Link>
    </div>
  );
}

// ─── Stat card ────────────────────────────────────────────────────────────────

function StatCard({
  loading,
  icon,
  label,
  value,
  sub,
}: {
  loading: boolean;
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-xl border bg-white p-5">
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      {loading ? (
        <div className="animate-pulse">
          <div className="h-7 bg-gray-200 rounded w-20 mb-1" />
          <div className="h-4 bg-gray-100 rounded w-28" />
        </div>
      ) : (
        <>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </>
      )}
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatRelativeDate(iso: string | null): string {
  if (!iso) return "niciodată";
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "niciodată";

  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfThen = new Date(then.getFullYear(), then.getMonth(), then.getDate());
  const diffDays = Math.round(
    (startOfToday.getTime() - startOfThen.getTime()) / (1000 * 60 * 60 * 24),
  );

  if (diffDays <= 0) return "astăzi";
  if (diffDays === 1) return "ieri";
  if (diffDays < 7) return `acum ${diffDays} zile`;
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return weeks === 1 ? "acum o săptămână" : `acum ${weeks} săptămâni`;
  }
  if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return months === 1 ? "acum o lună" : `acum ${months} luni`;
  }
  const years = Math.floor(diffDays / 365);
  return years === 1 ? "acum un an" : `acum ${years} ani`;
}
