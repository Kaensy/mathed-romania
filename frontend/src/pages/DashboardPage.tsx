import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate, Link } from "react-router-dom";
import { BookOpen, PenLine, BarChart3 } from "lucide-react";
import api from "@/api/client";
import type { DashboardStats } from "@/types/progress";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    api
      .get<DashboardStats>("/progress/dashboard/")
      .then((res) => setStats(res.data))
      .catch(() => {/* non-fatal — show placeholders */})
      .finally(() => setLoadingStats(false));
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  const completionPct = stats
    ? Math.round((stats.completed_lessons / (stats.total_lessons || 1)) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-bold text-indigo-900">MathEd Romania</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user.first_name} {user.last_name}
            </span>
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
        <h2 className="text-2xl font-bold text-gray-900">
          Bun venit, {user.first_name}!
        </h2>
        <p className="mt-1 text-gray-500">
          {user.user_type === "student"
            ? "Continuă să înveți matematică."
            : "Urmărește progresul elevilor tăi."}
        </p>

        {/* Stats row */}
        {user.user_type === "student" && (
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
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
              sub={stats?.perfect_batches ? `${stats.perfect_batches} sesiuni perfecte` : undefined}

            />
            <StatCard
              loading={loadingStats}
              icon={<BarChart3 className="w-5 h-5 text-amber-500" />}
              label="În progres"
              value={stats ? String(stats.in_progress_lessons) : "—"}
              sub="lecții deschise"
            />
          </div>
        )}

        {/* Navigation cards */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            to="/grade/5"
            className="rounded-xl border bg-white p-6 hover:border-indigo-300 hover:shadow-sm transition-all block"
          >
            <div className="mb-3 text-2xl">📚</div>
            <h3 className="font-semibold text-gray-900">Lecții</h3>
            <p className="mt-1 text-sm text-gray-500">Clasa a V-a — Matematică</p>
          </Link>
          <Link to="/exercises" className="rounded-xl border bg-white p-6 hover:border-indigo-300 hover:shadow-sm transition-all block">
  <div className="mb-3 text-2xl">✏️</div>
  <h3 className="font-semibold text-gray-900">Exerciții</h3>
  <p className="mt-1 text-sm text-gray-500">Toate exercițiile tale</p>
</Link>
          <Link to="/tests" className="rounded-xl border bg-white p-6 hover:border-indigo-300 hover:shadow-sm transition-all block">
  <div className="mb-3 text-2xl">🏆</div>
  <h3 className="font-semibold text-gray-900">Teste</h3>
  <p className="mt-1 text-sm text-gray-500">Evaluările lecțiilor</p>
</Link>
        </div>

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
    </div>
  );
}

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
