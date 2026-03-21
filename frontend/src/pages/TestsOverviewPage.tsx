/**
 * TestsOverviewPage — global overview of all lesson tests.
 *
 * Route: /tests
 *
 * Lists every published lesson test ordered by lesson sequence, grouped
 * by unit. Shows pass status and best score, with a direct link to take
 * (or retry) the test.
 */
import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  Trophy,
  ChevronRight,
} from "lucide-react";
import api from "@/api/client";

// ─── Types ────────────────────────────────────────────────────────────────────

interface TestSummary {
  test_id: number;
  lesson_id: number;
  lesson_title: string;
  unit_id: number;
  unit_title: string;
  unit_order: number;
  lesson_order: number;
  pass_threshold: number;
  time_limit_minutes: number | null;
  attempts_count: number;
  passed: boolean | null;   // null = never attempted
  best_score: number | null;
}

interface TestsOverviewResponse {
  tests: TestSummary[];
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function TestsOverviewPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState<TestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<TestsOverviewResponse>("/progress/tests-overview/")
      .then((res) => setTests(res.data.tests))
      .catch(() => setError("Nu am putut încărca testele."))
      .finally(() => setLoading(false));
  }, []);

  const byUnit = groupByUnit(tests);
  const passedCount = tests.filter((t) => t.passed === true).length;
  const attemptedCount = tests.filter((t) => t.passed !== null).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center gap-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <span className="text-gray-300">|</span>
          <span className="text-sm font-medium text-gray-700">Teste</span>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Teste</h1>
        <p className="text-gray-500 text-sm mb-6">
          Evaluările pentru fiecare lecție
        </p>

        {/* Summary strip */}
        {!loading && !error && tests.length > 0 && (
          <div className="flex flex-wrap gap-6 mb-8 text-sm text-gray-500">
            <span>
              <span className="font-semibold text-gray-800">{passedCount}</span>
              {" / "}{tests.length} teste promovate
            </span>
            {attemptedCount > 0 && (
              <span>
                <span className="font-semibold text-gray-800">{attemptedCount}</span>
                {" "}susținute
              </span>
            )}
          </div>
        )}

        {loading && <SkeletonList />}

        {error && (
          <div className="text-center py-16 text-red-500">
            <p>{error}</p>
            <button onClick={() => navigate(-1)} className="mt-4 text-indigo-600 hover:underline text-sm">
              Înapoi
            </button>
          </div>
        )}

        {!loading && !error && tests.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <Trophy className="w-10 h-10 mx-auto mb-3 opacity-40" />
            <p>Nu există teste disponibile încă.</p>
          </div>
        )}

        {!loading && !error && byUnit.map(({ unitTitle, unitOrder, tests: unitTests }) => (
          <section key={unitOrder} className="mb-10">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              {unitTitle}
            </h2>
            <div className="space-y-3">
              {unitTests.map((test) => (
                <TestCard key={test.test_id} test={test} />
              ))}
            </div>
          </section>
        ))}
      </main>
    </div>
  );
}

// ─── Test card ────────────────────────────────────────────────────────────────

function TestCard({ test }: { test: TestSummary }) {
  const { status, color, icon } = resolveStatus(test);
  const romanianGrade =
    test.best_score !== null
      ? Math.round((test.best_score / 100) * 9 + 1)
      : null;

  return (
    <Link
      to={`/test/${test.test_id}`}
      className="flex items-center gap-4 bg-white rounded-2xl border border-gray-200 shadow-sm
        px-5 py-4 hover:border-indigo-300 hover:shadow-md transition-all"
    >
      {/* Status icon */}
      <div className={`shrink-0 ${color}`}>{icon}</div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 font-mono shrink-0">
            {test.lesson_order}.
          </span>
          <h3 className="font-semibold text-gray-900 text-sm truncate">
            {test.lesson_title}
          </h3>
        </div>

        <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-gray-400">
          <span className={`font-medium ${color}`}>{status}</span>
          {test.best_score !== null && (
            <span>
              {Math.round(test.best_score)}%
              {romanianGrade !== null && ` (nota ${romanianGrade})`}
            </span>
          )}
          {test.attempts_count > 0 && (
            <span>{test.attempts_count} {test.attempts_count === 1 ? "încercare" : "încercări"}</span>
          )}
          {test.time_limit_minutes && (
            <span className="flex items-center gap-0.5">
              <Clock className="w-3 h-3" />
              {test.time_limit_minutes} min
            </span>
          )}
          <span>Prag: {test.pass_threshold}%</span>
        </div>
      </div>

      <ChevronRight className="w-4 h-4 text-gray-300 shrink-0" />
    </Link>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function resolveStatus(test: TestSummary): {
  status: string;
  color: string;
  icon: React.ReactNode;
} {
  if (test.passed === null) {
    return {
      status: "Nesusținut",
      color: "text-gray-400",
      icon: <div className="w-6 h-6 rounded-full border-2 border-gray-200" />,
    };
  }
  if (test.passed) {
    return {
      status: "Promovat",
      color: "text-emerald-600",
      icon: <CheckCircle className="w-6 h-6 text-emerald-500" />,
    };
  }
  return {
    status: "Nepromovat",
    color: "text-red-500",
    icon: <XCircle className="w-6 h-6 text-red-400" />,
  };
}

function groupByUnit(tests: TestSummary[]) {
  const map = new Map<number, { unitTitle: string; unitOrder: number; tests: TestSummary[] }>();
  for (const test of tests) {
    if (!map.has(test.unit_id)) {
      map.set(test.unit_id, {
        unitTitle: test.unit_title,
        unitOrder: test.unit_order,
        tests: [],
      });
    }
    map.get(test.unit_id)!.tests.push(test);
  }
  return Array.from(map.values()).sort((a, b) => a.unitOrder - b.unitOrder);
}

function SkeletonList() {
  return (
    <div className="space-y-3 animate-pulse">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-white rounded-2xl border border-gray-200 px-5 py-4 flex items-center gap-4">
          <div className="w-6 h-6 rounded-full bg-gray-200 shrink-0" />
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-1.5" />
            <div className="h-3 bg-gray-100 rounded w-1/3" />
          </div>
        </div>
      ))}
    </div>
  );
}
