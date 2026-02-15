import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Simple top bar */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-bold text-primary-900">MathEd Romania</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user.first_name} {user.last_name}
            </span>
            <span className="rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-700">
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

      {/* Main content */}
      <main className="mx-auto max-w-5xl px-6 py-8">
        <h2 className="text-2xl font-bold text-gray-900">
          Bun venit, {user.first_name}!
        </h2>
        <p className="mt-2 text-gray-600">
          {user.user_type === "student"
            ? "Aici vei găsi lecțiile și exercițiile tale de matematică."
            : "Aici poți vedea progresul elevilor tăi."}
        </p>

        {/* Placeholder cards */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-xl border bg-white p-6">
            <div className="mb-3 text-2xl">📚</div>
            <h3 className="font-semibold text-gray-900">Lecții</h3>
            <p className="mt-1 text-sm text-gray-500">Disponibil în curând — Phase 3</p>
          </div>
          <div className="rounded-xl border bg-white p-6">
            <div className="mb-3 text-2xl">✏️</div>
            <h3 className="font-semibold text-gray-900">Exerciții</h3>
            <p className="mt-1 text-sm text-gray-500">Disponibil în curând — Phase 4</p>
          </div>
          <div className="rounded-xl border bg-white p-6">
            <div className="mb-3 text-2xl">📊</div>
            <h3 className="font-semibold text-gray-900">Progres</h3>
            <p className="mt-1 text-sm text-gray-500">Disponibil în curând — Phase 4</p>
          </div>
        </div>
      </main>
    </div>
  );
}
